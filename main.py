"""Command-line interface for the Task Manager module."""
from datetime import date

from database import Database
from task_service import TaskService, ValidationError

MENU = """
=== Task Manager ===
1. Add task   2. View tasks   3. Update task
4. Complete   5. Delete       6. Suggest next   7. Exit"""


def print_tasks(tasks):
    if not tasks:
        print("No tasks found.")
        return
    print(f"{'ID':<4}{'Title':<32}{'Priority':<10}{'Due date':<12}{'Status'}")
    for t in tasks:
        print(f"{t.id:<4}{t.title[:30]:<32}{t.priority:<10}{(t.due_date or '-'):<12}{t.status}")


def ask_id(prompt="Task ID: "):
    try:
        return int(input(prompt))
    except ValueError:
        raise ValidationError("task ID must be a number")


def handle(choice, service):
    if choice == "1":
        title = input("Title: ")
        description = input("Description (optional): ")
        priority = input("Priority (low/medium/high): ")
        due = input("Due date (YYYY-MM-DD, optional): ")
        task_id = service.add_task(title, priority, due, description)
        print(f"Task added with ID {task_id}")
    elif choice == "2":
        status = input("Filter by status (pending/completed, blank = all): ").strip().lower()
        priority = input("Filter by priority (low/medium/high, blank = all): ").strip().lower()
        print_tasks(service.list_tasks(status, priority))
    elif choice == "3":
        task = service.get_task(ask_id())
        print("Leave a field blank to keep its current value.")
        changes = {}
        for field in ("title", "description", "priority", "due_date"):
            value = input(f"New {field} [{getattr(task, field) or ''}]: ")
            if value.strip():
                changes[field] = value
        service.update_task(task.id, **changes)
        print(f"Task {task.id} updated")
    elif choice == "4":
        task = service.complete_task(ask_id())
        print(f"Task {task.id} marked as completed")
    elif choice == "5":
        task_id = ask_id()
        service.delete_task(task_id)
        print(f"Task {task_id} deleted")
    elif choice == "6":
        task = service.suggest_next_task()
        if task is None:
            print("No pending tasks. Nothing to suggest.")
        else:
            print(f"Suggested next task: [{task.id}] {task.title} (score {service.score(task)})")
    else:
        print("Invalid option. Please choose 1-7.")


def main():
    service = TaskService(Database("tasks.db"))
    while True:
        print(MENU)
        try:
            choice = input("Choose an option: ").strip()
            if choice == "7":
                print("Goodbye!")
                break
            handle(choice, service)
        except ValidationError as err:
            print(f"Error: {err}")
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            break


if __name__ == "__main__":
    main()
