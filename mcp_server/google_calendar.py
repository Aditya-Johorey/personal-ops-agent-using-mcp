import os
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ["https://www.googleapis.com/auth/calendar"]
TOKEN_FILE = "token.json"
CLIENT_SECRET_FILE = "credentials/client_secret.json"

# Candidate slots we offer, in HH:MM 24h format, in the user's local timezone.
ALL_SLOTS = ["09:00", "10:00", "11:00", "13:00", "14:00", "15:30", "16:00"]

def get_calendar_service():
    creds = None
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(TOKEN_FILE, "w") as f:
            f.write(creds.to_json())
    return build("calendar", "v3", credentials=creds)

def get_user_timezone() -> ZoneInfo:
    tz_name = os.getenv("USER_TIMEZONE", "UTC")
    return ZoneInfo(tz_name)

def check_availability(date_str: str, duration_minutes: int = 30) -> list[str]:
    """
    Check free slots on a given date (YYYY-MM-DD) that can fit a meeting
    of the given duration, in the user's local timezone.
    """

    tz = get_user_timezone()
    service = get_calendar_service()

    day_start = datetime.strptime(date_str, "%Y-%m-%d").replace(tzinfo=tz)
    day_end = day_start + timedelta(days=1)

    body = {
        "timeMin": day_start.isoformat(),
        "timeMax": day_end.isoformat(),
        "timeZone": str(tz),
        "items": [{"id": "primary"}]
    }

    result = service.freebusy().query(body = body).execute()
    busy_periods = result["calendars"]["primary"]["busy"]

    free_slots = []
    for slot in ALL_SLOTS:
        hour, minute = map(int, slot.split(":"))
        slot_start = day_start.replace(hour=hour, minute=minute)
        slot_end = slot_start + timedelta(minutes=duration_minutes)

        overlaps = False
        for busy in busy_periods:
            busy_start = datetime.fromisoformat(busy["start"])
            busy_end = datetime.fromisoformat(busy["end"])
            if slot_start < busy_end and slot_end > busy_start:
                overlaps = True
                break

        if not overlaps:
            free_slots.append(slot)

    return free_slots