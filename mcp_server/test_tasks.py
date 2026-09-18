from tasks import add_task, list_tasks

if __name__ == "__main__":
    task = add_task("Test task from MCP project", due_date="2026-09-25", priority="high")
    print("Created:", task)
    print("All tasks:", list_tasks())