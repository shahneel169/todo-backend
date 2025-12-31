from turtle import update

import pytest
from app.crud import todo as crud_todo
from fastapi.testclient import TestClient
from httpx import get
from sqlalchemy.orm import Session
from tests.factories.todo_factory import TodoCreateFactory

# Mark all tests in this module as integration tests
pytestmark = pytest.mark.integration


class TestGetTodosEndpoint:
    """Test suite for GET /api/v1/todos endpoint"""

    def test_get_todos_empty(self, client: TestClient):
        """Should return empty array when no todo exists"""
        response = client.get("/api/v1/todos")

        assert response.status_code == 200
        assert response.json() == []

    def test_get_todos_returns_all(self, client: TestClient, db_session: Session):
        """Should return all todos with correct structure"""

        todo1 = TodoCreateFactory.build(title="todo 1")
        todo2 = TodoCreateFactory.build(title="todo 2")

        crud_todo.create_todo(db_session, todo1)
        crud_todo.create_todo(db_session, todo2)

        response = client.get("/api/v1/todos")
        data = response.json()
        assert response.status_code == 200
        assert len(response.json()) == 2
        assert data[0]["title"] == todo1.title
        assert data[1]["title"] == todo2.title

        assert "id" in data[0]
        assert "created_at" in data[0]
        assert "updated_at" in data[0]


class TestGetTodoEndpoint:
    """Test suite for GET /api/v1/todos/{id} endpoint"""

    def test_get_todo_by_id_success(self, client: TestClient, db_session: Session):
        """Should return todo with correct structure"""

        todo = TodoCreateFactory.build(title="todo 1")
        created_todo = crud_todo.create_todo(db_session, todo)

        response = client.get(f"/api/v1/todos/{created_todo.id}")
        data = response.json()

        assert response.status_code == 200
        assert data["id"] == created_todo.id
        assert data["title"] == "todo 1"

    def test_get_todo_not_found(self, client: TestClient):
        response = client.get("/api/v1/todos/999")

        assert response.status_code == 404
        assert response.json()["detail"] == "Todo not found"


class TestCreateTodoEndpoint:
    """Test suite for POST /api/v1/todos endpoint"""

    def test_create_todo_sucess(self, client: TestClient):
        todo_data = {"title": "todo 1", "completed": False, "due_date": "2025-12-31"}

        response = client.post(
            "/api/v1/todos",
            json=todo_data,
        )

        data = response.json()

        assert response.status_code == 200
        assert data["title"] == "todo 1"
        assert data["completed"] == False
        assert data["due_date"] == "2025-12-31"
        assert "id" in data
        assert data["id"] is not None

    def test_create_todo_minimal_fields(self, client: TestClient):
        """Should create todo with only required fields"""
        # Arrange
        todo_data = {"title": "Minimal todo"}

        # Act
        response = client.post("/api/v1/todos/", json=todo_data)

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Minimal todo"
        assert data["completed"] is False  # Default value
        assert data["due_date"] is None  # Optional field

    def test_create_todo_validation_error(self, client: TestClient):
        """Should return 422 when required fields are missing"""
        # Arrange: Missing required 'title' field
        todo_data = {"completed": False}

        # Act
        response = client.post("/api/v1/todos/", json=todo_data)

        # Assert
        assert response.status_code == 422


class TestUpdateTodoEndpoint:
    """Test suite for PUT /api/v1/todos/{id} endpoint"""

    def test_update_todo_success(self, client: TestClient, db_session: Session):
        """Should update todo and return updated version"""

        todo_data = TodoCreateFactory.build(title="todo 1")
        created_todo = crud_todo.create_todo(db_session, todo_data)

        update_data = {
            "title": "Updated via API",
            "completed": True,
        }

        response = client.put(
            f"/api/v1/todos/{created_todo.id}",
            json=update_data,
        )

        data = response.json()

        assert response.status_code == 200
        assert data["title"] == "Updated via API"
        assert data["completed"] is True

    def test_update_todo_partial(self, client: TestClient, db_session: Session):
        """Should update only provided fields"""
        # Arrange
        todo_data = TodoCreateFactory.build(title="Original", completed=False)
        created_todo = crud_todo.create_todo(db_session, todo_data)

        # Only update completed status
        update_data = {"completed": True}

        # Act
        response = client.put(f"/api/v1/todos/{created_todo.id}", json=update_data)

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Original"  # Unchanged
        assert data["completed"] is True  # Changed

    def test_update_todo_not_found(self, client: TestClient):
        """Should return 404 when todo not found"""
        # Arrange
        update_data = {"title": "Updated via API", "completed": True}

        # Act
        response = client.put("/api/v1/todos/999", json=update_data)

        # Assert
        assert response.status_code == 404
        assert response.json()["detail"] == "Todo not found"


class TestDeleteTodoEndpoint:
    """Test suite for DELETE /api/v1/todos/{id} endpoint"""

    def test_delete_todo_success(self, client: TestClient, db_session: Session):
        """Should delete todo and return success message"""
        # Arrange
        todo_data = TodoCreateFactory.build(title="To delete")
        created_todo = crud_todo.create_todo(db_session, todo_data)
        todo_id = created_todo.id

        # Act
        response = client.delete(f"/api/v1/todos/{todo_id}")

        # Assert
        assert response.status_code == 200
        assert response.json()["message"] == "Todo deleted successfully"

        # Verify it's actually deleted
        get_response = client.get(f"/api/v1/todos/{todo_id}")
        assert get_response.status_code == 404

    def test_delete_todo_not_found(self, client: TestClient):
        """Should return 404 when deleting non-existent todo"""
        # Act
        response = client.delete("/api/v1/todos/999")

        # Assert
        assert response.status_code == 404
        assert response.json()["detail"] == "Todo not found"


class TestTodoEndToEnd:
    """End-to-end test scenarios"""

    def test_complete_todo_workflow(self, client: TestClient):
        """Test complete CRUD workflow"""
        # 1. Create a todo
        todo_data = {"title": "Test todo", "completed": False}
        create_response = client.post("/api/v1/todos/", json=todo_data)
        assert create_response.status_code == 200
        todo_id = create_response.json()["id"]

        # 2. Get todo by id
        get_response = client.get(f"/api/v1/todos/{todo_id}")
        assert get_response.status_code == 200
        assert get_response.json()["title"] == "Test todo"

        # 3. Update todo
        update_response = client.put(
            f"/api/v1/todos/{todo_id}",
            json={"completed": True},
        )

        assert update_response.status_code == 200
        assert update_response.json()["completed"] is True

        # 4. Delete the todo
        delete_response = client.delete(f"/api/v1/todos/{todo_id}")

        assert delete_response.status_code == 200

        # 5. Verify todo deletion
        get_response = client.get(f"/api/v1/todos/{todo_id}")
        assert get_response.status_code == 404
