"""
API routes for idea management.
"""
from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from database import get_db
from schemas import IdeaCreate, IdeaUpdate, IdeaResponse
from services.idea_service import IdeaService

router = APIRouter(prefix="/ideas", tags=["ideas"])


@router.post("/", response_model=IdeaResponse)
def create_idea(
    idea: IdeaCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new idea.
    
    Args:
        idea: Idea creation data
        db: Database session
        
    Returns:
        Created idea
    """
    service = IdeaService(db)
    db_idea = service.create_idea(idea)
    return db_idea


@router.get("/", response_model=List[IdeaResponse])
def get_ideas(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    search: Optional[str] = Query(None),
    tags: Optional[List[str]] = Query(None),
    status: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """
    Get ideas with optional filtering.
    
    Args:
        skip: Number of records to skip
        limit: Maximum number of records to return
        search: Search term for title and description
        tags: Filter by tags
        status: Filter by status
        db: Database session
        
    Returns:
        List of ideas
    """
    service = IdeaService(db)
    ideas = service.get_ideas(
        skip=skip,
        limit=limit,
        search=search,
        tags=tags,
        status=status
    )
    return ideas


@router.get("/stats")
def get_idea_stats(db: Session = Depends(get_db)):
    """
    Get statistics about ideas.
    
    Args:
        db: Database session
        
    Returns:
        Idea statistics
    """
    service = IdeaService(db)
    return service.get_idea_stats()


@router.get("/recent", response_model=List[IdeaResponse])
def get_recent_ideas(
    limit: int = Query(5, ge=1, le=20),
    db: Session = Depends(get_db)
):
    """
    Get recently updated ideas.
    
    Args:
        limit: Maximum number of ideas to return
        db: Database session
        
    Returns:
        List of recent ideas
    """
    service = IdeaService(db)
    return service.get_recent_ideas(limit=limit)


@router.get("/{idea_id}", response_model=IdeaResponse)
def get_idea(
    idea_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Get a specific idea by ID.
    
    Args:
        idea_id: UUID of the idea
        db: Database session
        
    Returns:
        Idea details
    """
    service = IdeaService(db)
    db_idea = service.get_idea(idea_id)
    
    if not db_idea:
        raise HTTPException(status_code=404, detail="Idea not found")
    
    return db_idea


@router.put("/{idea_id}", response_model=IdeaResponse)
def update_idea(
    idea_id: UUID,
    idea_update: IdeaUpdate,
    db: Session = Depends(get_db)
):
    """
    Update an existing idea.
    
    Args:
        idea_id: UUID of the idea to update
        idea_update: Updated idea data
        db: Database session
        
    Returns:
        Updated idea
    """
    service = IdeaService(db)
    db_idea = service.update_idea(idea_id, idea_update)
    
    if not db_idea:
        raise HTTPException(status_code=404, detail="Idea not found")
    
    return db_idea


@router.delete("/{idea_id}")
def delete_idea(
    idea_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Delete an idea and all related data.
    
    Args:
        idea_id: UUID of the idea to delete
        db: Database session
        
    Returns:
        Success message
    """
    service = IdeaService(db)
    success = service.delete_idea(idea_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Idea not found")
    
    return {"message": "Idea deleted successfully"}