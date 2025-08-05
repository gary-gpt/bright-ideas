"""
Updated Pydantic schemas for Bright Ideas - Structured Refinement System
"""
from datetime import datetime
from typing import List, Dict, Any, Optional
from uuid import UUID
from pydantic import BaseModel, Field, field_validator

# Idea Schemas
class IdeaCreate(BaseModel):
    """Schema for creating a new idea"""
    title: str = Field(..., min_length=1, max_length=200)
    original_description: str = Field(..., min_length=10)
    tags: List[str] = Field(default_factory=list)
    
    @field_validator('tags', mode='before')
    @classmethod
    def validate_tags(cls, v):
        """Ensure tags is always a list, even if sent as string"""
        if isinstance(v, str):
            if v.strip() == '' or v.strip() == '[]':
                return []
            try:
                import json
                parsed = json.loads(v)
                return parsed if isinstance(parsed, list) else []
            except (json.JSONDecodeError, TypeError):
                return []
        elif isinstance(v, list):
            return v
        else:
            return []

class IdeaUpdate(BaseModel):
    """Schema for updating an existing idea"""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    original_description: Optional[str] = None
    tags: Optional[List[str]] = None
    status: Optional[str] = Field(None, pattern="^(captured|refining|planned|archived)$")

class IdeaResponse(BaseModel):
    """Schema for idea responses"""
    id: UUID
    title: str
    original_description: str
    tags: List[str]
    status: str
    created_at: datetime
    updated_at: datetime
    
    # Include related data counts
    refinement_sessions_count: int = 0
    plans_count: int = 0
    has_active_plan: bool = False
    
    class Config:
        from_attributes = True

class IdeaDetailResponse(IdeaResponse):
    """Extended idea response with related data"""
    latest_session: Optional['RefinementSessionResponse'] = None
    active_plan: Optional['PlanResponse'] = None

# Refinement Session Schemas
class RefinementQuestion(BaseModel):
    """Individual question structure"""
    id: str
    question: str

class RefinementSessionCreate(BaseModel):
    """Schema for creating refinement session"""
    idea_id: UUID

class RefinementAnswersSubmit(BaseModel):
    """Schema for submitting answers to refinement questions"""
    answers: Dict[str, str] = Field(..., description="Question ID to answer mapping")

class RefinementSessionResponse(BaseModel):
    """Schema for refinement session responses"""
    id: UUID
    idea_id: UUID
    questions: List[RefinementQuestion]
    answers: Dict[str, str]
    is_complete: bool
    created_at: datetime
    completed_at: Optional[datetime]
    
    class Config:
        from_attributes = True

# Plan Schemas
class PlanStep(BaseModel):
    """Individual plan step structure"""
    order: int
    title: str
    description: str
    estimated_time: Optional[str] = None

class PlanResource(BaseModel):
    """Plan resource structure"""
    title: str
    url: Optional[str] = None
    type: str = "tool"  # tool, article, service, etc.
    description: Optional[str] = None

class PlanCreate(BaseModel):
    """Schema for creating a plan"""
    refinement_session_id: UUID
    summary: str
    steps: List[PlanStep]
    resources: List[PlanResource] = Field(default_factory=list)

class PlanUpdate(BaseModel):
    """Schema for updating a plan"""
    summary: Optional[str] = None
    steps: Optional[List[PlanStep]] = None
    resources: Optional[List[PlanResource]] = None
    status: Optional[str] = Field(None, pattern="^(draft|generated|edited|published)$")

class PlanResponse(BaseModel):
    """Schema for plan responses"""
    id: UUID
    idea_id: UUID
    refinement_session_id: Optional[UUID]
    summary: str
    steps: List[PlanStep]
    resources: List[PlanResource]
    status: str
    is_active: bool
    content_markdown: Optional[str]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class PlanExportResponse(BaseModel):
    """Schema for plan export"""
    idea: Dict[str, Any]
    plan: Dict[str, Any]

# AI/LLM Schemas
class QuestionGenerationRequest(BaseModel):
    """Schema for requesting AI-generated questions"""
    title: str
    description: str

class QuestionGenerationResponse(BaseModel):
    """Schema for AI-generated questions response"""
    questions: List[RefinementQuestion]
    
class PlanGenerationRequest(BaseModel):
    """Schema for requesting AI-generated plan"""
    idea: IdeaResponse
    refinement_session: RefinementSessionResponse

class PlanGenerationResponse(BaseModel):
    """Schema for AI-generated plan response"""
    summary: str
    steps: List[PlanStep]  
    resources: List[PlanResource]

# Update forward references
IdeaDetailResponse.model_rebuild()