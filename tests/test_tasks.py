"""Unit tests. Each test uses a fresh in-memory database."""
import os
import sys
import unittest
from datetime import date

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import Database
from task_service import TaskService, ValidationError

TODAY = date(2026, 9, 29)


class TaskServiceTests(unittest.TestCase):
    def setUp(self):
        self.service = TaskService(Database(":memory:"))

    def tearDown(self):
        self.service.db.close()

    # ---- CRUD ----
    def test_create_valid_task(self):
        task_id = self.service.add_task("Read", "low")
        self.assertEqual(task_id, 1)
        self.assertEqual(self.service.get_task(task_id).title, "Read")

    def test_empty_title(self):
        with self.assertRaisesRegex(ValidationError, "title cannot be empty"):
            self.service.add_task("", "low")

    def test_invalid_priority(self):
        with self.assertRaisesRegex(ValidationError, "priority must be low, medium or high"):
            self.service.add_task("Read", "urgent")

    def test_invalid_date(self):
        with self.assertRaisesRegex(ValidationError, "date must be YYYY-MM-DD"):
            self.service.add_task("Read", "low", "31-12-2026")

    def test_update_task(self):
        task_id = self.service.add_task("Read", "low")
        self.service.update_task(task_id, priority="high")
        self.assertEqual(self.service.get_task(task_id).priority, "high")

    def test_complete_task(self):
        task_id = self.service.add_task("Read", "low")
        self.service.complete_task(task_id)
        self.assertEqual(self.service.get_task(task_id).status, "completed")

    def test_delete_task(self):
        task_id = self.service.add_task("Read", "low")
        self.service.delete_task(task_id)
        self.assertEqual(self.service.list_tasks(), [])

    def test_delete_missing_task(self):
        with self.assertRaisesRegex(ValidationError, "task not found"):
            self.service.delete_task(999)

    def test_filter_by_priority(self):
        self.service.add_task("A", "low")
        self.service.add_task("B", "high")
        result = self.service.list_tasks(priority="high")
        self.assertEqual([t.title for t in result], ["B"])

    # ---- Suggestion ----
    def test_suggestion_order(self):
        for title, priority, due in [
            ("Finish internship report", "high", "2026-10-01"),
            ("Buy groceries", "low", "2026-09-29"),
            ("Prepare presentation", "medium", "2026-10-05"),
            ("Submit fee form", "high", "2026-09-27"),
            ("Read book", "low", "2026-11-01"),
        ]:
            self.service.add_task(title, priority, due)
        best = self.service.suggest_next_task(TODAY)
        self.assertEqual(best.id, 4)
        self.assertEqual(self.service.score(best, TODAY), 60)

    def test_suggestion_tie_prefers_earlier_due_date(self):
        # Both are high priority and due within 1-3 days -> equal score (45).
        self.service.add_task("Later", "high", "2026-10-02")
        self.service.add_task("Sooner", "high", "2026-10-01")
        best = self.service.suggest_next_task(TODAY)
        self.assertEqual(best.title, "Sooner")

    def test_suggestion_empty(self):
        self.assertIsNone(self.service.suggest_next_task(TODAY))

    def test_completed_tasks_not_suggested(self):
        task_id = self.service.add_task("Done already", "high", "2026-09-27")
        self.service.complete_task(task_id)
        self.assertIsNone(self.service.suggest_next_task(TODAY))


if __name__ == "__main__":
    unittest.main()
