"""
Updated API routes for idea management - New Architecture
"""
from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func

from database import get_db
from models import Idea, RefinementSession, Plan, IdeaStatus
from schemas import (
    IdeaCreate, 
    IdeaUpdate, 
    IdeaResponse, 
    IdeaDetailResponse
)

router = APIRouter(prefix="/ideas", tags=["ideas"])

@router.post("/", response_model=IdeaResponse)
def create_idea(
    idea: IdeaCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new idea with the new architecture
    """
    import logging
    logger = logging.getLogger(__name__)
    
    logger.info(f"Creating new idea: {idea.title}")
    logger.info(f"Idea data: {idea.model_dump()}")
    logger.info(f"Tags - type: {type(idea.tags)}, value: {idea.tags}, repr: {repr(idea.tags)}")
    
    try:
        # Ensure tags is a proper list with explicit type guarantees
        tags = []
        if idea.tags:
            if isinstance(idea.tags, str):
                # Handle string input (should not happen with new schema, but safety first)
                try:
                    import json
                    parsed = json.loads(idea.tags)
                    tags = parsed if isinstance(parsed, list) else []
                except (json.JSONDecodeError, TypeError, AttributeError):
                    tags = []
            elif isinstance(idea.tags, list):
                # Ensure all items are strings
                tags = [str(tag).strip() for tag in idea.tags if tag and str(tag).strip()]
            else:
                tags = []
        
        logger.info(f"Final processed tags - type: {type(tags)}, value: {tags}, count: {len(tags)}")
        
        # Create new idea with explicit JSON-compatible data
        # Ensure tags is stored as proper Python list, not JSON string
        logger.info(f"Creating idea with tags as: {tags} (Python list)")
        
        db_idea = Idea(
            title=idea.title.strip(),
            original_description=idea.original_description.strip(),
            tags=tags,  # Pass as Python list - SQLAlchemy will handle JSON conversion
            status=IdeaStatus.captured
        )
        
        db.add(db_idea)
        db.commit()
        db.refresh(db_idea)
        
        logger.info(f"Successfully created idea with ID: {db_idea.id}")
        
        # Return with computed fields
        response = IdeaResponse(
            id=db_idea.id,
            title=db_idea.title,
            original_description=db_idea.original_description,
            tags=db_idea.tags,
            status=db_idea.status.value,
            created_at=db_idea.created_at,
            updated_at=db_idea.updated_at,
            refinement_sessions_count=0,
            plans_count=0,
            has_active_plan=False
        )
        
        return response
        
    except Exception as e:
        logger.error(f"Failed to create idea: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to create idea: {str(e)}")

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
    Get ideas with optional filtering and related data counts
    """
    query = db.query(Idea)
    
    # Apply filters
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            (Idea.title.ilike(search_term)) |
            (Idea.original_description.ilike(search_term))
        )
    
    if tags:
        # Filter by tags (JSON array contains any of the specified tags)
        for tag in tags:
            query = query.filter(func.json_array_length(Idea.tags.op('?')(tag)) > 0)
    
    if status:
        try:
            status_enum = IdeaStatus(status)
            query = query.filter(Idea.status == status_enum)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid status: {status}")
    
    # Order by most recent first
    query = query.order_by(Idea.updated_at.desc())
    
    # Apply pagination
    ideas = query.offset(skip).limit(limit).all()
    
    # Build response with computed fields (simplified for initial deployment)
    response_ideas = []
    for idea in ideas:
        # For now, return zero counts until the new tables are properly set up
        response_ideas.append(IdeaResponse(
            id=idea.id,
            title=idea.title,
            original_description=idea.original_description,
            tags=idea.tags,
            status=idea.status.value,
            created_at=idea.created_at,
            updated_at=idea.updated_at,
            refinement_sessions_count=0,
            plans_count=0,
            has_active_plan=False
        ))
    
    return response_ideas

@router.get("/stats")
def get_idea_stats(db: Session = Depends(get_db)):
    """
    Get statistics about ideas (simplified for initial deployment)
    """
    total_ideas = db.query(Idea).count()
    
    # Count by status
    status_counts = {}
    for status in IdeaStatus:
        count = db.query(Idea).filter(Idea.status == status).count()
        status_counts[status.value] = count
    
    # Simplified stats until all tables are set up
    return {
        "total_ideas": total_ideas,
        "status_counts": status_counts,
        "ideas_with_plans": 0,
        "total_refinement_sessions": 0,
        "completed_refinement_sessions": 0,
        "average_sessions_per_idea": 0.0
    }

@router.get("/recent", response_model=List[IdeaResponse])
def get_recent_ideas(
    limit: int = Query(5, ge=1, le=20),
    db: Session = Depends(get_db)
):
    """
    Get recently updated ideas with simplified response
    """
    # Get ideas with basic info
    ideas = db.query(Idea).order_by(
        Idea.updated_at.desc()
    ).limit(limit).all()
    
    response_ideas = []
    for idea in ideas:
        # For now, return zero counts until the new tables are properly set up
        # This prevents database query errors during the transition
        response_ideas.append(IdeaResponse(
            id=idea.id,
            title=idea.title,
            original_description=idea.original_description,
            tags=idea.tags,
            status=idea.status.value,
            created_at=idea.created_at,
            updated_at=idea.updated_at,
            refinement_sessions_count=0,
            plans_count=0,
            has_active_plan=False
        ))
    
    return response_ideas

@router.get("/{idea_id}", response_model=IdeaDetailResponse)
def get_idea(
    idea_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Get a specific idea with full related data
    """
    idea = db.query(Idea).filter(Idea.id == idea_id).first()
    
    if not idea:
        raise HTTPException(status_code=404, detail="Idea not found")
    
    # Build detailed response
    sessions_count = len(idea.refinement_sessions)
    plans_count = len(idea.plans)
    has_active_plan = idea.active_plan is not None
    
    response = IdeaDetailResponse(
        id=idea.id,
        title=idea.title,
        original_description=idea.original_description,
        tags=idea.tags,
        status=idea.status.value,
        created_at=idea.created_at,
        updated_at=idea.updated_at,
        refinement_sessions_count=sessions_count,
        plans_count=plans_count,
        has_active_plan=has_active_plan,
        latest_session=idea.latest_session,
        active_plan=idea.active_plan
    )
    
    return response

@router.put("/{idea_id}", response_model=IdeaResponse)
def update_idea(
    idea_id: UUID,
    idea_update: IdeaUpdate,
    db: Session = Depends(get_db)
):
    """
    Update an existing idea
    """
    idea = db.query(Idea).filter(Idea.id == idea_id).first()
    
    if not idea:
        raise HTTPException(status_code=404, detail="Idea not found")
    
    # Update fields if provided
    if idea_update.title is not None:
        idea.title = idea_update.title
    
    if idea_update.original_description is not None:
        idea.original_description = idea_update.original_description
    
    if idea_update.tags is not None:
        idea.tags = idea_update.tags
    
    if idea_update.status is not None:
        try:
            idea.status = IdeaStatus(idea_update.status)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid status: {idea_update.status}")
    
    db.commit()
    db.refresh(idea)
    
    # Return response with computed fields
    sessions_count = len(idea.refinement_sessions)
    plans_count = len(idea.plans)
    has_active_plan = idea.active_plan is not None
    
    return IdeaResponse(
        id=idea.id,
        title=idea.title,
        original_description=idea.original_description,
        tags=idea.tags,
        status=idea.status.value,
        created_at=idea.created_at,
        updated_at=idea.updated_at,
        refinement_sessions_count=sessions_count,
        plans_count=plans_count,
        has_active_plan=has_active_plan
    )

@router.delete("/{idea_id}")
def delete_idea(
    idea_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Delete an idea and all related data (cascading)
    """
    idea = db.query(Idea).filter(Idea.id == idea_id).first()
    
    if not idea:
        raise HTTPException(status_code=404, detail="Idea not found")
    
    db.delete(idea)  # Cascading deletes will handle related records
    db.commit()
    
    return {"message": "Idea deleted successfully"}

@router.get("/{idea_id}/summary")
def get_idea_summary(
    idea_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Get a comprehensive summary of an idea's progress through the system
    """
    idea = db.query(Idea).filter(Idea.id == idea_id).first()
    
    if not idea:
        raise HTTPException(status_code=404, detail="Idea not found")
    
    # Gather all related data
    sessions = idea.refinement_sessions
    plans = idea.plans
    active_plan = idea.active_plan
    
    summary = {
        "idea": {
            "id": str(idea.id),
            "title": idea.title,
            "description": idea.original_description,
            "status": idea.status.value,
            "tags": idea.tags,
            "created_at": idea.created_at.isoformat(),
            "updated_at": idea.updated_at.isoformat()
        },
        "refinement_progress": {
            "total_sessions": len(sessions),
            "completed_sessions": len([s for s in sessions if s.is_complete]),
            "latest_session": sessions[0] if sessions else None
        },
        "planning_progress": {
            "total_plans": len(plans),
            "has_active_plan": active_plan is not None,
            "active_plan_id": str(active_plan.id) if active_plan else None
        },
        "next_steps": _get_suggested_next_steps(idea)
    }
    
    return summary

def _get_suggested_next_steps(idea: Idea) -> List[str]:
    """
    Suggest next steps based on idea's current state
    """
    if idea.status == IdeaStatus.captured:
        return [
            "Start a refinement session to get AI-generated questions",
            "Add more descriptive tags to categorize your idea"
        ]
    elif idea.status == IdeaStatus.refining:
        incomplete_sessions = [s for s in idea.refinement_sessions if not s.is_complete]
        if incomplete_sessions:
            return [
                "Complete the current refinement session by answering all questions",
                "Generate an implementation plan from your completed answers"
            ]
        else:
            return [
                "Generate an implementation plan from your refinement session",
                "Start a new refinement session to explore different angles"
            ]
    elif idea.status == IdeaStatus.planned:
        if not idea.active_plan:
            return [
                "Activate one of your generated plans",
                "Export your plan to start implementation"
            ]
        else:
            return [
                "Export your active plan as JSON or Markdown",
                "Begin implementing the steps in your plan",
                "Create a new refinement session to explore variations"
            ]
    elif idea.status == IdeaStatus.archived:
        return [
            "Restore this idea to continue working on it",
            "Use it as inspiration for new ideas"
        ]
    
    return ["Continue developing your idea"]