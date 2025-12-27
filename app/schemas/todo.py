from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel


class TodoBase(BaseModel):
    title: str
    completed: bool = False
    due_date: Optional[date] = None


class TodoCreate(TodoBase):
    pass


class TodoUpdate(BaseModel):
    title: Optional[str] = None
    completed: Optional[bool] = None
    due_date: Optional[date] = None


class TodoResponse(TodoBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
