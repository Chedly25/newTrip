from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import Optional, Dict
import json
import uuid
import logging

from app.core.claude_ai import ClaudeAIService
from app.core.cache import redis_client
from app import schemas

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/chat", tags=["chat"])

claude_service = ClaudeAIService()

@router.post("/", response_model=schemas.ChatResponse)
async def chat_with_assistant(message: schemas.ChatMessage):
    """Chat with Claude AI travel assistant"""
    
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

@router.delete("/{conversation_id}")
async def clear_conversation(conversation_id: str):
    """Clear conversation history"""
    
    if redis_client:
        try:
            history_key = f"chat:{conversation_id}"
            redis_client.delete(history_key)
        except Exception as e:
            logger.warning(f"Cache error: {e}")
    
    return {"message": "Conversation cleared"}