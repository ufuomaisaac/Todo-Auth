from sqlmodel import SQLModel, create_engine, Session
from typing import Generator

DATABASE_URL = "sqlite:///./todo.db"
engine = create_engine(DATABASE_URL, echo=False)


def get_session() -> Generator:
    with Session(engine) as session:
        yield session
