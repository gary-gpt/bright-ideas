"""
Updated SQLAlchemy models for Bright Ideas - Structured Refinement System
"""
from sqlalchemy import Column, String, Text, DateTime, Boolean, JSON, ForeignKey, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
from uuid import uuid4
import enum

Base = declarative_base()

# Enums
class IdeaStatus(str, enum.Enum):
    captured = "captured"
    refining = "refining" 
    planned = "planned"
    archived = "archived"

class PlanStatus(str, enum.Enum):
    draft = "draft"
    generated = "generated"
    edited = "edited"
    published = "published"

class Idea(Base):
    """Core idea entity - the starting point for everything"""
    __tablename__ = "ideas"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    title = Column(String(200), nullable=False)
    original_description = Column(Text, nullable=False)
    tags = Column(JSON, default=lambda: [])  # ["productivity", "ai", "tool"]
    status = Column(Enum(IdeaStatus), default=IdeaStatus.captured)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    refinement_sessions = relationship(
        "RefinementSession", 
        back_populates="idea", 
        cascade="all, delete-orphan",
        order_by="RefinementSession.created_at.desc()"
    )
    plans = relationship(
        "Plan", 
        back_populates="idea", 
        cascade="all, delete-orphan",
        order_by="Plan.created_at.desc()"
    )

    @property
    def active_plan(self):
        """Get the currently active plan for this idea"""
        for plan in self.plans:
            if plan.is_active:
                return plan
        return None

    @property
    def latest_session(self):
        """Get the most recent refinement session"""
        return self.refinement_sessions[0] if self.refinement_sessions else None

class RefinementSession(Base):
    """AI-generated questions and user answers for idea refinement"""
    __tablename__ = "refinement_sessions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    idea_id = Column(UUID(as_uuid=True), ForeignKey("ideas.id"), nullable=False)
    
    # AI-generated questions and user answers
    questions = Column(JSON, nullable=False)  
    # Format: [{"id": "q1", "question": "Who are the target users?"}, ...]
    
    answers = Column(JSON, default=dict)      
    # Format: {"q1": "Busy professionals who get 50+ newsletters", "q2": "..."}
    
    # Session metadata
    is_complete = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    
    # Store the LLM prompt used to generate questions (for debugging/improvement)
    generation_prompt = Column(Text, nullable=True)
    
    # Relationships
    idea = relationship("Idea", back_populates="refinement_sessions")
    plans = relationship("Plan", back_populates="refinement_session")

    def mark_complete(self):
        """Mark this session as complete"""
        self.is_complete = True
        self.completed_at = datetime.utcnow()

class Plan(Base):
    """Generated implementation plan based on refined idea"""
    __tablename__ = "plans"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    idea_id = Column(UUID(as_uuid=True), ForeignKey("ideas.id"), nullable=False)
    refinement_session_id = Column(UUID(as_uuid=True), ForeignKey("refinement_sessions.id"), nullable=True)
    
    # Plan content (structured)
    summary = Column(Text, nullable=False)  # 1-paragraph overview
    steps = Column(JSON, nullable=False)    # [{"order": 1, "title": "...", "description": "...", "estimated_time": "2 hours"}]
    resources = Column(JSON, default=list) # [{"title": "Figma", "url": "...", "type": "tool", "description": "..."}]
    
    # Plan metadata
    status = Column(Enum(PlanStatus), default=PlanStatus.generated)
    is_active = Column(Boolean, default=False)  # Only one active plan per idea
    content_markdown = Column(Text, nullable=True)  # Human-readable version
    
    # Generation metadata
    generation_prompt = Column(Text, nullable=True)  # LLM prompt used
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    idea = relationship("Idea", back_populates="plans")
    refinement_session = relationship("RefinementSession", back_populates="plans")

    def activate(self):
        """Make this the active plan (deactivates others for same idea)"""
        # Deactivate other plans for this idea
        for plan in self.idea.plans:
            if plan.id != self.id:
                plan.is_active = False
        self.is_active = True

    def to_export_dict(self):
        """Generate export-ready dictionary"""
        return {
            "idea": {
                "title": self.idea.title,
                "description": self.idea.original_description,
                "tags": self.idea.tags
            },
            "plan": {
                "summary": self.summary,
                "steps": self.steps,
                "resources": self.resources,
                "status": self.status.value
            }
        }