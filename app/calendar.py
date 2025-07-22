from google.oauth2 import service_account
from googleapiclient.discovery import build
from datetime import timedelta
from app.settings import settings
import logging
from typing import List, Optional
from datetime import datetime

logging.basicConfig(level=settings.LOG_LEVEL)
logger = logging.getLogger(__name__)


credentials = service_account.Credentials.from_service_account_file(
    settings.GOOGLE_CREDENTIALS_FILE, scopes=settings.SCOPES
)
service = build("calendar", "v3", credentials=credentials)

def get_events(start_time: datetime, end_time: datetime) -> List[dict]:
    try:
        logger.info(f"Fetching events from {start_time} to {end_time}")
        events_result = (
            service.events()
            .list(
                calendarId=settings.GOOGLE_CALENDAR_ID,
                timeMin=start_time.isoformat(),
                timeMax=end_time.isoformat(),
                singleEvents=True,
                orderBy="startTime",
            )
            .execute()
        )
        return events_result.get("items", [])
    except Exception as e:
        logger.error(f"Erro ao buscar eventos do Google Calendar: {e}")
        return []

def is_slot_available(start_time: datetime, end_time: datetime) -> bool:
    events = get_events(start_time, end_time)
    logger.info(f"Checked slot availability from {start_time} to {end_time}: {'available' if len(events) == 0 else 'not available'}")
    return len(events) == 0

def create_event(user_name: str, service_name: str, professional_name: str, start_time: datetime, duration_minutes: int) -> Optional[str]:
    end_time = start_time + timedelta(minutes=duration_minutes)
    event = {
        "summary": f"{user_name} - {service_name}",
        "description": f"Profissional: {professional_name}",
        "start": {"dateTime": start_time.isoformat(), "timeZone": settings.TIMEZONE},
        "end": {"dateTime": end_time.isoformat(), "timeZone": settings.TIMEZONE},
    }
    logger.info(f"Creating event for {user_name} - {service_name} with {professional_name} starting at {start_time} for {duration_minutes} minutes")
    try:
        created_event = service.events().insert(calendarId=settings.GOOGLE_CALENDAR_ID, body=event).execute()
        return created_event.get("id")
    except Exception as e:
        logger.error(f"Erro ao criar evento no Google Calendar: {e}")
        return None