from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from app.database import get_session
from app.auth.models import User
from app.auth.utils import get_current_user
from app.todos.models import Todo, TodoCreate, TodoUpdate

router = APIRouter()


@router.get("", response_model=List[Todo])
async def list_todos(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> List[Todo]:
    return session.exec(select(Todo).where(Todo.user_id == current_user.id)).all()


@router.post("", response_model=Todo, status_code=status.HTTP_201_CREATED)
async def create_todo(
    todo_in: TodoCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> Todo:
    todo = Todo(**todo_in.model_dump(), user_id=current_user.id)
    session.add(todo)
    session.commit()
    session.refresh(todo)
    return todo


@router.patch("/{todo_id}", response_model=Todo)
async def update_todo(
    todo_id: int,
    todo_in: TodoUpdate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> Todo:
    todo = session.get(Todo, todo_id)
    if not todo or todo.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Todo not found")

    update_data = todo_in.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(todo, key, value)

    session.add(todo)
    session.commit()
    session.refresh(todo)
    return todo


@router.delete("/{todo_id}")
async def delete_todo(
    todo_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> dict:
    todo = session.get(Todo, todo_id)
    if not todo or todo.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Todo not found")

    session.delete(todo)
    session.commit()
    return {"message": "Todo deleted successfully"}
