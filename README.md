# JobTrack API

A production-style Job Application and Interview Tracking REST API built with Python, FastAPI, SQLAlchemy, and MySQL.

## Features

### Authentication
- User registration
- Secure password hashing with Argon2
- JWT authentication
- Protected API endpoints
- User-specific application ownership

### Applications
- Create, read, update, and delete applications
- Status tracking:
  - Applied
  - Interview
  - Rejected
  - Offer
  - Accepted
- Search by company or role
- Filter by status, company, and role
- Pagination with limit and offset
- Sorting by ID, company, role, status, created time, and updated time
- Duplicate application protection
- Created and updated timestamps

### Dashboard
- Total application count
- Status-based statistics
- Five most recently updated applications

### Status History
- Automatically records status changes
- View the complete status timeline for an application

### Interviews
- Create and manage interviews
- Interview rounds
- Interview date and time
- Notes
- Interview result
- Upcoming interview endpoint
- User ownership protection
- Cascade deletion when an application is deleted

### Testing
- Pytest test suite
- In-memory SQLite test database
- CRUD tests
- Duplicate protection tests
- Status history tests
- User ownership/security tests
- Interview tests

## Tech Stack

- Python 3.13
- FastAPI
- SQLAlchemy
- MySQL
- PyMySQL
- Pydantic
- JWT
- Argon2 password hashing
- Pytest
- HTTPX
- Uvicorn

## Project Structure

```text
Jobtrack-api/
│
├── app/
│   ├── core/
│   │   ├── dependencies.py
│   │   ├── jwt.py
│   │   └── security.py
│   │
│   ├── routers/
│   │   ├── application.py
│   │   ├── interview.py
│   │   └── user.py
│   │
│   ├── schemas/
│   │   ├── application.py
│   │   ├── interview.py
│   │   ├── status.py
│   │   └── user.py
│   │
│   ├── database.py
│   ├── models.py
│   └── main.py
│
├── tests/
│   ├── conftest.py
│   ├── test_application.py
│   └── test_interview.py
│
├── .env
├── .gitignore
├── pytest.ini
├── requirements.txt
└── README.md