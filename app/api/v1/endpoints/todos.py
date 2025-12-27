from app.schemas.todo import TodoUpdate
from app.schemas.todo import TodoCreate
from fastapi import APIRouter, Depends, HTTPException
from typing import List
from app.schemas.todo import TodoResponse
from app.crud import todo as crud_todo
from app.api.deps import get_db_session
from sqlalchemy.orm import Session

router = APIRouter()


@router.get("/", response_model=List[TodoResponse])
def get_todos(db: Session = Depends(get_db_session)):
    return crud_todo.get_todos(db)


@router.get("/{id}", response_model=TodoResponse)
def get_todo(id: int, db: Session = Depends(get_db_session)):
    db_todo = crud_todo.get_todo(db, id)

    if not db_todo:
        raise HTTPException(status=404, detail="Todo not found")
    return db_todo


@router.post("/", response_model=TodoResponse)
def create_todo(todo: TodoCreate, db: Session = Depends(get_db_session)):
    return crud_todo.create_todo(db, todo)


@router.put("/{id}", response_model=TodoResponse)
def update_todo(id: int, todo: TodoUpdate, db: Session = Depends(get_db_session)):
    db_todo = crud_todo.update_todo(db, id, todo)

    if not db_todo:
        raise HTTPException(status=404, detail="Todo not found")
    return db_todo


@router.delete("/{id}")
def delete_todo(id: int, db: Session = Depends(get_db_session)):
    db_todo = crud_todo.delete_todo(db, id)

    if not db_todo:
        raise HTTPException(status=404, detail="Todo not found")
    return {"message": "Todo deleted successfully"}
