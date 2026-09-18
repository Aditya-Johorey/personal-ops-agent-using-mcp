import os
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google_auth import get_service

# Candidate slots we offer, in HH:MM 24h format, in the user's local timezone.
ALL_SLOTS = ["09:00", "10:00", "11:00", "13:00", "14:00", "15:30", "16:00"]


def get_calendar_service():
    return get_service("calendar", "v3")

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

def create_event(date_str: str,
    start_time: str,
    duration_minutes: int,
    title: str,
    description: str = "",
    attendee_emails: list[str] | None = None,
) -> dict:
    """
    Create an event on the primary calendar.

    Args:
        date_str: Date in YYYY-MM-DD format.
        start_time: Start time in HH:MM 24h format.
        duration_minutes: Length of the event in minutes.
        title: Event title/summary.
        description: Optional event description.
        attendee_emails: Optional list of attendee email addresses.

    Returns:
        A dict with the created event's id and a link to view it.
    """

    tz = get_user_timezone()
    service = get_calendar_service()

    hour, minute = map(int, start_time.split(":"))
    start_dt = datetime.strptime(date_str, "%Y-%m-%d").replace(
        hour=hour, minute=minute, tzinfo=tz
    )
    end_dt = start_dt + timedelta(minutes=duration_minutes)

    event_body = {
        "summary":title,
        "description":description,
        "start": {"dateTime": start_dt.isoformat(), "timeZone": str(tz)},
        "end": {"dateTime": end_dt.isoformat(), "timeZone": str(tz)},
    }

    if attendee_emails:
        event_body["attendees"] = [{"email": email} for email in attendee_emails]

    created = service.events().insert(
        calendarId = "primary",
        body = event_body,
        sendUpdates = "all" if attendee_emails else None
    ).execute()

    return {"event_id": created["id"], "link": created.get("htmlLink", "")}