import yaml
from datetime import datetime
import pendulum
from unidecode import unidecode
from app.utils import DAY_MAP
from app.calendar import is_slot_available, create_event
from app.settings import settings
import logging
from app.configuration import settings
from typing import List, Dict, Optional

logging.basicConfig(level=settings.LOG_LEVEL)
logger = logging.getLogger(__name__)


class Service:
    """
    Represents a service that can be scheduled with professionals.
    Contains details about the service and methods to handle scheduling.
    """
    def __init__(self, data: Dict) -> None:
        # Initialize service attributes from input data dictionary
        self.name = data["name"]
        self.price = data.get("price")
        self.duration = data.get("duration")
        self.description = data.get("description")
        self.professionals = data.get("professionals", [])

    def get_name(self) -> str:
        # Return the name of the service
        return self.name

    def get_price(self) -> Optional[float]:
        # Return the price of the service
        return self.price

    def get_duration(self) -> Optional[int]:
        # Return the duration of the service in minutes
        return self.duration

    def get_description(self) -> Optional[str]:
        # Return the description of the service
        return self.description

    def get_professionals(self) -> List[Dict]:
        # Return the list of professionals associated with the service
        return self.professionals

    def get_available_professionals(self, target_day: str, target_time: str) -> List[str]:
        """
        Returns a list of professional names available at the given day and time.
        Uses _validate_slot to ensure the slot is actually available.
        Accepts target_day as a date string (YYYY-MM-DD) or day name in Portuguese.
        """
        logger.debug(f"Checking available professionals for {target_day} at {target_time}")
        try:
            normalized_time = datetime.strptime(target_time.strip(), "%H:%M").strftime("%H:%M")
        except ValueError:
            return []

        # Detect if target_day is a date (e.g., 2025-07-17)
        try:
            date_obj = pendulum.parse(target_day.strip())
            day_key = date_obj.format("dddd", locale="pt").lower()
        except Exception:
            day_key = target_day.strip().lower()

        available = []

        for prof in self.professionals:
            for availability in prof.get("availability", []):
                if availability["day"].lower() == day_key:
                    for slot in availability.get("slots", []):
                        start_str, _ = slot.split("-")
                        try:
                            normalized_start = datetime.strptime(start_str.strip(), "%H:%M").strftime("%H:%M")
                        except ValueError:
                            continue
                        if normalized_start == normalized_time and self._validate_slot(day_key, normalized_time):
                            available.append(prof["name"])
                            break
        logger.debug(f"Available professionals at {target_day} {target_time}: {available}")
        return available

    def find_professionals_for_slot(self, day: str, time: str) -> List[str]:
        # Wrapper method to find professionals available for a specific day and time slot
        return self.get_available_professionals(day, time)

    def get_available_slots(self) -> List[Dict[str, str]]:
        """
        Aggregates and returns all available slots for all professionals of the service.
        Each slot includes professional name, day, and time slot string.
        """
        logger.debug(f"Getting available slots for service {self.name}")
        slots = []
        duration = self.get_duration()
        for prof in self.professionals:
            slots.extend(self.get_slots_for_professional(prof["name"]))
        return slots

    def get_slots_for_professional(self, professional_name: str) -> List[Dict[str, str]]:
        """
        Returns all available time slots for a given professional.
        Slots are generated based on professional's availability and service duration.
        """
        slots = []
        for prof in self.professionals:
            if prof["name"].lower() == professional_name.lower():
                for availability in prof.get("availability", []):
                    for slot in availability.get("slots", []):
                        start_str, end_str = slot.split("-")
                        start_time = pendulum.parse(start_str, strict=False)
                        end_time = pendulum.parse(end_str, strict=False)

                        current_time = start_time
                        while current_time.add(minutes=self.get_duration()) <= end_time:
                            current_time_str = current_time.format("HH:mm")
                            if self._validate_slot(availability["day"], current_time_str):
                                slots.append({
                                    "professional": prof["name"],
                                    "day": availability["day"],
                                    "slot": f"{current_time_str}-{(current_time.add(minutes=self.get_duration())).format('HH:mm')}"
                                })
                            current_time = current_time.add(minutes=self.get_duration())
        return slots

    def _validate_slot(self, requested_day: str, requested_time: str) -> bool:
        day_key = requested_day.strip().lower()
        english_day = DAY_MAP.get(day_key)
        if not english_day:
            return False

        try:
            hour, minute = map(int, requested_time.strip().split(":"))
        except ValueError:
            return False

        today = pendulum.now(settings.TIMEZONE)
        appointment_dt = today.next(english_day).replace(hour=hour, minute=minute, second=0, microsecond=0)
        duration = self.get_duration()

        return is_slot_available(appointment_dt, appointment_dt.add(minutes=duration))

    def schedule(self, user_name: str, requested_day: str, requested_time: str, professional_name: Optional[str] = None) -> Dict[str, str]:
        """
        Attempts to schedule an appointment for the user with a professional.
        If no professional specified, tries all available professionals for that slot.
        Returns a status dict indicating success, error, or no availability.
        """
        logger.info(f"Attempting to schedule {self.name} for {user_name} on {requested_day} at {requested_time} with {professional_name if professional_name else 'any available professional'}")
        appointment_dt = None
        duration = self.get_duration()
        if not professional_name:
            professionals = self.find_professionals_for_slot(requested_day, requested_time)
        else:
            professionals = [professional_name]

        for professional in professionals:
            if self._validate_slot(requested_day, requested_time):
                now = pendulum.now(settings.TIMEZONE)
                day_key = requested_day.strip().lower()
                english_day = DAY_MAP.get(day_key)
                if not english_day:
                    continue
                try:
                    hour, minute = map(int, requested_time.strip().split(":"))
                except ValueError:
                    continue
                appointment_dt = now.next(english_day).replace(hour=hour, minute=minute, second=0, microsecond=0)
                # If slot is free, create event and return success
                event_id = create_event(user_name, self.name, professional, appointment_dt, duration)
                logger.info(f"Appointment scheduled: {event_id}")
                return {
                    "status": "success",
                    "message": f"Cita agendada com {professional} em {appointment_dt.to_datetime_string()}",
                    "event_id": event_id,
                }

        # If no professionals available at the requested time, return no availability
        logger.warning(f"No availability for {self.name} on {requested_day} at {requested_time}")
        return {
            "status": "no_availability",
            "message": f"Todos os profissionais estão ocupados nesse horário para {self.name} na {requested_day} às {requested_time}.",
        }


class Services:
    """
    Container class to manage multiple Service instances.
    Loads services configuration from a YAML file.
    """
    def __init__(self, config_path: str = settings.SERVICES_FILE) -> None:
        # Load services configuration from YAML file
        with open(config_path, "r") as f:
            config = yaml.safe_load(f)
        self.services = [Service(s) for s in config.get("services", [])]
        logger.info(f"Loaded {len(self.services)} services from {config_path}")

    def get_all(self) -> List[Service]:
        # Return list of all Service instances
        return self.services

    def get_by_name(self, name: str) -> Optional[Service]:
        """
        Find and return a Service instance by name.
        Uses unidecode normalization for case-insensitive and accent-insensitive matching.
        """
        normalized_query = unidecode(name.lower())
        for service in self.services:
            normalized_service = unidecode(service.name.lower())
            if normalized_query in normalized_service or normalized_service in normalized_query:
                logger.debug(f"Service found for query '{name}': {service.name}")
                return service
        logger.warning(f"No service found for query '{name}'")
        return None