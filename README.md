# Task Manager

A small command-line task manager written in Python with SQLite storage. It supports full CRUD operations and a rule-based **"suggest next task"** feature that ranks pending tasks by priority and urgency.

Built as a mini software module to practise clean, modular, documented code.

## Features

- **Create** tasks with title, description, priority (`low` / `medium` / `high`) and optional due date
- **Read** all tasks, filtered by status or priority
- **Update** any task field, or mark a task as completed
- **Delete** tasks
- **Suggest** which pending task to work on next
- Input validation with clear error messages
- Unit tests (standard library `unittest`)

## Requirements

- Python 3.8 or newer
- No third-party packages

## Installation

```bash
git clone https://github.com/<username>/task-manager.git
cd task-manager

# optional: virtual environment
python -m venv venv
venv\Scripts\activate          # Windows
source venv/bin/activate       # macOS / Linux
```

## Usage

```bash
python main.py
```

```
=== Task Manager ===
1. Add task   2. View tasks   3. Update task
4. Complete   5. Delete       6. Suggest next   7. Exit
```

Example session:

```
Choose an option: 1
Title: Finish internship report
Description (optional):
Priority (low/medium/high): high
Due date (YYYY-MM-DD, optional): 2026-10-01
Task added with ID 1

Choose an option: 1
Title: Buy groceries
Description (optional):
Priority (low/medium/high): urgent
Error: priority must be low, medium or high

Choose an option: 6
Suggested next task: [1] Finish internship report (score 45)
```

Tasks are saved in `tasks.db`, which is created automatically on first run.

### Demo of the suggestion feature

```bash
python demo.py
```

Loads five sample tasks into an in-memory database and shows how the scoring picks the next task (matches Section 6.2 of the report).

### Run the tests

```bash
python -m unittest discover tests
```

## Project structure

```
task-manager/
├── main.py            # Command-line interface
├── task_service.py    # Validation, business rules, suggestion scoring
├── database.py        # SQLite access (parameterised SQL)
├── models.py          # Task data class
├── demo.py            # Worked example of the suggestion feature
├── tests/
│   └── test_tasks.py  # Unit tests
├── docs/
│   └── Task_Manager_Report_v2.docx
├── requirements.txt
└── README.md
```

## Architecture

```
User -> main.py (interface) -> task_service.py (service) -> database.py (data access) -> tasks.db
                                      |
                                  models.py (Task)
```

Each layer has one job, so the command-line interface could be replaced by a web UI without changing the service or database code.

## Suggestion scoring

Each pending task gets **priority points + urgency points**.

| Priority | Points |   | Due date | Points |
|----------|--------|---|----------|--------|
| high     | 30     |   | overdue  | 30     |
| medium   | 20     |   | today    | 25     |
| low      | 10     |   | 1-3 days | 15     |
|          |        |   | 4-7 days | 5      |
|          |        |   | later / none | 0  |

The highest total wins; ties are broken by the earlier due date.

## Development decisions

- **Layered design** for separation of concerns and easy testing.
- **SQLite** needs no setup and ships with Python.
- **Parameterised queries** everywhere to prevent SQL injection; the dynamic `UPDATE` only accepts whitelisted column names.
- **Validation in one place** (the service layer) to avoid duplicated checks.
- **Rule-based suggestions** rather than machine learning: transparent, explainable and deterministic, which makes it simple to test.
- **In-memory database in tests** so real data is never touched.

## Database schema

| Column      | Type    | Notes                          |
|-------------|---------|--------------------------------|
| id          | INTEGER | Primary key, auto-increment    |
| title       | TEXT    | Required                       |
| description | TEXT    | Optional                       |
| priority    | TEXT    | low / medium / high            |
| due_date    | TEXT    | YYYY-MM-DD, optional           |
| status      | TEXT    | pending / completed            |
| created_at  | TEXT    | Timestamp                      |

## Future improvements

User accounts, task categories, a web front end, and a learned recommendation model once enough usage data exists.

## Author

Pratham
