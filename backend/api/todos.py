"""
API routes for todo management
"""
from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func

from database import get_db
from models import Todo
from schemas import TodoCreate, TodoUpdate, TodoResponse

router = APIRouter(prefix="/todos", tags=["todos"])

@router.get("/", response_model=List[TodoResponse])
async def get_todos(
    completed: bool = None,
    db: Session = Depends(get_db)
):
    """Get all todos, optionally filtered by completion status"""
    query = db.query(Todo)
    
    if completed is not None:
        query = query.filter(Todo.is_completed == completed)
    
    todos = query.order_by(Todo.created_at.desc()).all()
    return todos

@router.post("/", response_model=TodoResponse, status_code=201)
async def create_todo(
    todo_data: TodoCreate,
    db: Session = Depends(get_db)
):
    """Create a new todo"""
    todo = Todo(text=todo_data.text)
    db.add(todo)
    db.commit()
    db.refresh(todo)
    return todo

@router.get("/{todo_id}", response_model=TodoResponse)
async def get_todo(
    todo_id: UUID,
    db: Session = Depends(get_db)
):
    """Get a specific todo by ID"""
    todo = db.query(Todo).filter(Todo.id == todo_id).first()
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    return todo

@router.put("/{todo_id}", response_model=TodoResponse)
async def update_todo(
    todo_id: UUID,
    todo_data: TodoUpdate,
    db: Session = Depends(get_db)
):
    """Update a todo"""
    todo = db.query(Todo).filter(Todo.id == todo_id).first()
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    
    if todo_data.text is not None:
        todo.text = todo_data.text
    if todo_data.is_completed is not None:
        todo.is_completed = todo_data.is_completed
    
    db.commit()
    db.refresh(todo)
    return todo

@router.post("/{todo_id}/complete", response_model=TodoResponse)
async def complete_todo(
    todo_id: UUID,
    db: Session = Depends(get_db)
):
    """Mark a todo as completed (and delete it since spec says checkboxes get deleted)"""
    todo = db.query(Todo).filter(Todo.id == todo_id).first()
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    
    # Delete the todo instead of marking complete since spec says they get deleted
    db.delete(todo)
    db.commit()
    return todo

@router.delete("/{todo_id}")
async def delete_todo(
    todo_id: UUID,
    db: Session = Depends(get_db)
):
    """Delete a todo"""
    todo = db.query(Todo).filter(Todo.id == todo_id).first()
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    
    db.delete(todo)
    db.commit()
    return {"message": "Todo deleted"}

@router.get("/stats/count")
async def get_todo_stats(db: Session = Depends(get_db)):
    """Get todo statistics"""
    total = db.query(func.count(Todo.id)).scalar()
    completed = db.query(func.count(Todo.id)).filter(Todo.is_completed == True).scalar()
    pending = total - completed
    
    return {
        "total": total,
        "completed": completed,
        "pending": pending
    }