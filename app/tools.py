from typing import Any, Callable, List
from app.configuration import Configuration
import logging
from app.settings import settings

logging.basicConfig(level=settings.LOG_LEVEL)
logger = logging.getLogger(__name__)


async def list_services() -> List[str]:
    """List available services."""
    configuration = Configuration.from_context()
    services = configuration.services.get_all()
    logger.info("Listing available services")
    return [service.get_name() for service in services]

async def get_available_slots(service_name: str) -> List[dict[str, Any]]:
    """Get available slots for a service."""
    configuration = Configuration.from_context()
    services = configuration.services
    service = services.get_by_name(service_name)
    logger.info(f"Getting available slots for service: {service_name}")
    if not service:
        return []
    return service.get_available_slots()

async def get_slots_for_professional(service_name: str, professional_name: str) -> List[dict[str, Any]]:
    """Get available slots for a service."""
    configuration = Configuration.from_context()
    services = configuration.services
    service = services.get_by_name(service_name)
    logger.info(f"Getting available slots for service: {service_name} and professional: {professional_name}")
    if not service:
        return []
    return service.get_slots_for_professional(professional_name)

async def schedule_appointment(user_name: str, service_name: str, day: str, time: str) -> dict[str, Any]:
    """Attempt to schedule an appointment."""
    configuration = Configuration.from_context()
    service = configuration.services.get_by_name(service_name)
    if not service:
        logger.warning(f"Service '{service_name}' not found for user '{user_name}'")
        return {"status": "error", "message": f"Serviço '{service_name}' não encontrado."}
    else:
        logger.info(f"Scheduling appointment for user: {user_name}, service: {service_name}, day: {day}, time: {time}")
    result = service.schedule(user_name, day, time)
    return result

TOOLS: List[Callable[..., Any]] = [list_services, get_available_slots, get_slots_for_professional, schedule_appointment]