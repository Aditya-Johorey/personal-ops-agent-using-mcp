from dotenv import load_dotenv
load_dotenv()

from google_calendar import create_event

if __name__ == "__main__":
    result = create_event(
        date_str="2026-09-20",
        start_time="14:00",
        duration_minutes=30,
        title="Test event from MCP project",
        description="Just testing create_event before wiring into MCP.",
    )
    print(result)