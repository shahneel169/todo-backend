# FastAPI Todo Backend - Implementation Guide

## Progress Tracker

- [ ] Phase 1: Environment Setup
- [ ] Phase 2: Core Configuration
- [ ] Phase 3: Database Models
- [ ] Phase 4: Pydantic Schemas
- [ ] Phase 5: CRUD Operations
- [ ] Phase 6: API Endpoints
- [ ] Phase 7: Main Application
- [ ] Phase 8: Database Setup & Testing

---

## Phase 1: Environment Setup 🔧

### Step 1: Create `requirements.txt` ✅

**Location**: `todo-be/requirements.txt`

```txt
fastapi>=0.115.0
uvicorn[standard]>=0.32.0
python-dotenv>=1.0.0
sqlalchemy>=2.0.0
alembic>=1.13.0
psycopg2-binary>=2.9.9
pydantic>=2.10.0
pydantic-settings>=2.6.0
```

- [ ] File created
- [ ] Dependencies listed

### Step 2: Install Dependencies

**Commands**:

```bash
cd todo-be
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

- [ ] Virtual environment created
- [ ] Virtual environment activated
- [ ] Dependencies installed

### Step 3: Create `.env` file

**Location**: `todo-be/.env`

```env
DATABASE_URL=postgresql://username:password@localhost:5432/todo_db
PROJECT_NAME=Todo API
DEBUG=True
```

- [ ] File created
- [ ] Database URL configured
- [ ] Project name set

### Step 4: Create `.gitignore`

**Location**: `todo-be/.gitignore`

```
venv/
__pycache__/
*.pyc
.env
*.db
.pytest_cache/
```

- [ ] File created
- [ ] Sensitive files excluded

---

## Phase 2: Core Configuration ⚙️

### Step 5: Create `app/core/config.py`

**Location**: `todo-be/app/core/config.py`

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str
    DATABASE_URL: str
    DEBUG: bool = False

    class Config:
        env_file = ".env"

settings = Settings()
```

- [ ] File created
- [ ] Settings class defined
- [ ] Environment variables configured

### Step 6: Create `app/core/database.py`

**Location**: `todo-be/app/core/database.py`

```python
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from .config import settings

engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

- [ ] File created
- [ ] Database engine configured
- [ ] Session factory created
- [ ] Dependency injection function defined

---

## Phase 3: Database Models 🗄️

### Step 7: Create `app/models/todo.py`

**Location**: `todo-be/app/models/todo.py`

```python
from sqlalchemy import Column, Integer, String, Boolean, Date
from app.core.database import Base

class Todo(Base):
    __tablename__ = "todos"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    completed = Column(Boolean, default=False)
    due_date = Column(String, nullable=True)
```

- [ ] File created
- [ ] Todo model defined
- [ ] Table columns configured

### Step 8: Update `app/models/__init__.py`

**Location**: `todo-be/app/models/__init__.py`

```python
from .todo import Todo
```

- [ ] File updated
- [ ] Todo model exported

---

## Phase 4: Pydantic Schemas 📋

### Step 9: Create `app/schemas/todo.py`

**Location**: `todo-be/app/schemas/todo.py`

```python
from pydantic import BaseModel
from typing import Optional

class TodoBase(BaseModel):
    title: str
    completed: bool = False
    due_date: Optional[str] = None

class TodoCreate(TodoBase):
    pass

class TodoUpdate(BaseModel):
    title: Optional[str] = None
    completed: Optional[bool] = None
    due_date: Optional[str] = None

class TodoResponse(TodoBase):
    id: int

    class Config:
        from_attributes = True
```

- [ ] File created
- [ ] Base schema defined
- [ ] Create schema defined
- [ ] Update schema defined
- [ ] Response schema defined

### Step 10: Update `app/schemas/__init__.py`

**Location**: `todo-be/app/schemas/__init__.py`

```python
from .todo import TodoCreate, TodoUpdate, TodoResponse
```

- [ ] File updated
- [ ] Schemas exported

---

## Phase 5: CRUD Operations 💾

### Step 11: Create `app/crud/todo.py`

**Location**: `todo-be/app/crud/todo.py`

```python
from sqlalchemy.orm import Session
from app.models.todo import Todo
from app.schemas.todo import TodoCreate, TodoUpdate

def get_todos(db: Session):
    return db.query(Todo).all()

def get_todo(db: Session, todo_id: int):
    return db.query(Todo).filter(Todo.id == todo_id).first()

def create_todo(db: Session, todo: TodoCreate):
    db_todo = Todo(**todo.model_dump())
    db.add(db_todo)
    db.commit()
    db.refresh(db_todo)
    return db_todo

def update_todo(db: Session, todo_id: int, todo: TodoUpdate):
    db_todo = db.query(Todo).filter(Todo.id == todo_id).first()
    if db_todo:
        for key, value in todo.model_dump(exclude_unset=True).items():
            setattr(db_todo, key, value)
        db.commit()
        db.refresh(db_todo)
    return db_todo

def delete_todo(db: Session, todo_id: int):
    db_todo = db.query(Todo).filter(Todo.id == todo_id).first()
    if db_todo:
        db.delete(db_todo)
        db.commit()
    return db_todo
```

- [ ] File created
- [ ] Get all todos function
- [ ] Get single todo function
- [ ] Create todo function
- [ ] Update todo function
- [ ] Delete todo function

---

## Phase 6: API Endpoints 🌐

### Step 12: Create `app/api/deps.py`

**Location**: `todo-be/app/api/deps.py`

```python
from typing import Generator
from sqlalchemy.orm import Session
from app.core.database import get_db

def get_db_session() -> Generator:
    return get_db()
```

- [ ] File created
- [ ] Database dependency defined

### Step 13: Create `app/api/v1/endpoints/todos.py`

**Location**: `todo-be/app/api/v1/endpoints/todos.py`

```python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.crud import todo as crud_todo
from app.schemas.todo import TodoCreate, TodoUpdate, TodoResponse
from app.api.deps import get_db_session

router = APIRouter()

@router.get("/", response_model=List[TodoResponse])
def get_todos(db: Session = Depends(get_db_session)):
    return crud_todo.get_todos(db)

@router.post("/", response_model=TodoResponse)
def create_todo(todo: TodoCreate, db: Session = Depends(get_db_session)):
    return crud_todo.create_todo(db, todo)

@router.get("/{todo_id}", response_model=TodoResponse)
def get_todo(todo_id: int, db: Session = Depends(get_db_session)):
    db_todo = crud_todo.get_todo(db, todo_id)
    if not db_todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    return db_todo

@router.put("/{todo_id}", response_model=TodoResponse)
def update_todo(todo_id: int, todo: TodoUpdate, db: Session = Depends(get_db_session)):
    db_todo = crud_todo.update_todo(db, todo_id, todo)
    if not db_todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    return db_todo

@router.delete("/{todo_id}")
def delete_todo(todo_id: int, db: Session = Depends(get_db_session)):
    db_todo = crud_todo.delete_todo(db, todo_id)
    if not db_todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    return {"message": "Todo deleted successfully"}
```

- [ ] File created
- [ ] GET all todos endpoint
- [ ] POST create todo endpoint
- [ ] GET single todo endpoint
- [ ] PUT update todo endpoint
- [ ] DELETE todo endpoint

### Step 14: Create `app/api/v1/router.py`

**Location**: `todo-be/app/api/v1/router.py`

```python
from fastapi import APIRouter
from app.api.v1.endpoints import todos

api_router = APIRouter()
api_router.include_router(todos.router, prefix="/todos", tags=["todos"])
```

- [ ] File created
- [ ] Router aggregated

---

## Phase 7: Main Application 🚀

### Step 15: Create `app/main.py`

**Location**: `todo-be/app/main.py`

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.database import engine, Base
from app.api.v1.router import api_router

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title=settings.PROJECT_NAME)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Your React app URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(api_router, prefix="/api/v1")

@app.get("/")
def root():
    return {"message": "Todo API is running"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}
```

- [ ] File created
- [ ] FastAPI app initialized
- [ ] CORS configured
- [ ] Routes included
- [ ] Health check endpoint added

---

## Phase 8: Database Setup & Testing 🗃️

### Step 16: Install PostgreSQL

**Tasks**:

1. Download PostgreSQL from https://www.postgresql.org/download/
2. Install PostgreSQL
3. Create database:
   ```sql
   CREATE DATABASE todo_db;
   ```
4. Update `.env` with your credentials

- [ ] PostgreSQL installed
- [ ] Database created
- [ ] Credentials updated in `.env`

### Step 17: Run the Application

**Commands**:

```bash
uvicorn app.main:app --reload
```

**Test URLs**:

- API Docs: http://localhost:8000/docs
- Root: http://localhost:8000/
- Health: http://localhost:8000/health

- [ ] Application running
- [ ] API docs accessible
- [ ] Endpoints tested

---

## API Endpoints Testing Checklist

### Test at `http://localhost:8000/docs`

- [ ] **POST** `/api/v1/todos/` - Create a todo
- [ ] **GET** `/api/v1/todos/` - Get all todos
- [ ] **GET** `/api/v1/todos/{id}` - Get specific todo
- [ ] **PUT** `/api/v1/todos/{id}` - Update todo
- [ ] **DELETE** `/api/v1/todos/{id}` - Delete todo

---

## Quick Reference Commands

### Virtual Environment

```bash
# Activate
venv\Scripts\activate  # Windows
source venv/bin/activate  # Mac/Linux

# Deactivate
deactivate
```

### Run Application

```bash
uvicorn app.main:app --reload
```

### Database Migrations (Optional - Advanced)

```bash
alembic init alembic
alembic revision --autogenerate -m "Initial migration"
alembic upgrade head
```

---

## Notes & Tips

- Always activate virtual environment before working
- Check `.env` file for correct database credentials
- Use `/docs` endpoint for interactive API testing
- Keep this file updated as you complete each step
- Commit your code regularly to Git

---

**Happy Coding! 🚀**
