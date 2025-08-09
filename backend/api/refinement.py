"""
API routes for refinement sessions - AI-generated questions and answers
"""
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from uuid import UUID

from database import get_db
from models import Idea, RefinementSession, IdeaStatus
from schemas import (
    RefinementSessionCreate,
    RefinementSessionResponse,
    RefinementAnswersSubmit,
    QuestionGenerationResponse
)
from services.ai_service import AIService

router = APIRouter(prefix="/refinement", tags=["refinement"])
ai_service = AIService()

@router.post("/sessions/", response_model=RefinementSessionResponse)
async def create_refinement_session(
    session_data: RefinementSessionCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new refinement session with AI-generated questions
    """
    # Get the idea
    idea = db.query(Idea).filter(Idea.id == session_data.idea_id).first()
    if not idea:
        raise HTTPException(status_code=404, detail="Idea not found")
    
    # Get previous context for continuation
    previous_sessions = db.query(RefinementSession).filter(
        RefinementSession.idea_id == session_data.idea_id,
        RefinementSession.is_complete == True
    ).order_by(RefinementSession.created_at.desc()).all()
    
    previous_plans = []
    if idea.active_plan:
        previous_plans = [idea.active_plan]
    
    # Generate questions using AI with context
    try:
        questions = await ai_service.generate_refinement_questions(
            title=idea.title,
            description=idea.original_description,
            previous_sessions=previous_sessions,
            previous_plans=previous_plans
        )
        
        # Convert to JSON format for storage
        questions_json = [
            {"id": q.id, "question": q.question} 
            for q in questions
        ]
        
        # Create refinement session
        refinement_session = RefinementSession(
            idea_id=session_data.idea_id,
            questions=questions_json,
            answers={},
            is_complete=False
        )
        
        db.add(refinement_session)
        
        # Update idea status to refining
        idea.status = IdeaStatus.refining
        
        db.commit()
        db.refresh(refinement_session)
        
        return refinement_session
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to create refinement session: {str(e)}"
        )

@router.get("/sessions/{session_id}", response_model=RefinementSessionResponse)
def get_refinement_session(
    session_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Get a specific refinement session
    """
    session = db.query(RefinementSession).filter(
        RefinementSession.id == session_id
    ).first()
    
    if not session:
        raise HTTPException(status_code=404, detail="Refinement session not found")
    
    return session

@router.get("/ideas/{idea_id}/sessions/", response_model=List[RefinementSessionResponse])
def get_idea_refinement_sessions(
    idea_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Get all refinement sessions for an idea
    """
    idea = db.query(Idea).filter(Idea.id == idea_id).first()
    if not idea:
        raise HTTPException(status_code=404, detail="Idea not found")
    
    sessions = db.query(RefinementSession).filter(
        RefinementSession.idea_id == idea_id
    ).order_by(RefinementSession.created_at.desc()).all()
    
    return sessions

@router.put("/sessions/{session_id}/answers/", response_model=RefinementSessionResponse)
def submit_refinement_answers(
    session_id: UUID,
    answers_data: RefinementAnswersSubmit,
    db: Session = Depends(get_db)
):
    """
    Submit answers to refinement questions
    """
    session = db.query(RefinementSession).filter(
        RefinementSession.id == session_id
    ).first()
    
    if not session:
        raise HTTPException(status_code=404, detail="Refinement session not found")
    
    # Update answers
    session.answers = answers_data.answers
    
    # Check if all questions are answered
    question_ids = {q["id"] for q in session.questions}
    answered_ids = set(answers_data.answers.keys())
    
    if question_ids <= answered_ids:  # All questions answered
        session.mark_complete()
    
    db.commit()
    db.refresh(session)
    
    return session

@router.post("/sessions/{session_id}/complete/", response_model=RefinementSessionResponse)
def complete_refinement_session(
    session_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Mark a refinement session as complete
    """
    session = db.query(RefinementSession).filter(
        RefinementSession.id == session_id
    ).first()
    
    if not session:
        raise HTTPException(status_code=404, detail="Refinement session not found")
    
    session.mark_complete()
    db.commit()
    db.refresh(session)
    
    return session

@router.post("/questions/generate/", response_model=QuestionGenerationResponse)
async def generate_questions(
    request: Dict[str, Any],
    db: Session = Depends(get_db)
):
    """
    Generate new questions for an idea (standalone endpoint for testing)
    """
    # Extract idea_id from request body
    idea_id = request.get("idea_id")
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
        questions = await ai_service.generate_refinement_questions(
            title=idea.title,
            description=idea.original_description
        )
        
        return QuestionGenerationResponse(questions=questions)
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate questions: {str(e)}"
        )