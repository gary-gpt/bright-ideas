"""
Pydantic schemas for request/response validation.
"""
from datetime import datetime
from typing import List, Dict, Any, Optional
from uuid import UUID
from pydantic import BaseModel, Field


# Idea Schemas
class IdeaCreate(BaseModel):
    """Schema for creating a new idea."""
    title: str = Field(..., min_length=1, max_length=200)
    original_description: str = Field(..., min_length=10)
    tags: List[str] = Field(default_factory=list)


class IdeaUpdate(BaseModel):
    """Schema for updating an existing idea."""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    refined_description: Optional[str] = None
    problem_statement: Optional[str] = None
    target_audience: Optional[str] = None
    implementation_notes: Optional[Dict[str, Any]] = None
    tags: Optional[List[str]] = None
    status: Optional[str] = Field(None, regex="^(captured|refined|building|completed)$")


class IdeaResponse(BaseModel):
    """Schema for idea responses."""
    id: UUID
    title: str
    original_description: str
    refined_description: Optional[str]
    problem_statement: Optional[str]
    target_audience: Optional[str]
    implementation_notes: Dict[str, Any]
    tags: List[str]
    status: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# Conversation Schemas
class MessageCreate(BaseModel):
    """Schema for creating a new message in a conversation."""
    content: str = Field(..., min_length=1)
    role: str = Field(..., regex="^(user|assistant)$")


class ConversationCreate(BaseModel):
    """Schema for creating a new conversation."""
    idea_id: UUID
    mode: str = Field(..., regex="^(capture|build)$")
    initial_message: Optional[str] = None


class ConversationResponse(BaseModel):
    """Schema for conversation responses."""
    id: UUID
    idea_id: UUID
    mode: str
    messages: List[Dict[str, Any]]
    context: Dict[str, Any]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# Build Plan Schemas
class BuildPlanCreate(BaseModel):
    """Schema for creating a build plan."""
    idea_id: UUID
    plan_data: Dict[str, Any] = Field(..., description="Structured plan data")


class BuildPlanUpdate(BaseModel):
    """Schema for updating a build plan."""
    plan_data: Optional[Dict[str, Any]] = None
    export_configs: Optional[Dict[str, Any]] = None


class BuildPlanResponse(BaseModel):
    """Schema for build plan responses."""
    id: UUID
    idea_id: UUID
    plan_data: Dict[str, Any]
    export_configs: Dict[str, Any]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# Export Schemas
class ExportCreate(BaseModel):
    """Schema for creating an export."""
    build_plan_id: UUID
    export_type: str = Field(..., min_length=1, max_length=50)
    file_data: Dict[str, str] = Field(..., description="Filename to content mapping")


class ExportResponse(BaseModel):
    """Schema for export responses."""
    id: UUID
    build_plan_id: UUID
    export_type: str
    file_data: Dict[str, str]
    created_at: datetime
    
    class Config:
        from_attributes = True


# Chat/AI Schemas
class ChatMessage(BaseModel):
    """Schema for chat messages."""
    role: str = Field(..., regex="^(user|assistant|system)$")
    content: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class ChatRequest(BaseModel):
    """Schema for chat requests."""
    message: str = Field(..., min_length=1)
    conversation_id: Optional[UUID] = None
    context: Optional[Dict[str, Any]] = Field(default_factory=dict)


class ChatResponse(BaseModel):
    """Schema for chat responses."""
    message: str
    conversation_id: UUID
    suggestions: Optional[List[str]] = None
    context: Optional[Dict[str, Any]] = None