from sqlalchemy import Column, Integer, String, Boolean, Date
from app.core.database import Base
from app.models.base import TimeStampMixin


class Todo(Base, TimeStampMixin):
    __tablename__ = "todos"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    completed = Column(Boolean, default=False)
    due_date = Column(Date, nullable=True)
