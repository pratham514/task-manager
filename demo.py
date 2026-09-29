"""Reproduces the worked example from the report (Section 6.2).

Run:  python demo.py
Uses an in-memory database, so it never touches tasks.db.
"""
from datetime import date

from database import Database
from task_service import TaskService

TODAY = date(2026, 9, 29)

SAMPLE = [
    ("Finish internship report", "high", "2026-10-01"),
    ("Buy groceries", "low", "2026-09-29"),
    ("Prepare presentation", "medium", "2026-10-05"),
    ("Submit fee form", "high", "2026-09-27"),
    ("Read book", "low", "2026-11-01"),
]

service = TaskService(Database(":memory:"))
for title, priority, due in SAMPLE:
    service.add_task(title, priority, due)

print(f"Scores as of {TODAY}:")
for task in service.list_tasks():
    print(f"  [{task.id}] {task.title:<28} score {service.score(task, TODAY)}")

best = service.suggest_next_task(TODAY)
print(f"\nSuggested next task: [{best.id}] {best.title} (score {service.score(best, TODAY)})")
