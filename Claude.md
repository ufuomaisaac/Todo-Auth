# CLAUDE.md — Todo App with Auth

This file gives you everything you need to work on this project. Read it fully before writing any code.

---

## Project Overview

A REST API for a Todo application with user authentication. Users can register, log in, and manage their own todos. Each user can only see and modify their own todos.

**Stack:**
- **Language:** Python 3.11+
- **Framework:** FastAPI
- **Database:** SQLite (via SQLModel)
- **Auth:** JWT (JSON Web Tokens) using `python-jose`
- **Password Hashing:** `bcrypt`
- **Server:** `uvicorn`
- **Config:** `python-dotenv`

---

## Project Structure

Strictly follow this feature-based structure. Do not create files or folders outside of it without asking first.

```
todo-app/
├── app/
│   ├── __init__.py
│   ├── database.py          # Shared DB engine and session
│   ├── auth/
│   │   ├── __init__.py
│   │   ├── models.py        # User SQLModel table + Pydantic schemas
│   │   ├── routes.py        # POST /auth/register, POST /auth/login
│   │   └── utils.py         # Password hashing, JWT creation & verification
│   └── todos/
│       ├── __init__.py
│       ├── models.py        # Todo SQLModel table + Pydantic schemas
│       └── routes.py        # GET, POST, PATCH, DELETE /todos
├── venv/
├── main.py                  # App entry point — mounts all routers
└── .env                     # Secret keys — never commit this
```

---

## Environment Variables

Always load config from `.env` using `python-dotenv`. Never hardcode secrets.

Required `.env` keys:
```
SECRET_KEY=<long-random-string>
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

Load them like this:
```python
from dotenv import load_dotenv
import os

load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY")
```

---

## Database Rules

- Use **SQLModel** for all models — it combines SQLAlchemy and Pydantic in one class.
- Database file is `todo.db` in the root directory.
- The engine and `get_session` dependency live exclusively in `app/database.py`.
- Call `SQLModel.metadata.create_all(engine)` once on startup in `main.py`.
- Use FastAPI's `Depends(get_session)` for DB access in routes — never create sessions manually inside route functions.

```python
# app/database.py
from sqlmodel import SQLModel, create_engine, Session
from typing import Generator

DATABASE_URL = "sqlite:///./todo.db"
engine = create_engine(DATABASE_URL, echo=False)

def get_session() -> Generator:
    with Session(engine) as session:
        yield session
```

---

## Auth Rules

### Password Hashing (`app/auth/utils.py`)
- Always hash passwords with `bcrypt` before saving to the DB.
- Never store or log plain text passwords anywhere.

```python
from passlib.context import CryptContext
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)
```

### JWT (`app/auth/utils.py`)
- Issue a JWT on successful login.
- Token payload must include `sub` (the user's email) and `exp` (expiry).
- Verification extracts the user from the token — no DB lookup needed for identity.

### Protected Routes
- Create a `get_current_user` dependency in `app/auth/utils.py`.
- All todo routes must use `Depends(get_current_user)`.
- Never expose another user's todos — always filter by `current_user.id`.

---

## Models

### User (`app/auth/models.py`)
Define three things in this file:
1. `User` — the SQLModel table (stored in DB)
2. `UserCreate` — Pydantic schema for registration input (email + password)
3. `UserRead` — Pydantic schema for responses (never include password)

### Todo (`app/todos/models.py`)
Define three things:
1. `Todo` — the SQLModel table, with a `user_id` foreign key to `User`
2. `TodoCreate` — input schema (title, optional description)
3. `TodoUpdate` — update schema (all fields optional — use `Optional`)

---

## API Endpoints

### Auth Routes — prefix: `/auth`
| Method | Path | Body | Response | Auth Required |
|--------|------|------|----------|---------------|
| POST | `/auth/register` | `UserCreate` | `UserRead` | No |
| POST | `/auth/login` | `email`, `password` (form) | `{ access_token, token_type }` | No |

### Todo Routes — prefix: `/todos`
| Method | Path | Body | Response | Auth Required |
|--------|------|------|----------|---------------|
| GET | `/todos` | — | `List[Todo]` | Yes |
| POST | `/todos` | `TodoCreate` | `Todo` | Yes |
| PATCH | `/todos/{id}` | `TodoUpdate` | `Todo` | Yes |
| DELETE | `/todos/{id}` | — | `{ message }` | Yes |

---

## Coding Conventions

- **Always use `async def`** for route functions.
- **Return meaningful HTTP status codes:**
  - `201` for resource creation
  - `404` when a resource is not found
  - `401` for unauthorized access
  - `400` for bad input (e.g. email already registered)
- **Raise exceptions using FastAPI's `HTTPException`** — never return raw error strings.
- **Keep route functions thin** — logic (hashing, token creation) belongs in `utils.py`, not in routes.
- **Type everything** — all function parameters and return types must be typed.
- Use **f-strings** for string formatting, never `.format()` or `%`.

---

## Response Consistency

All success responses should be the relevant Pydantic model or a simple dict:
```python
return {"message": "Todo deleted successfully"}
```

All error responses should use `HTTPException`:
```python
raise HTTPException(status_code=404, detail="Todo not found")
```

---

## main.py Rules

`main.py` only does four things:
1. Creates the FastAPI app instance
2. Calls `SQLModel.metadata.create_all(engine)` on startup
3. Includes the auth router with prefix `/auth`
4. Includes the todos router with prefix `/todos`

No business logic lives here.

```python
from fastapi import FastAPI
from sqlmodel import SQLModel
from app.database import engine
from app.auth.routes import router as auth_router
from app.todos.routes import router as todos_router

app = FastAPI(title="Todo API")

@app.on_event("startup")
def on_startup():
    SQLModel.metadata.create_all(engine)

app.include_router(auth_router, prefix="/auth", tags=["Auth"])
app.include_router(todos_router, prefix="/todos", tags=["Todos"])
```

---

## Build Order

Follow this order strictly. Do not jump ahead — each step depends on the previous.

- [ ] 1. `app/database.py` — engine and session
- [ ] 2. `app/auth/models.py` — User table + schemas
- [ ] 3. `app/todos/models.py` — Todo table + schemas
- [ ] 4. `app/auth/utils.py` — hashing + JWT logic
- [ ] 5. `app/auth/routes.py` — register + login
- [ ] 6. `app/todos/routes.py` — full CRUD
- [ ] 7. `main.py` — wire everything together
- [ ] 8. Run and test via `http://localhost:8000/docs`

---

## Hard Rules (Never Break These)

- **Never commit `.env`** — add it to `.gitignore` immediately.
- **Never store plain text passwords.**
- **Never return a User object that includes the password field.**
- **Never install a new package without flagging it** — ask first, then run `pip install` and update a `requirements.txt`.
- **Never put logic in `main.py`** beyond wiring routers.
- **Never access the DB directly in a route** — always use `Depends(get_session)`.
- **Never expose todos from another user** — always filter by `current_user.id`.

---

## Running the App

```bash
# Activate virtual environment first
source venv/bin/activate       # Mac/Linux
venv\Scripts\activate          # Windows

# Start the server
uvicorn main:app --reload
```

Visit `http://localhost:8000/docs` to test all endpoints interactively.

---

## Generating requirements.txt

After all packages are installed, run:
```bash
pip freeze > requirements.txt
```

This lets anyone else clone the project and install the same dependencies with:
```bash
pip install -r requirements.txt
```