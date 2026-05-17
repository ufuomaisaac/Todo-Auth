from typing import Optional
from sqlmodel import Field, SQLModel


class Todo(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    description: Optional[str] = None
    completed: bool = False
    user_id: int = Field(foreign_key="user.id")


class TodoCreate(SQLModel):
    title: str
    description: Optional[str] = None


class TodoUpdate(SQLModel):
    title: Optional[str] = None
    description: Optional[str] = None
    completed: Optional[bool] = None
