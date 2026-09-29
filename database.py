"""Data access layer: all SQL lives here.

Every query is parameterised (``?`` placeholders), so user text is never
concatenated into SQL. This prevents SQL injection.
"""
import sqlite3
from datetime import datetime
from typing import List, Optional

from models import Task

# Columns that callers are allowed to update. Whitelisting the column names
# keeps the dynamic UPDATE statement below safe.
UPDATABLE_COLUMNS = {"title", "description", "priority", "due_date", "status"}


class Database:
    """Thin wrapper around a SQLite connection."""

    def __init__(self, path: str = "tasks.db"):
        # Use ":memory:" for tests so real data is never touched.
        self.conn = sqlite3.connect(path)
        self.conn.row_factory = sqlite3.Row
        self._create_table()

    def _create_table(self) -> None:
        self.conn.execute(
            """
            CREATE TABLE IF NOT EXISTS tasks (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                title       TEXT NOT NULL,
                description TEXT DEFAULT '',
                priority    TEXT NOT NULL,
                due_date    TEXT,
                status      TEXT NOT NULL DEFAULT 'pending',
                created_at  TEXT NOT NULL
            )
            """
        )
        self.conn.commit()

    @staticmethod
    def _to_task(row: sqlite3.Row) -> Task:
        return Task(**dict(row))

    # ---- Create ---------------------------------------------------------
    def insert(self, title: str, description: str, priority: str,
               due_date: Optional[str]) -> int:
        """Insert a task and return its new ID."""
        cur = self.conn.execute(
            "INSERT INTO tasks (title, description, priority, due_date, created_at) "
            "VALUES (?, ?, ?, ?, ?)",
            (title, description, priority, due_date,
             datetime.now().isoformat(timespec="seconds")),
        )
        self.conn.commit()
        return cur.lastrowid

    # ---- Read -----------------------------------------------------------
    def get(self, task_id: int) -> Optional[Task]:
        row = self.conn.execute(
            "SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
        return self._to_task(row) if row else None

    def list(self, status: Optional[str] = None,
             priority: Optional[str] = None) -> List[Task]:
        """Return tasks, optionally filtered by status and/or priority."""
        query, params = "SELECT * FROM tasks WHERE 1=1", []
        if status:
            query += " AND status = ?"
            params.append(status)
        if priority:
            query += " AND priority = ?"
            params.append(priority)
        query += " ORDER BY id"
        return [self._to_task(r) for r in self.conn.execute(query, params)]

    # ---- Update ---------------------------------------------------------
    def update(self, task_id: int, **fields) -> bool:
        """Update the given columns. Returns True if a row was changed."""
        if not fields:
            return False
        if not set(fields) <= UPDATABLE_COLUMNS:
            raise ValueError("Unknown column in update")
        assignments = ", ".join(f"{col} = ?" for col in fields)
        cur = self.conn.execute(
            f"UPDATE tasks SET {assignments} WHERE id = ?",
            (*fields.values(), task_id),
        )
        self.conn.commit()
        return cur.rowcount > 0

    # ---- Delete ---------------------------------------------------------
    def delete(self, task_id: int) -> bool:
        cur = self.conn.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
        self.conn.commit()
        return cur.rowcount > 0

    def close(self) -> None:
        self.conn.close()
