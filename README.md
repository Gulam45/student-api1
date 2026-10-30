# Library Management API

A backend-only library management system built with FastAPI, Pydantic,
SQLAlchemy, and SQLite. Books, members, and lending history are stored in
`library.db` in the project root and persist when the server restarts.

## Features

- Create, list, retrieve, update, delete, and search books.
- Register, list, retrieve, update, and delete members.
- Issue available books to registered members and track due dates.
- Return books, restore availability, and calculate overdue days.
- Keep lending history; books and members with issue records cannot be deleted.
- Validate request data and return useful 404 and 409 errors.
- Explore the API using generated Swagger UI and OpenAPI documentation.

## Project structure

```text
student-api1/
├── app/
│   ├── api/
│   │   ├── books.py
│   │   ├── issues.py
│   │   └── members.py
│   ├── models/
│   │   ├── book.py
│   │   ├── issue.py
│   │   └── member.py
│   ├── schemas/
│   │   ├── books.py
│   │   ├── issues.py
│   │   └── members.py
│   ├── services/
│   │   └── issues.py
│   ├── database.py
│   └── main.py
├── tests/
│   ├── conftest.py
│   ├── test_books.py
│   ├── test_issues.py
│   └── test_members.py
├── requirements.txt
└── README.md
```

## Requirements and setup (Windows PowerShell)

Install Python 3.10 or newer. From the project folder, create and activate a
virtual environment:

```powershell
cd D:\student-api1
py -m venv .venv
.\.venv\Scripts\Activate.ps1
```

If PowerShell prevents environment activation, allow it for the current
PowerShell process and activate again:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

Install the project dependencies:

```powershell
python -m pip install -r requirements.txt
```

## Run the application

Start the development server from the project folder:

```powershell
python -m uvicorn app.main:app --reload
```

- Swagger UI: <http://127.0.0.1:8000/docs>
- OpenAPI JSON: <http://127.0.0.1:8000/openapi.json>
- The root URL <http://127.0.0.1:8000> redirects to Swagger UI.

The SQLite database file `library.db` is created automatically on startup.
Back up this file to preserve library data.

## API endpoints

All endpoints use `http://127.0.0.1:8000` as their base URL.

| Method | Endpoint | Description |
| --- | --- | --- |
| `POST` | `/books` | Add a book |
| `GET` | `/books` | List all books |
| `GET` | `/books/search?title=...&author=...&category=...` | Search books by one or more fields |
| `GET` | `/books/{book_id}` | Get a book and its availability |
| `PUT` | `/books/{book_id}` | Replace a book's title, author, and category |
| `DELETE` | `/books/{book_id}` | Delete a book with no lending history |
| `POST` | `/members` | Register a member |
| `GET` | `/members` | List all members |
| `GET` | `/members/{member_id}` | Get a member |
| `PUT` | `/members/{member_id}` | Replace a member's information |
| `DELETE` | `/members/{member_id}` | Delete a member with no lending history |
| `GET` | `/members/{member_id}/issues` | List that member's lending history |
| `POST` | `/issues` | Issue an available book to a member |
| `GET` | `/issues` | List all lending records |
| `GET` | `/issues?active_only=true` | List active loans only |
| `POST` | `/issues/{issue_id}/return` | Return an issued book |

### Example requests

Create a book (`POST /books`):

```json
{
  "title": "The Hobbit",
  "author": "J. R. R. Tolkien",
  "category": "Fantasy"
}
```

Register a member (`POST /members`):

```json
{
  "full_name": "Asha Rao",
  "email": "asha@example.com",
  "phone": "555-0100"
}
```

Issue a book (`POST /issues`). `due_date` is optional and defaults to 14 days
after issue:

```json
{
  "book_id": 1,
  "member_id": 1,
  "due_date": "2026-11-20"
}
```

Return a book (`POST /issues/1/return`). The API uses today's date if the
optional body is omitted:

```json
{
  "return_date": "2026-11-23"
}
```

An issue response includes the issue and due dates, optional return date, and
`overdue_days`. Issue and return dates must not precede the relevant issue
date. A book with an active loan cannot be issued again. Deleting a book or
member with lending history returns HTTP `409` so that records remain intact.
Invalid request fields return HTTP `422`; unknown IDs return HTTP `404`.

## Test with Postman

1. Start the server and create a request in Postman using the URLs above.
2. Select **Body → raw → JSON** for `POST` and `PUT` requests with a request body.
3. Create a book and a member using the example JSON. Use their returned IDs
   in the issue request.
4. Issue the book, then return it at `POST /issues/{issue_id}/return`.
5. Use `GET /books`, `GET /members`, and `GET /issues` to verify the results.

## Run automated tests

With the virtual environment active and dependencies installed, run:

```powershell
python -m pytest
```

The tests use a fresh in-memory SQLite database and do not modify the persistent
`library.db` application data.
