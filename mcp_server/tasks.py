import json
import uuid
from datetime import datetime
from pathlib import Path

TASK_FILE = Path(__file__).parent.parent / "data" / "tasks.json"

def _load_tasks() -> list[dict]:
    if not TASK_FILE.exists():
        return []
    return json.loads(TASK_FILE.read_text())

def _save_tasks(tasks: list[dict]) ->None:
    TASK_FILE.parent.mkdir(parents = True, exist_ok=True)
    TASK_FILE.write_text(json.dumps(tasks, indent = 2))

def add_task(title: str, due_date: str | None = None, priority: str = "medium") -> dict:
    """
    Add a new task.

    Args:
        title: What the task is.
        due_date: Optional due date in YYYY-MM-DD format.
        priority: One of "low", "medium", "high".

    Returns:
        The created task, including its id.
    """
    tasks = _load_tasks()
    task = {
        "id": str(uuid.uuid4())[:8],
        "title": title,
        "due_date": due_date,
        "priority": priority,
        "done":False,
        "created_at": datetime.now().isoformat()
    }
    tasks.append(task)
    _save_tasks(tasks)
    return task

def list_tasks(include_done: bool = False) -> list[dict]:
    """
    List tasks, optionally including completed ones.
    """
    tasks = _load_tasks()
    if not include_done:
        tasks = [t for t in tasks if not t["done"]]
    return tasks