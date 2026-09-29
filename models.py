"""Data model for the Task Manager module."""
from dataclasses import dataclass
from typing import Optional


@dataclass
class Task:
    """A single task, mirroring one row of the ``tasks`` table."""
    id: int
    title: str
    description: str
    priority: str              # "low" | "medium" | "high"
    due_date: Optional[str]    # "YYYY-MM-DD" or None
    status: str                # "pending" | "completed"
    created_at: str
