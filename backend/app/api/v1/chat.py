from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, List
from sqlalchemy.orm import Session
import json
import uuid
import logging

from app.core.claude_ai import ClaudeAIService
from app.core.cache import redis_client
from app import schemas, models
from app.database import get_db
from app.api.v1.auth import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/chat", tags=["Enhanced AI Chat"])

claude_service = ClaudeAIService()

# Enhanced Chat Models
class AdvancedChatMessage(BaseModel):
    message: str
    conversation_id: Optional[str] = None
    chat_type: str = "travel_companion"  # travel_companion, trip_planner, food_guide, safety_advisor
    context: Optional[Dict] = {}
    location: Optional[str] = None

class ChatContext(BaseModel):
    current_location: Optional[str] = None
    travel_dates: Optional[List[str]] = None
    interests: Optional[List[str]] = None
    budget: Optional[str] = None
    group_size: Optional[int] = 1
    travel_style: Optional[str] = "balanced"

# Legacy endpoint for backward compatibility
@router.post("/", response_model=schemas.ChatResponse)
async def chat_with_assistant(message: schemas.ChatMessage):
    """Chat with Claude AI travel assistant (legacy endpoint)"""
    
    # Get or create conversation
    conversation_id = message.conversation_id or str(uuid.uuid4())
    
    # Get conversation history from cache
    conversation_history = []
    if redis_client:
        try:
            history_key = f"chat:{conversation_id}"
            history = redis_client.get(history_key)
            if history:
                conversation_history = json.loads(history)
        except Exception as e:
            logger.warning(f"Cache error: {e}")
    
    # Get AI response
    response = await claude_service.chat_assistant(
        message.message,
        conversation_history
    )
    
    # Update history
    conversation_history.append({"role": "user", "content": message.message})
    conversation_history.append({"role": "assistant", "content": response})
    
    # Cache for 1 hour if Redis is available
    if redis_client:
        try:
            history_key = f"chat:{conversation_id}"
            redis_client.setex(
                history_key,
                3600,
                json.dumps(conversation_history[-10:])  # Keep last 10 messages
            )
        except Exception as e:
            logger.warning(f"Cache error: {e}")
    
    return {
        "conversation_id": conversation_id,
        "response": response
    }

# NEW ENHANCED AI CHAT ENDPOINTS

@router.post("/advanced")
async def advanced_travel_chat(
    message: AdvancedChatMessage,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Advanced AI travel companion with context awareness and persistent conversations"""
    
    try:
        # Get or create conversation
        conversation_id = message.conversation_id or str(uuid.uuid4())
        
        # Get or create conversation record
        conversation = db.query(models.Conversation).filter(
            models.Conversation.id == conversation_id
        ).first()
        
        if not conversation:
            conversation = models.Conversation(
                id=conversation_id,
                user_id=current_user.id,
                conversation_type=message.chat_type,
                context_location=message.location,
                context_data=message.context
            )
            db.add(conversation)
            db.commit()
            db.refresh(conversation)
        
        # Get conversation history from database
        messages = db.query(models.ConversationMessage).filter(
            models.ConversationMessage.conversation_id == conversation_id
        ).order_by(models.ConversationMessage.timestamp.desc()).limit(10).all()
        
        conversation_history = [
            {"role": msg.role, "content": msg.content}
            for msg in reversed(messages)
        ]
        
        # Get AI response with full context
        ai_response = await claude_service.advanced_travel_chat(
            message.message,
            context=message.context,
            conversation_history=conversation_history,
            chat_type=message.chat_type
        )
        
        # Save user message
        user_message = models.ConversationMessage(
            conversation_id=conversation_id,
            role="user",
            content=message.message,
            message_metadata={"location": message.location, "chat_type": message.chat_type}
        )
        db.add(user_message)
        
        # Save AI response
        ai_message = models.ConversationMessage(
            conversation_id=conversation_id,
            role="assistant",
            content=ai_response["response"],
            message_metadata={"confidence": ai_response.get("confidence", 0.0)}
        )
        db.add(ai_message)
        
        # Update conversation last activity
        conversation.last_activity = db.func.now()
        
        db.commit()
        
        return {
            "conversation_id": conversation_id,
            "response": ai_response["response"],
            "confidence": ai_response.get("confidence", 0.0),
            "chat_type": message.chat_type,
            "suggestions": ai_response.get("suggestions", [])
        }
        
    except Exception as e:
        logger.error(f"Advanced chat error: {e}")
        db.rollback()
        return {
            "conversation_id": conversation_id,
            "response": "I'm having trouble connecting. Please try again!",
            "confidence": 0.0
        }

@router.get("/conversations")
async def get_user_conversations(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Get all conversations for the current user"""
    
    conversations = db.query(models.Conversation).filter(
        models.Conversation.user_id == current_user.id
    ).order_by(models.Conversation.last_activity.desc()).all()
    
    return [
        {
            "id": str(conv.id),
            "conversation_type": conv.conversation_type,
            "context_location": conv.context_location,
            "last_activity": conv.last_activity,
            "message_count": len(conv.messages)
        }
        for conv in conversations
    ]

@router.get("/conversations/{conversation_id}")
async def get_conversation_history(
    conversation_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Get full conversation history"""
    
    try:
        conversation_uuid = uuid.UUID(conversation_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid conversation ID")
    
    conversation = db.query(models.Conversation).filter(
        models.Conversation.id == conversation_uuid,
        models.Conversation.user_id == current_user.id
    ).first()
    
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    messages = db.query(models.ConversationMessage).filter(
        models.ConversationMessage.conversation_id == conversation_uuid
    ).order_by(models.ConversationMessage.timestamp).all()
    
    return {
        "conversation_id": conversation_id,
        "conversation_type": conversation.conversation_type,
        "context_location": conversation.context_location,
        "context_data": conversation.context_data,
        "messages": [
            {
                "role": msg.role,
                "content": msg.content,
                "timestamp": msg.timestamp,
                "metadata": msg.message_metadata
            }
            for msg in messages
        ]
    }

@router.post("/contexts/update")
async def update_conversation_context(
    conversation_id: str,
    context: ChatContext,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Update conversation context (location, dates, preferences)"""
    
    try:
        conversation_uuid = uuid.UUID(conversation_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid conversation ID")
    
    conversation = db.query(models.Conversation).filter(
        models.Conversation.id == conversation_uuid,
        models.Conversation.user_id == current_user.id
    ).first()
    
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    # Update context
    conversation.context_location = context.current_location
    conversation.context_data = context.dict(exclude_unset=True)
    conversation.last_activity = db.func.now()
    
    db.commit()
    
    return {"message": "Context updated successfully"}

@router.delete("/conversations/{conversation_id}")
async def delete_conversation(
    conversation_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Delete a conversation and all its messages"""
    
    try:
        conversation_uuid = uuid.UUID(conversation_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid conversation ID")
    
    conversation = db.query(models.Conversation).filter(
        models.Conversation.id == conversation_uuid,
        models.Conversation.user_id == current_user.id
    ).first()
    
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    # Delete all messages first
    db.query(models.ConversationMessage).filter(
        models.ConversationMessage.conversation_id == conversation_uuid
    ).delete()
    
    # Delete conversation
    db.delete(conversation)
    db.commit()
    
    # Also clear from cache if exists
    if redis_client:
        try:
            history_key = f"chat:{conversation_id}"
            redis_client.delete(history_key)
        except Exception as e:
            logger.warning(f"Cache error: {e}")
    
    return {"message": "Conversation deleted successfully"}

# Legacy endpoint for clearing cache
@router.delete("/{conversation_id}")
async def clear_conversation(conversation_id: str):
    """Clear conversation history (legacy endpoint)"""
    
    if redis_client:
        try:
            history_key = f"chat:{conversation_id}"
            redis_client.delete(history_key)
        except Exception as e:
            logger.warning(f"Cache error: {e}")
    
    return {"message": "Conversation cleared"}