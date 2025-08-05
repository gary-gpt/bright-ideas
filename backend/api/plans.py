"""
API routes for implementation plans - AI-generated plans based on refined ideas
"""
from fastapi import APIRouter, Depends, HTTPException, Response
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from uuid import UUID
import json

from database import get_db
from models import Idea, RefinementSession, Plan, IdeaStatus, PlanStatus
from schemas import (
    PlanCreate,
    PlanUpdate,
    PlanResponse,
    PlanExportResponse,
    PlanGenerationResponse
)
from services.ai_service import AIService

router = APIRouter(prefix="/plans", tags=["plans"])
ai_service = AIService()

@router.get("/ideas/{idea_id}", response_model=List[PlanResponse])
def get_idea_plans(
    idea_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Get all plans for a specific idea
    """
    # Verify idea exists
    idea = db.query(Idea).filter(Idea.id == idea_id).first()
    if not idea:
        raise HTTPException(status_code=404, detail="Idea not found")
    
    # Get plans for this idea, ordered by creation date (newest first)
    plans = db.query(Plan).filter(
        Plan.idea_id == idea_id
    ).order_by(Plan.created_at.desc()).all()
    
    return plans

@router.post("/generate/", response_model=PlanResponse)
async def generate_plan(
    request: Dict[str, Any],
    db: Session = Depends(get_db)
):
    """
    Generate an implementation plan from a completed refinement session
    """
    # Extract refinement_session_id from request body
    refinement_session_id = request.get("refinement_session_id")
    if not refinement_session_id:
        raise HTTPException(status_code=400, detail="refinement_session_id is required")
    
    try:
        refinement_session_id = UUID(refinement_session_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid refinement_session_id format")
    
    # Get the refinement session
    session = db.query(RefinementSession).filter(
        RefinementSession.id == refinement_session_id
    ).first()
    
    if not session:
        raise HTTPException(status_code=404, detail="Refinement session not found")
    
    if not session.is_complete:
        raise HTTPException(
            status_code=400, 
            detail="Refinement session must be completed before generating plan"
        )
    
    # Get the idea
    idea = session.idea
    
    try:
        # Generate plan using AI
        plan_data = await ai_service.generate_plan(
            title=idea.title,
            description=idea.original_description,
            answers=session.answers
        )
        
        # Convert steps and resources to JSON format
        steps_json = [
            {
                "order": step.order,
                "title": step.title,
                "description": step.description,
                "estimated_time": step.estimated_time
            }
            for step in plan_data["steps"]
        ]
        
        resources_json = [
            {
                "title": resource.title,
                "url": resource.url,
                "type": resource.type,
                "description": resource.description
            }
            for resource in plan_data["resources"]
        ]
        
        # Generate markdown content
        markdown_content = ai_service.generate_markdown(
            plan_data, 
            idea.title
        )
        
        # Create plan
        plan = Plan(
            idea_id=idea.id,
            refinement_session_id=refinement_session_id,
            summary=plan_data["summary"],
            steps=steps_json,
            resources=resources_json,
            status=PlanStatus.generated,
            content_markdown=markdown_content,
            is_active=False  # Not active by default
        )
        
        db.add(plan)
        
        # Update idea status to planned
        idea.status = IdeaStatus.planned
        
        db.commit()
        db.refresh(plan)
        
        return plan
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate plan: {str(e)}"
        )

@router.get("/{plan_id}", response_model=PlanResponse)
def get_plan(
    plan_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Get a specific plan
    """
    plan = db.query(Plan).filter(Plan.id == plan_id).first()
    
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    
    return plan

@router.get("/ideas/{idea_id}", response_model=List[PlanResponse])
def get_idea_plans(
    idea_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Get all plans for an idea
    """
    idea = db.query(Idea).filter(Idea.id == idea_id).first()
    if not idea:
        raise HTTPException(status_code=404, detail="Idea not found")
    
    plans = db.query(Plan).filter(
        Plan.idea_id == idea_id
    ).order_by(Plan.created_at.desc()).all()
    
    return plans

@router.put("/{plan_id}", response_model=PlanResponse)
def update_plan(
    plan_id: UUID,
    plan_update: PlanUpdate,
    db: Session = Depends(get_db)
):
    """
    Update an existing plan
    """
    plan = db.query(Plan).filter(Plan.id == plan_id).first()
    
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    
    # Update fields if provided
    if plan_update.summary is not None:
        plan.summary = plan_update.summary
    
    if plan_update.steps is not None:
        plan.steps = [
            {
                "order": step.order,
                "title": step.title,
                "description": step.description,
                "estimated_time": step.estimated_time
            }
            for step in plan_update.steps
        ]
    
    if plan_update.resources is not None:
        plan.resources = [
            {
                "title": resource.title,
                "url": resource.url,
                "type": resource.type,
                "description": resource.description
            }
            for resource in plan_update.resources
        ]
    
    if plan_update.status is not None:
        plan.status = PlanStatus(plan_update.status)
    
    # Regenerate markdown if content changed
    if any([plan_update.summary, plan_update.steps, plan_update.resources]):
        plan_data = {
            "summary": plan.summary,
            "steps": plan_update.steps or [
                type('obj', (object,), step)() for step in plan.steps
            ],
            "resources": plan_update.resources or [
                type('obj', (object,), resource)() for resource in plan.resources
            ]
        }
        plan.content_markdown = ai_service.generate_markdown(
            plan_data, 
            plan.idea.title
        )
    
    db.commit()
    db.refresh(plan)
    
    return plan

@router.post("/{plan_id}/activate", response_model=PlanResponse)
def activate_plan(
    plan_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Make this plan the active plan for its idea
    """
    plan = db.query(Plan).filter(Plan.id == plan_id).first()
    
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    
    # Use the model method to activate (deactivates others)
    plan.activate()
    
    db.commit()
    db.refresh(plan)
    
    return plan

@router.delete("/{plan_id}")
def delete_plan(
    plan_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Delete a plan
    """
    plan = db.query(Plan).filter(Plan.id == plan_id).first()
    
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    
    db.delete(plan)
    db.commit()
    
    return {"message": "Plan deleted successfully"}

@router.get("/{plan_id}/export/json")
def export_plan_json(
    plan_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Export plan as JSON
    """
    plan = db.query(Plan).filter(Plan.id == plan_id).first()
    
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    
    export_data = plan.to_export_dict()
    
    return JSONResponse(
        content=export_data,
        headers={
            "Content-Disposition": f"attachment; filename={plan.idea.title.replace(' ', '_')}_plan.json"
        }
    )

@router.get("/{plan_id}/export/markdown")
def export_plan_markdown(
    plan_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Export plan as Markdown
    """
    plan = db.query(Plan).filter(Plan.id == plan_id).first()
    
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    
    if not plan.content_markdown:
        raise HTTPException(
            status_code=400,
            detail="Plan does not have markdown content generated"
        )
    
    return Response(
        content=plan.content_markdown,
        media_type="text/markdown",
        headers={
            "Content-Disposition": f"attachment; filename={plan.idea.title.replace(' ', '_')}_plan.md"
        }
    )

@router.post("/test-generation/", response_model=PlanGenerationResponse)
async def test_plan_generation(
    request: Dict[str, Any],
    db: Session = Depends(get_db)
):
    """
    Test plan generation without creating a plan (for development/testing)
    """
    # Extract parameters from request body
    idea_id = request.get("idea_id")
    answers = request.get("answers", {})
    
    if not idea_id:
        raise HTTPException(status_code=400, detail="idea_id is required")
    
    try:
        idea_id = UUID(idea_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid idea_id format")
    
    idea = db.query(Idea).filter(Idea.id == idea_id).first()
    if not idea:
        raise HTTPException(status_code=404, detail="Idea not found")
    
    try:
        plan_data = await ai_service.generate_plan(
            title=idea.title,
            description=idea.original_description,
            answers=answers
        )
        
        return PlanGenerationResponse(
            summary=plan_data["summary"],
            steps=plan_data["steps"],
            resources=plan_data["resources"]
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to test plan generation: {str(e)}"
        )