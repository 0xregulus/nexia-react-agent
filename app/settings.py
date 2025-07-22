import os
from dotenv import load_dotenv
load_dotenv()

from dataclasses import dataclass, field


@dataclass
class Settings:
    LLM_API_KEY: str = field(default=os.getenv("LLM_API_KEY"))
    TIMEZONE: str = field(default=os.getenv("TIMEZONE"))
    GOOGLE_CALENDAR_ID: str = field(default=os.getenv("GOOGLE_CALENDAR_ID"))
    SCOPES: list[str] = field(default_factory=lambda: ["https://www.googleapis.com/auth/calendar"])
    GOOGLE_CREDENTIALS_FILE: str = field(default=os.getenv("GOOGLE_CREDENTIALS_FILE"))
    TELEGRAM_BOT_TOKEN: str = field(default=os.getenv("TELEGRAM_BOT_TOKEN"))
    LOG_LEVEL: str = field(default=os.getenv("LOG_LEVEL", "INFO"))
    LOG_FILE: str = field(default=os.getenv("LOG_FILE", "app.log"))
    SESSIONS_FILE: str = field(default=os.getenv("SESSIONS_FILE", "data/sessions.json"))
    SERVICES_FILE: str = field(default=os.getenv("SERVICES_FILE", "data/services.yaml"))

settings = Settings()

