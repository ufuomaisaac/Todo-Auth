from fastapi import FastAPI
from sqlmodel import SQLModel

from app.database import engine
from app.auth.routes import router as auth_router
from app.todos.routes import router as todos_router

app = FastAPI(title="Todo API")


@app.on_event("startup")
def on_startup() -> None:
    SQLModel.metadata.create_all(engine)


app.include_router(auth_router, prefix="/auth", tags=["Auth"])
app.include_router(todos_router, prefix="/todos", tags=["Todos"])
