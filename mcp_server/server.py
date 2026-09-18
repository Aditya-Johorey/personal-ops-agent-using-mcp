from dotenv import load_dotenv
load_dotenv()

from mcp.server import MCPServer
from google_calendar import (
    check_availability as _check_availability,
    create_event as _create_event,
)

mcp = MCPServer("PersonalOpsServer")


@mcp.tool()
def check_availability(date: str, duration_minutes: int = 30) -> list[str]:
    """
    Check available time slots on a given date that can fit a meeting
    of the given duration.

    Args:
        date: Date in YYYY-MM-DD format.
        duration_minutes: Length of the meeting in minutes (default 30).

    Returns:
        A list of available start times (HH:MM) on that date.
    """
    return _check_availability(date, duration_minutes)


@mcp.tool()
def create_event(
    date: str,
    start_time: str,
    duration_minutes: int,
    title: str,
    description: str = "",
    attendee_emails: list[str] | None = None,
) -> dict:
    """
    Create an event on the user's primary Google Calendar.

    Args:
        date: Date in YYYY-MM-DD format.
        start_time: Start time in HH:MM 24h format.
        duration_minutes: Length of the event in minutes.
        title: Event title/summary.
        description: Optional event description.
        attendee_emails: Optional list of attendee email addresses to invite.

    Returns:
        A dict with the created event's id and a link to view it.
    """
    return _create_event(date, start_time, duration_minutes, title, description, attendee_emails)


if __name__ == "__main__":
    mcp.run()