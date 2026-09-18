from dotenv import load_dotenv
load_dotenv()

from mcp.server import MCPServer
from google_calendar import (
    check_availability as _check_availability,
    create_event as _create_event,
)
from tasks import add_task as _add_task, list_tasks as _list_tasks
from gmail import send_email as _send_email

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


@mcp.tool()
def add_task(title: str, due_date: str | None = None, priority: str = "medium") -> dict:
    """
    Add a new task to the task tracker.

    Args:
        title: What the task is.
        due_date: Optional due date in YYYY-MM-DD format.
        priority: One of "low", "medium", "high".

    Returns:
        The created task, including its id.
    """
    return _add_task(title, due_date, priority)


@mcp.tool()
def list_tasks(include_done: bool = False) -> list[dict]:
    """
    List current tasks.

    Args:
        include_done: If true, include already-completed tasks.

    Returns:
        A list of tasks.
    """
    return _list_tasks(include_done)


@mcp.tool()
def send_email(to: str, subject: str, body: str) -> dict:
    """
    Send an email from the user's Gmail account.

    Args:
        to: Recipient email address.
        subject: Email subject line.
        body: Plain-text email body.

    Returns:
        A dict with the sent message's id.
    """
    return _send_email(to, subject, body)


if __name__ == "__main__":
    mcp.run(transport="streamable-http", host="127.0.0.1", port=8000)