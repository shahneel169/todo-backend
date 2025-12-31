# Mark all tests in this module as unit tests

from datetime import date

import pytest
from app.api.v1.endpoints import todos
from app.crud import todo as crud_todo
from app.models.todo import Todo
from app.schemas.todo import TodoCreate, TodoUpdate
from sqlalchemy.orm import Session
from tests.factories.todo_factory import TodoCreateFactory

pytestmark = pytest.mark.unit


class TestGetTodos:
    """Test suite for get_todos function"""

    def test_get_todos_empty_database(self, db_session: Session):
        """Should return empty list when no todos exist"""
        todos = crud_todo.get_todos(db_session)
        assert todos == []

    def test_get_todos_return_all_todos(self, db_session: Session):
        """Should return all todos from database"""
        # Arrage: create test todos
        todo1 = TodoCreateFactory.build(title="Todo 1")
        todo2 = TodoCreateFactory.build(title="Todo 2")

        crud_todo.create_todo(db_session, todo1)
        crud_todo.create_todo(db_session, todo2)

        todos = crud_todo.get_todos(db_session)

        assert len(todos) == 2
        assert str(todos[0].title) == "Todo 1"
        assert str(todos[1].title) == "Todo 2"


class TestGetTodo:
    """Test suit for get_todo function"""

    def test_get_todo_by_id_success(self, db_session: Session):
        "should return todo when valid id is provided"

        todo_data = TodoCreateFactory.build(title="Todo 1")
        created_todo = crud_todo.create_todo(db_session, todo_data)
        found_todo = crud_todo.get_todo(db_session, created_todo.id)  # type: ignore

        assert found_todo is not None
        assert found_todo.id == created_todo.id  # type: ignore
        assert str(found_todo.title) == todo_data.title

    def test_get_todo_not_found(self, db_session: Session):
        found_todo = crud_todo.get_todo(db_session, 999)

        assert found_todo is None


class TestCreateTodo:
    """Test suit for create_todo function"""

    def test_create_todo_success(self, db_session: Session):
        todo_data = TodoCreateFactory.build(title="Todo 1")
        created_todo = crud_todo.create_todo(db_session, todo_data)

        assert created_todo is not None
        assert str(created_todo.title) == "Todo 1"
        assert created_todo.completed is False
        assert created_todo.id is not None
        assert created_todo.created_at is not None
        assert created_todo.updated_at is not None

    def test_create_todo_with_due_date(self, db_session: Session):
        """Should create todo with due date"""
        todo_data = TodoCreateFactory.build(title="Todo 1", due_date="2026-01-01")

        created_todo = crud_todo.create_todo(db_session, todo_data)

        assert created_todo.due_date == date(2026, 1, 1)  # type: ignore

    def test_create_todo_with_invalid_due_date(self, db_session: Session):
        """Should raise ValidationError when due date is invalid"""
        from pydantic import ValidationError

        with pytest.raises(ValidationError):
            todo_data = TodoCreateFactory.build(title="Todo 1", due_date="invalid")

        assert db_session.query(Todo).filter(Todo.title == "Todo 1").count() == 0
        assert db_session.query(Todo).count() == 0


class TestUpdateTodo:
    "Test suite for update_todo function"

    def test_update_todo_title(self, db_session: Session):
        todo_data = TodoCreateFactory.build(title="Orignal title")
        created_todo = crud_todo.create_todo(db_session, todo_data)

        updated_todo_data = TodoUpdate(title="Updated title")

        updated_todo = crud_todo.update_todo(db_session, created_todo.id, updated_todo_data)  # type: ignore

        assert updated_todo is not None
        assert str(updated_todo.title) == "Updated title"
        assert updated_todo.id == created_todo.id  # type: ignore

    def test_update_todo_completed(self, db_session: Session):
        todo_data = TodoCreateFactory.build(title="Orignal title")
        created_todo = crud_todo.create_todo(db_session, todo_data)

        updated_todo_data = TodoUpdate(completed=True)

        updated_todo = crud_todo.update_todo(db_session, created_todo.id, updated_todo_data)  # type: ignore

        assert updated_todo is not None
        assert updated_todo.completed is True
        assert updated_todo.id == created_todo.id  # type: ignore

    def test_update_todo_partial_update(self, db_session: Session):
        todo_data = TodoCreateFactory.build(title="Orignal title", completed=False)

        created_todo = crud_todo.create_todo(db_session, todo_data)
        updated_todo_data = TodoUpdate(completed=True)
        updated_todo = crud_todo.update_todo(db_session, created_todo.id, updated_todo_data)  # type: ignore

        assert updated_todo is not None
        assert updated_todo.completed is True  # Changed
        assert str(updated_todo.title) == "Orignal title"  # Unchanged

    def test_update_nonexistent_todo(self, db_session: Session):
        """Should return None when updating non-existent todo"""
        updated_todo_data = TodoUpdate(title="Updated title")
        updated_todo = crud_todo.update_todo(db_session, 999, updated_todo_data)

        assert updated_todo is None


class TestDeleteTodo:
    """Test suite for delete_todo function"""

    def test_delete_todo_success(self, db_session: Session):
        todo_data = TodoCreateFactory.build(title="Todo 1")
        created_todo = crud_todo.create_todo(db_session, todo_data)

        deleted_todo = crud_todo.delete_todo(db_session, created_todo.id)  # type: ignore

        assert deleted_todo is not None
        assert deleted_todo.id == created_todo.id  # type: ignore

        found_todo = crud_todo.get_todo(db_session, created_todo.id)  # type: ignore
        assert found_todo is None

    def test_delete_nonexistent_todo(self, db_session: Session):
        """Should return None when deleting non-existent todo"""
        deleted_todo = crud_todo.delete_todo(db_session, 999)

        assert deleted_todo is None
