"""
SQLAlchemy database models for Bright Ideas.
"""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, DateTime, ForeignKey, ARRAY
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from database import Base


class Idea(Base):
    """
    Core idea model storing brainstormed concepts.
    """
    __tablename__ = "ideas"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(200), nullable=False)
    original_description = Column(Text, nullable=False)
    refined_description = Column(Text)
    problem_statement = Column(Text)
    target_audience = Column(Text)
    implementation_notes = Column(JSONB, default=dict)
    tags = Column(ARRAY(String), default=list)
    status = Column(String(20), default="captured")  # captured, refined, building, completed
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    conversations = relationship("Conversation", back_populates="idea", cascade="all, delete-orphan")
    build_plans = relationship("BuildPlan", back_populates="idea", cascade="all, delete-orphan")


class Conversation(Base):
    """
    AI conversation history for idea refinement and build planning.
    """
    __tablename__ = "conversations"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    idea_id = Column(UUID(as_uuid=True), ForeignKey("ideas.id"), nullable=False)
    mode = Column(String(20), nullable=False)  # capture, build
    messages = Column(JSONB, default=list)  # [{"role": "user|assistant", "content": "...", "timestamp": "..."}]
    context = Column(JSONB, default=dict)  # Additional context data
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    idea = relationship("Idea", back_populates="conversations")


class BuildPlan(Base):
    """
    Structured build plans generated from refined ideas.
    """
    __tablename__ = "build_plans"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    idea_id = Column(UUID(as_uuid=True), ForeignKey("ideas.id"), nullable=False)
    plan_data = Column(JSONB, nullable=False)  # {components: [], phases: [], tasks: []}
    export_configs = Column(JSONB, default=dict)  # Export format preferences
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    idea = relationship("Idea", back_populates="build_plans")
    exports = relationship("Export", back_populates="build_plan", cascade="all, delete-orphan")


class Export(Base):
    """
    Generated export files from build plans.
    """
    __tablename__ = "exports"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    build_plan_id = Column(UUID(as_uuid=True), ForeignKey("build_plans.id"), nullable=False)
    export_type = Column(String(50), nullable=False)  # markdown, json, zip, etc.
    file_data = Column(JSONB, nullable=False)  # {filename: content, ...}
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    build_plan = relationship("BuildPlan", back_populates="exports")