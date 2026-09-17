from dotenv import load_dotenv
load_dotenv()

from mcp.server import MCPServer
from google_calendar import check_availability as _check_availability

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


if __name__ == "__main__":
    mcp.run()