"""Service layer: validation, business rules and task suggestion scoring."""
import re
from datetime import date, datetime
from typing import List, Optional

from database import Database
from models import Task

VALID_PRIORITIES = ("low", "medium", "high")
VALID_STATUSES = ("pending", "completed")

# Points awarded for each priority level (see README / report, Section 6).
PRIORITY_POINTS = {"high": 30, "medium": 20, "low": 10}


class ValidationError(Exception):
    """Raised when input is invalid or a task cannot be found."""


class TaskService:
    """Business logic. The interface layer talks only to this class."""

    def __init__(self, db: Database):
        self.db = db

    # ---- Validation helpers --------------------------------------------
    @staticmethod
    def _clean_title(title: str) -> str:
        title = (title or "").strip()
        if not title:
            raise ValidationError("title cannot be empty")
        return title

    @staticmethod
    def _clean_priority(priority: str) -> str:
        priority = (priority or "").strip().lower()
        if priority not in VALID_PRIORITIES:
            raise ValidationError("priority must be low, medium or high")
        return priority

    @staticmethod
    def _clean_due_date(due_date: Optional[str]) -> Optional[str]:
        due_date = (due_date or "").strip()
        if not due_date:
            return None  # due date is optional
        # The regex rejects loose formats such as "2026-9-1";
        # strptime then rejects impossible dates such as "2026-02-30".
        if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", due_date):
            raise ValidationError("date must be YYYY-MM-DD")
        try:
            datetime.strptime(due_date, "%Y-%m-%d")
        except ValueError:
            raise ValidationError("date must be YYYY-MM-DD")
        return due_date

    # ---- CRUD -----------------------------------------------------------
    def add_task(self, title: str, priority: str, due_date: Optional[str] = None,
                 description: str = "") -> int:
        """Validate the input, save the task and return its new ID."""
        return self.db.insert(
            self._clean_title(title),
            (description or "").strip(),
            self._clean_priority(priority),
            self._clean_due_date(due_date),
        )

    def get_task(self, task_id: int) -> Task:
        task = self.db.get(task_id)
        if task is None:
            raise ValidationError("task not found")
        return task

    def list_tasks(self, status: Optional[str] = None,
                   priority: Optional[str] = None) -> List[Task]:
        if status and status not in VALID_STATUSES:
            raise ValidationError("status must be pending or completed")
        if priority:
            priority = self._clean_priority(priority)
        return self.db.list(status or None, priority)

    def update_task(self, task_id: int, **fields) -> Task:
        """Update only the fields supplied (title, description, priority, due_date)."""
        self.get_task(task_id)  # raises "task not found" if missing
        cleaned = {}
        if "title" in fields:
            cleaned["title"] = self._clean_title(fields["title"])
        if "description" in fields:
            cleaned["description"] = (fields["description"] or "").strip()
        if "priority" in fields:
            cleaned["priority"] = self._clean_priority(fields["priority"])
        if "due_date" in fields:
            cleaned["due_date"] = self._clean_due_date(fields["due_date"])
        self.db.update(task_id, **cleaned)
        return self.get_task(task_id)

    def complete_task(self, task_id: int) -> Task:
        self.get_task(task_id)
        self.db.update(task_id, status="completed")
        return self.get_task(task_id)

    def delete_task(self, task_id: int) -> None:
        if not self.db.delete(task_id):
            raise ValidationError("task not found")

    # ---- Suggestion (rule-based recommendation) -------------------------
    @staticmethod
    def urgency_points(due_date: Optional[str], today: date) -> int:
        """Points for how close the due date is."""
        if not due_date:
            return 0
        days_left = (datetime.strptime(due_date, "%Y-%m-%d").date() - today).days
        if days_left < 0:
            return 30      # overdue
        if days_left == 0:
            return 25      # due today
        if days_left <= 3:
            return 15      # due in 1-3 days
        if days_left <= 7:
            return 5       # due in 4-7 days
        return 0           # more than a week away

    def score(self, task: Task, today: Optional[date] = None) -> int:
        """Total score = priority points + urgency points."""
        today = today or date.today()
        return PRIORITY_POINTS[task.priority] + self.urgency_points(task.due_date, today)

    def suggest_next_task(self, today: Optional[date] = None) -> Optional[Task]:
        """Return the pending task with the highest score, or None.

        Ties are broken by the earlier due date (tasks with no due date last).
        """
        today = today or date.today()
        pending = self.db.list(status="pending")
        if not pending:
            return None
        return sorted(
            pending,
            key=lambda t: (-self.score(t, today), t.due_date or "9999-12-31"),
        )[0]
