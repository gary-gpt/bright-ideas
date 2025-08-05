"""
API routes for conversation management.
"""
from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from schemas import ConversationCreate, ConversationResponse, MessageCreate, ChatRequest, ChatResponse
from services.conversation_service import ConversationService

router = APIRouter(prefix="/conversations", tags=["conversations"])


@router.post("/", response_model=ConversationResponse)
def create_conversation(
    conversation: ConversationCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new conversation.
    
    Args:
        conversation: Conversation creation data
        db: Database session
        
    Returns:
        Created conversation
    """
    service = ConversationService(db)
    
    try:
        db_conversation = service.create_conversation(conversation)
        return db_conversation
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/refine/{idea_id}", response_model=ConversationResponse)
async def start_refinement_conversation(
    idea_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Start a new refinement conversation for an idea.
    
    Args:
        idea_id: UUID of the idea to refine
        db: Database session
        
    Returns:
        Created conversation with initial AI response
    """
    service = ConversationService(db)
    
    try:
        conversation = await service.start_refinement_conversation(idea_id)
        return conversation
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start refinement: {str(e)}")


@router.get("/{conversation_id}", response_model=ConversationResponse)
def get_conversation(
    conversation_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Get a specific conversation by ID.
    
    Args:
        conversation_id: UUID of the conversation
        db: Database session
        
    Returns:
        Conversation details
    """
    service = ConversationService(db)
    conversation = service.get_conversation(conversation_id)
    
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    return conversation


@router.get("/idea/{idea_id}", response_model=List[ConversationResponse])
def get_idea_conversations(
    idea_id: UUID,
    mode: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Get all conversations for an idea.
    
    Args:
        idea_id: UUID of the idea
        mode: Optional filter by conversation mode
        db: Database session
        
    Returns:
        List of conversations
    """
    service = ConversationService(db)
    conversations = service.get_idea_conversations(idea_id, mode)
    return conversations


@router.post("/{conversation_id}/messages", response_model=ConversationResponse)
async def add_message(
    conversation_id: UUID,
    message: MessageCreate,
    db: Session = Depends(get_db)
):
    """
    Add a message to a conversation.
    
    Args:
        conversation_id: UUID of the conversation
        message: Message to add
        db: Database session
        
    Returns:
        Updated conversation
    """
    service = ConversationService(db)
    
    try:
        updated_conversation = await service.add_message(conversation_id, message)
        
        if not updated_conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")
        
        return updated_conversation
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to add message: {str(e)}")


@router.post("/chat", response_model=ChatResponse)
async def chat(
    chat_request: ChatRequest,
    db: Session = Depends(get_db)
):
    """
    Send a chat message and get AI response.
    
    Args:
        chat_request: Chat request with message and context
        db: Database session
        
    Returns:
        Chat response with AI message
    """
    service = ConversationService(db)
    
    try:
        if chat_request.conversation_id:
            # Add message to existing conversation
            message = MessageCreate(role="user", content=chat_request.message)
            conversation = await service.add_message(chat_request.conversation_id, message)
            
            if not conversation:
                raise HTTPException(status_code=404, detail="Conversation not found")
            
            # Get the latest AI response
            ai_message = None
            for msg in reversed(conversation.messages):
                if msg.get("role") == "assistant":
                    ai_message = msg.get("content")
                    break
            
            return ChatResponse(
                message=ai_message or "No response generated",
                conversation_id=conversation.id,
                context=conversation.context
            )
        else:
            raise HTTPException(status_code=400, detail="conversation_id is required")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat failed: {str(e)}")


@router.put("/{conversation_id}/context")
def update_conversation_context(
    conversation_id: UUID,
    context_updates: dict,
    db: Session = Depends(get_db)
):
    """
    Update conversation context.
    
    Args:
        conversation_id: UUID of the conversation
        context_updates: Context data to update
        db: Database session
        
    Returns:
        Success message
    """
    service = ConversationService(db)
    conversation = service.update_context(conversation_id, context_updates)
    
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    return {"message": "Context updated successfully"}


@router.delete("/{conversation_id}")
def delete_conversation(
    conversation_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Delete a conversation.
    
    Args:
        conversation_id: UUID of the conversation to delete
        db: Database session
        
    Returns:
        Success message
    """
    service = ConversationService(db)
    success = service.delete_conversation(conversation_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    return {"message": "Conversation deleted successfully"}