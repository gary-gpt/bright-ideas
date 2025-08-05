"""
Business logic for managing ideas and their lifecycle.
"""
from typing import List, Optional, Dict, Any
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from models import Idea, Conversation, BuildPlan
from schemas import IdeaCreate, IdeaUpdate


class IdeaService:
    """Service for managing idea operations."""
    
    def __init__(self, db: Session):
        """Initialize idea service with database session."""
        self.db = db
    
    def create_idea(self, idea_data: IdeaCreate) -> Idea:
        """
        Create a new idea.
        
        Args:
            idea_data: Idea creation data
            
        Returns:
            Created idea instance
        """
        db_idea = Idea(
            title=idea_data.title,
            original_description=idea_data.original_description,
            tags=idea_data.tags,
            status="captured"
        )
        
        self.db.add(db_idea)
        self.db.commit()
        self.db.refresh(db_idea)
        
        return db_idea
    
    def get_idea(self, idea_id: UUID) -> Optional[Idea]:
        """
        Get an idea by ID.
        
        Args:
            idea_id: UUID of the idea
            
        Returns:
            Idea instance or None if not found
        """
        return self.db.query(Idea).filter(Idea.id == idea_id).first()
    
    def get_ideas(
        self, 
        skip: int = 0, 
        limit: int = 100,
        search: Optional[str] = None,
        tags: Optional[List[str]] = None,
        status: Optional[str] = None
    ) -> List[Idea]:
        """
        Get ideas with optional filtering.
        
        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            search: Search term for title and description
            tags: Filter by tags
            status: Filter by status
            
        Returns:
            List of ideas
        """
        query = self.db.query(Idea)
        
        # Apply search filter
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                or_(
                    Idea.title.ilike(search_term),
                    Idea.original_description.ilike(search_term),
                    Idea.refined_description.ilike(search_term)
                )
            )
        
        # Apply tag filter
        if tags:
            for tag in tags:
                query = query.filter(Idea.tags.contains([tag]))
        
        # Apply status filter
        if status:
            query = query.filter(Idea.status == status)
        
        # Order by most recent first
        query = query.order_by(Idea.updated_at.desc())
        
        return query.offset(skip).limit(limit).all()
    
    def update_idea(self, idea_id: UUID, update_data: IdeaUpdate) -> Optional[Idea]:
        """
        Update an existing idea.
        
        Args:
            idea_id: UUID of the idea to update
            update_data: Updated idea data
            
        Returns:
            Updated idea instance or None if not found
        """
        db_idea = self.get_idea(idea_id)
        if not db_idea:
            return None
        
        # Update fields that are provided
        update_dict = update_data.dict(exclude_unset=True)
        for field, value in update_dict.items():
            setattr(db_idea, field, value)
        
        self.db.commit()
        self.db.refresh(db_idea)
        
        return db_idea
    
    def delete_idea(self, idea_id: UUID) -> bool:
        """
        Delete an idea and all related data.
        
        Args:
            idea_id: UUID of the idea to delete
            
        Returns:
            True if deleted, False if not found
        """
        db_idea = self.get_idea(idea_id)
        if not db_idea:
            return False
        
        self.db.delete(db_idea)
        self.db.commit()
        
        return True
    
    def get_idea_stats(self) -> Dict[str, Any]:
        """
        Get statistics about ideas.
        
        Returns:
            Dictionary with idea statistics
        """
        total_ideas = self.db.query(Idea).count()
        
        status_counts = {}
        for status in ["captured", "refined", "building", "completed"]:
            count = self.db.query(Idea).filter(Idea.status == status).count()
            status_counts[status] = count
        
        # Get most common tags
        all_ideas = self.db.query(Idea).all()
        tag_counts = {}
        for idea in all_ideas:
            for tag in idea.tags:
                tag_counts[tag] = tag_counts.get(tag, 0) + 1
        
        popular_tags = sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        
        return {
            "total_ideas": total_ideas,
            "status_distribution": status_counts,
            "popular_tags": popular_tags
        }
    
    def get_recent_ideas(self, limit: int = 5) -> List[Idea]:
        """
        Get the most recently updated ideas.
        
        Args:
            limit: Maximum number of ideas to return
            
        Returns:
            List of recent ideas
        """
        return (
            self.db.query(Idea)
            .order_by(Idea.updated_at.desc())
            .limit(limit)
            .all()
        )