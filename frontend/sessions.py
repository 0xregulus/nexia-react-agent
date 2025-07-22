import json
import os
from app.settings import settings

def load_sessions():
    if os.path.exists(settings.SESSIONS_FILE):
        with open(settings.SESSIONS_FILE, "r") as f:
            return json.load(f)
    return {}

def save_sessions(sessions):
    with open(settings.SESSIONS_FILE, "w") as f:
        json.dump(sessions, f, indent=2)
