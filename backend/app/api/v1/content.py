from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, Dict, List
import uuid
import logging

from app import models
from app.database import get_db
from app.api.v1.auth import get_current_user
from app.core.claude_ai import ClaudeAIService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/content", tags=["AI Content Generator"])

claude_service = ClaudeAIService()

# Content generation models
class ContentGenerationRequest(BaseModel):
    content_type: str  # blog_post, social_media, trip_summary, itinerary_narrative
    places: List[Dict]
    title: Optional[str] = None
    tone: str = "enthusiastic"  # casual, professional, humorous, poetic
    target_audience: str = "general travelers"
    language: str = "en"
    custom_prompt: Optional[str] = None
    related_trip_id: Optional[str] = None

class ContentResponse(BaseModel):
    content_id: str
    title: str
    content: str
    word_count: int
    hashtags: Optional[List[str]] = None
    content_type: str

@router.post("/generate", response_model=ContentResponse)
async def generate_travel_content(
    request: ContentGenerationRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Generate AI-powered travel content"""
    
    try:
        # Prepare context for AI
        context = {
            "tone": request.tone,
            "audience": request.target_audience,
            "language": request.language
        }
        
        if request.custom_prompt:
            context["custom_instructions"] = request.custom_prompt
        
        # Generate content using Claude
        ai_result = await claude_service.generate_travel_content(
            request.content_type,
            request.places,
            context
        )
        
        if "error" in ai_result:
            raise HTTPException(status_code=500, detail=ai_result["error"])
        
        # Create database record
        generated_content = models.GeneratedContent(
            user_id=current_user.id,
            content_type=request.content_type,
            title=ai_result.get("title", request.title or "Untitled"),
            content=ai_result.get("content", ""),
            prompt_used=request.custom_prompt or f"Generate {request.content_type}",
            target_audience=request.target_audience,
            tone=request.tone,
            language=request.language,
            related_places=[place.get("name", "Unknown") for place in request.places[:10]],
            related_trip_id=uuid.UUID(request.related_trip_id) if request.related_trip_id else None,
            word_count=ai_result.get("word_count", len(ai_result.get("content", "").split()))
        )
        
        db.add(generated_content)
        db.commit()
        db.refresh(generated_content)
        
        return {
            "content_id": str(generated_content.id),
            "title": ai_result.get("title", ""),
            "content": ai_result.get("content", ""),
            "word_count": ai_result.get("word_count", 0),
            "hashtags": ai_result.get("hashtags", []),
            "content_type": request.content_type
        }
        
    except Exception as e:
        logger.error(f"Content generation error: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate content")

@router.post("/generate-from-trip/{trip_id}")
async def generate_content_from_trip(
    trip_id: str,
    content_type: str,
    tone: str = "enthusiastic",
    target_audience: str = "general travelers",
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Generate content based on an existing trip itinerary"""
    
    try:
        trip_uuid = uuid.UUID(trip_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid trip ID")
    
    # Get the trip
    trip = db.query(models.Itinerary).filter(
        models.Itinerary.id == trip_uuid,
        models.Itinerary.user_id == current_user.id
    ).first()
    
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")
    
    # Extract places from the trip
    places = []
    if trip.generated_plan and "places" in trip.generated_plan:
        places = trip.generated_plan["places"]
    
    # Get city information
    city = db.query(models.City).filter(models.City.id == trip.city_id).first()
    if city:
        places.append({
            "name": city.name,
            "description": f"Beautiful city in {city.region}, France",
            "category": "destination"
        })
    
    # Generate content
    context = {
        "tone": tone,
        "audience": target_audience,
        "trip_dates": f"{trip.start_date} to {trip.end_date}" if trip.start_date and trip.end_date else None
    }
    
    ai_result = await claude_service.generate_travel_content(
        content_type,
        places,
        context
    )
    
    if "error" in ai_result:
        raise HTTPException(status_code=500, detail=ai_result["error"])
    
    # Save generated content
    generated_content = models.GeneratedContent(
        user_id=current_user.id,
        content_type=content_type,
        title=ai_result.get("title", f"My Trip to {city.name if city else 'France'}"),
        content=ai_result.get("content", ""),
        prompt_used=f"Generate {content_type} from trip {trip_id}",
        target_audience=target_audience,
        tone=tone,
        language="en",
        related_places=[place.get("name", "Unknown") for place in places[:10]],
        related_trip_id=trip_uuid,
        word_count=ai_result.get("word_count", len(ai_result.get("content", "").split()))
    )
    
    db.add(generated_content)
    db.commit()
    
    return {
        "content_id": str(generated_content.id),
        "title": ai_result.get("title", ""),
        "content": ai_result.get("content", ""),
        "word_count": ai_result.get("word_count", 0),
        "hashtags": ai_result.get("hashtags", []),
        "content_type": content_type
    }

@router.get("/my-content")
async def get_user_generated_content(
    content_type: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Get all user's generated content"""
    
    query = db.query(models.GeneratedContent).filter(
        models.GeneratedContent.user_id == current_user.id
    )
    
    if content_type:
        query = query.filter(models.GeneratedContent.content_type == content_type)
    
    content_items = query.order_by(models.GeneratedContent.created_at.desc()).all()
    
    return [
        {
            "id": str(item.id),
            "title": item.title,
            "content_type": item.content_type,
            "word_count": item.word_count,
            "tone": item.tone,
            "target_audience": item.target_audience,
            "related_places": item.related_places,
            "created_at": item.created_at,
            "preview": item.content[:200] + "..." if len(item.content) > 200 else item.content
        }
        for item in content_items
    ]

@router.get("/{content_id}")
async def get_generated_content(
    content_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Get specific generated content"""
    
    try:
        content_uuid = uuid.UUID(content_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid content ID")
    
    content = db.query(models.GeneratedContent).filter(
        models.GeneratedContent.id == content_uuid,
        models.GeneratedContent.user_id == current_user.id
    ).first()
    
    if not content:
        raise HTTPException(status_code=404, detail="Content not found")
    
    return {
        "id": str(content.id),
        "title": content.title,
        "content": content.content,
        "content_type": content.content_type,
        "word_count": content.word_count,
        "tone": content.tone,
        "target_audience": content.target_audience,
        "language": content.language,
        "related_places": content.related_places,
        "related_trip_id": str(content.related_trip_id) if content.related_trip_id else None,
        "created_at": content.created_at
    }

@router.post("/{content_id}/regenerate")
async def regenerate_content(
    content_id: str,
    tone: Optional[str] = None,
    target_audience: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Regenerate content with different parameters"""
    
    try:
        content_uuid = uuid.UUID(content_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid content ID")
    
    original_content = db.query(models.GeneratedContent).filter(
        models.GeneratedContent.id == content_uuid,
        models.GeneratedContent.user_id == current_user.id
    ).first()
    
    if not original_content:
        raise HTTPException(status_code=404, detail="Content not found")
    
    # Use new parameters or keep original ones
    new_tone = tone or original_content.tone
    new_audience = target_audience or original_content.target_audience
    
    # Recreate places list
    places = [{"name": place} for place in original_content.related_places]
    
    # Generate new content
    context = {
        "tone": new_tone,
        "audience": new_audience,
        "language": original_content.language
    }
    
    ai_result = await claude_service.generate_travel_content(
        original_content.content_type,
        places,
        context
    )
    
    if "error" in ai_result:
        raise HTTPException(status_code=500, detail=ai_result["error"])
    
    # Update the existing content
    original_content.content = ai_result.get("content", "")
    original_content.title = ai_result.get("title", original_content.title)
    original_content.tone = new_tone
    original_content.target_audience = new_audience
    original_content.word_count = ai_result.get("word_count", 0)
    original_content.created_at = db.func.now()  # Update timestamp
    
    db.commit()
    
    return {
        "content_id": content_id,
        "title": ai_result.get("title", ""),
        "content": ai_result.get("content", ""),
        "word_count": ai_result.get("word_count", 0),
        "hashtags": ai_result.get("hashtags", []),
        "content_type": original_content.content_type
    }

@router.delete("/{content_id}")
async def delete_generated_content(
    content_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Delete generated content"""
    
    try:
        content_uuid = uuid.UUID(content_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid content ID")
    
    content = db.query(models.GeneratedContent).filter(
        models.GeneratedContent.id == content_uuid,
        models.GeneratedContent.user_id == current_user.id
    ).first()
    
    if not content:
        raise HTTPException(status_code=404, detail="Content not found")
    
    db.delete(content)
    db.commit()
    
    return {"message": "Content deleted successfully"}

@router.get("/templates/suggestions")
async def get_content_type_suggestions():
    """Get available content types and their descriptions"""
    
    return {
        "content_types": [
            {
                "type": "blog_post",
                "name": "Travel Blog Post",
                "description": "Detailed, engaging blog post about your travel experience",
                "length": "800-1200 words",
                "best_for": "Personal blogs, travel websites"
            },
            {
                "type": "social_media",
                "name": "Social Media Post",
                "description": "Short, catchy post perfect for Instagram, Facebook, or Twitter",
                "length": "50-280 characters",
                "best_for": "Instagram, Facebook, Twitter"
            },
            {
                "type": "trip_summary",
                "name": "Trip Summary",
                "description": "Comprehensive summary of your entire trip",
                "length": "400-600 words",
                "best_for": "Trip reports, sharing with friends"
            },
            {
                "type": "itinerary_narrative",
                "name": "Itinerary Story",
                "description": "Day-by-day narrative of your itinerary",
                "length": "200-400 words per day",
                "best_for": "Travel guides, detailed itineraries"
            }
        ],
        "tones": [
            {"value": "casual", "name": "Casual & Friendly"},
            {"value": "professional", "name": "Professional & Informative"},
            {"value": "humorous", "name": "Humorous & Entertaining"},
            {"value": "poetic", "name": "Poetic & Inspiring"},
            {"value": "enthusiastic", "name": "Enthusiastic & Excited"}
        ],
        "audiences": [
            {"value": "general travelers", "name": "General Travelers"},
            {"value": "budget travelers", "name": "Budget Travelers"},
            {"value": "luxury travelers", "name": "Luxury Travelers"},
            {"value": "solo travelers", "name": "Solo Travelers"},
            {"value": "family travelers", "name": "Family Travelers"},
            {"value": "adventure seekers", "name": "Adventure Seekers"},
            {"value": "cultural enthusiasts", "name": "Cultural Enthusiasts"}
        ]
    }