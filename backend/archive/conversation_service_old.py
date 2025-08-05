"""
Service for managing AI conversations and chat interactions.
"""
from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import datetime
from sqlalchemy.orm import Session
from models import Conversation, Idea
from schemas import ConversationCreate, MessageCreate
from services.ai_service import ai_service


class ConversationService:
    """Service for managing conversation operations."""
    
    def __init__(self, db: Session):
        """Initialize conversation service with database session."""
        self.db = db
    
    def create_conversation(self, conversation_data: ConversationCreate) -> Conversation:
        """
        Create a new conversation.
        
        Args:
            conversation_data: Conversation creation data
            
        Returns:
            Created conversation instance
        """
        # Verify the idea exists
        idea = self.db.query(Idea).filter(Idea.id == conversation_data.idea_id).first()
        if not idea:
            raise ValueError(f"Idea with ID {conversation_data.idea_id} not found")
        
        # Initialize messages list
        messages = []
        if conversation_data.initial_message:
            messages.append({
                "role": "user",
                "content": conversation_data.initial_message,
                "timestamp": datetime.utcnow().isoformat()
            })
        
        db_conversation = Conversation(
            idea_id=conversation_data.idea_id,
            mode=conversation_data.mode,
            messages=messages,
            context={}
        )
        
        self.db.add(db_conversation)
        self.db.commit()
        self.db.refresh(db_conversation)
        
        return db_conversation
    
    def get_conversation(self, conversation_id: UUID) -> Optional[Conversation]:
        """
        Get a conversation by ID.
        
        Args:
            conversation_id: UUID of the conversation
            
        Returns:
            Conversation instance or None if not found
        """
        return self.db.query(Conversation).filter(Conversation.id == conversation_id).first()
    
    def get_idea_conversations(
        self, 
        idea_id: UUID, 
        mode: Optional[str] = None
    ) -> List[Conversation]:
        """
        Get all conversations for an idea.
        
        Args:
            idea_id: UUID of the idea
            mode: Optional filter by conversation mode
            
        Returns:
            List of conversations
        """
        query = self.db.query(Conversation).filter(Conversation.idea_id == idea_id)
        
        if mode:
            query = query.filter(Conversation.mode == mode)
        
        return query.order_by(Conversation.created_at.desc()).all()
    
    async def add_message(
        self, 
        conversation_id: UUID, 
        message: MessageCreate
    ) -> Optional[Conversation]:
        """
        Add a message to a conversation.
        
        Args:
            conversation_id: UUID of the conversation
            message: Message to add
            
        Returns:
            Updated conversation or None if not found
        """
        conversation = self.get_conversation(conversation_id)
        if not conversation:
            return None
        
        # Add user message
        new_message = {
            "role": message.role,
            "content": message.content,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        conversation.messages.append(new_message)
        
        # Generate AI response if the message is from user
        if message.role == "user":
            ai_response = await self._generate_ai_response(conversation, message.content)
            if ai_response:
                ai_message = {
                    "role": "assistant",
                    "content": ai_response,
                    "timestamp": datetime.utcnow().isoformat()
                }
                conversation.messages.append(ai_message)
        
        # Update the conversation
        self.db.commit()
        self.db.refresh(conversation)
        
        return conversation
    
    async def start_refinement_conversation(self, idea_id: UUID) -> Conversation:
        """
        Start a new refinement conversation for an idea.
        
        Args:
            idea_id: UUID of the idea to refine
            
        Returns:
            Created conversation with initial AI response
        """
        idea = self.db.query(Idea).filter(Idea.id == idea_id).first()
        if not idea:
            raise ValueError(f"Idea with ID {idea_id} not found")
        
        # Create conversation
        conversation = Conversation(
            idea_id=idea_id,
            mode="capture",
            messages=[],
            context={"idea_title": idea.title, "original_description": idea.original_description}
        )
        
        self.db.add(conversation)
        self.db.commit()
        self.db.refresh(conversation)
        
        # Generate initial AI refinement response
        try:
            refinement_result = await ai_service.refine_idea(
                original_description=idea.original_description
            )
            
            # Add AI message to conversation
            ai_message = {
                "role": "assistant",
                "content": refinement_result["response"],
                "timestamp": datetime.utcnow().isoformat(),
                "metadata": {
                    "questions": refinement_result.get("questions", []),
                    "refined_data": refinement_result.get("refined_data", {})
                }
            }
            
            conversation.messages.append(ai_message)
            conversation.context.update({
                "refinement_questions": refinement_result.get("questions", []),
                "refined_data": refinement_result.get("refined_data", {})
            })
            
            self.db.commit()
            self.db.refresh(conversation)
            
        except Exception as e:
            # If AI call fails, add a fallback message
            fallback_message = {
                "role": "assistant",
                "content": f"I'd love to help you refine your idea: '{idea.title}'. Let's start by exploring what problem this idea solves and who it would benefit. Can you tell me more about your vision?",
                "timestamp": datetime.utcnow().isoformat()
            }
            conversation.messages.append(fallback_message)
            self.db.commit()
            self.db.refresh(conversation)
        
        return conversation
    
    async def _generate_ai_response(self, conversation: Conversation, user_message: str) -> Optional[str]:
        """
        Generate AI response based on conversation context.
        
        Args:
            conversation: Current conversation
            user_message: Latest user message
            
        Returns:
            AI response string or None if failed
        """
        try:
            if conversation.mode == "capture":
                # Refinement mode - use existing conversation history
                conversation_history = [
                    {"role": msg["role"], "content": msg["content"]} 
                    for msg in conversation.messages
                ]
                
                idea = self.db.query(Idea).filter(Idea.id == conversation.idea_id).first()
                refinement_result = await ai_service.refine_idea(
                    original_description=idea.original_description,
                    conversation_history=conversation_history
                )
                
                return refinement_result["response"]
                
            elif conversation.mode == "build":
                # Build mode - collaborative chat
                conversation_history = [
                    {"role": msg["role"], "content": msg["content"]} 
                    for msg in conversation.messages
                ]
                
                return await ai_service.chat_response(
                    message=user_message,
                    context=conversation.context,
                    conversation_history=conversation_history
                )
                
        except Exception as e:
            print(f"AI response generation failed: {e}")
            return None
    
    def update_context(
        self, 
        conversation_id: UUID, 
        context_updates: Dict[str, Any]
    ) -> Optional[Conversation]:
        """
        Update conversation context.
        
        Args:
            conversation_id: UUID of the conversation
            context_updates: Context data to update
            
        Returns:
            Updated conversation or None if not found
        """
        conversation = self.get_conversation(conversation_id)
        if not conversation:
            return None
        
        conversation.context.update(context_updates)
        self.db.commit()
        self.db.refresh(conversation)
        
        return conversation
    
    def delete_conversation(self, conversation_id: UUID) -> bool:
        """
        Delete a conversation.
        
        Args:
            conversation_id: UUID of the conversation to delete
            
        Returns:
            True if deleted, False if not found
        """
        conversation = self.get_conversation(conversation_id)
        if not conversation:
            return False
        
        self.db.delete(conversation)
        self.db.commit()
        
        return True