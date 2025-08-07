from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List, Dict
from datetime import datetime, timedelta
import uuid
import logging

from app import models
from app.database import get_db
from app.api.v1.auth import get_current_user
from app.core.claude_ai import ClaudeAIService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/events", tags=["AI-Powered Events & Activities"])

claude_service = ClaudeAIService()

# Event models
class EventCreate(BaseModel):
    city_id: int
    name: str
    description: str
    event_type: str
    start_date: datetime
    end_date: Optional[datetime] = None
    venue_name: Optional[str] = None
    venue_address: Optional[str] = None
    price_range: Optional[str] = None
    booking_url: Optional[str] = None
    source_url: Optional[str] = None
    is_recurring: bool = False

class EventRecommendationRequest(BaseModel):
    city_id: int
    travel_dates: List[str]
    interests: List[str] = []
    budget: str = "moderate"
    travel_style: str = "balanced"
    group_size: int = 1

@router.post("/add")
async def add_event(
    event: EventCreate,
    db: Session = Depends(get_db)
):
    """Add a new event (admin/curator function)"""
    
    # Verify city exists
    city = db.query(models.City).filter(models.City.id == event.city_id).first()
    if not city:
        raise HTTPException(status_code=404, detail="City not found")
    
    new_event = models.Event(
        city_id=event.city_id,
        name=event.name,
        description=event.description,
        event_type=event.event_type,
        start_date=event.start_date,
        end_date=event.end_date,
        venue_name=event.venue_name,
        venue_address=event.venue_address,
        price_range=event.price_range,
        booking_url=event.booking_url,
        source_url=event.source_url,
        is_recurring=event.is_recurring
    )
    
    db.add(new_event)
    db.commit()
    db.refresh(new_event)
    
    return {
        "id": str(new_event.id),
        "message": "Event added successfully"
    }

@router.get("/city/{city_id}")
async def get_city_events(
    city_id: int,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    event_type: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get events for a specific city"""
    
    query = db.query(models.Event).filter(models.Event.city_id == city_id)
    
    # Filter by date range
    if start_date:
        try:
            start_dt = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
            query = query.filter(models.Event.start_date >= start_dt)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid start_date format")
    
    if end_date:
        try:
            end_dt = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
            query = query.filter(models.Event.end_date <= end_dt)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid end_date format")
    
    # Filter by event type
    if event_type:
        query = query.filter(models.Event.event_type.ilike(f"%{event_type}%"))
    
    events = query.order_by(models.Event.start_date).limit(100).all()
    
    return [
        {
            "id": str(event.id),
            "name": event.name,
            "description": event.description,
            "event_type": event.event_type,
            "start_date": event.start_date,
            "end_date": event.end_date,
            "venue_name": event.venue_name,
            "venue_address": event.venue_address,
            "price_range": event.price_range,
            "booking_url": event.booking_url,
            "local_popularity_score": event.local_popularity_score,
            "tourist_friendly_score": event.tourist_friendly_score,
            "is_recurring": event.is_recurring
        }
        for event in events
    ]

@router.post("/recommendations")
async def get_personalized_event_recommendations(
    request: EventRecommendationRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Get AI-powered personalized event recommendations"""
    
    try:
        # Get city information
        city = db.query(models.City).filter(models.City.id == request.city_id).first()
        if not city:
            raise HTTPException(status_code=404, detail="City not found")
        
        # Parse travel dates
        travel_start = datetime.fromisoformat(request.travel_dates[0].replace('Z', '+00:00'))
        travel_end = datetime.fromisoformat(request.travel_dates[-1].replace('Z', '+00:00'))
        
        # Get available events during travel period
        available_events = db.query(models.Event).filter(
            models.Event.city_id == request.city_id,
            models.Event.start_date >= travel_start - timedelta(days=1),
            models.Event.start_date <= travel_end + timedelta(days=1)
        ).all()
        
        # Prepare event data for AI
        events_for_ai = [
            {
                "id": str(event.id),
                "name": event.name,
                "description": event.description,
                "event_type": event.event_type,
                "start_date": event.start_date.isoformat(),
                "venue": event.venue_name,
                "price_range": event.price_range
            }
            for event in available_events
        ]
        
        # Get user preferences
        user_preferences = {
            "interests": request.interests,
            "budget": request.budget,
            "travel_style": request.travel_style,
            "group_size": request.group_size
        }
        
        # Get AI recommendations
        ai_recommendations = await claude_service.recommend_events(
            user_preferences,
            events_for_ai,
            city.name,
            request.travel_dates
        )
        
        if "error" in ai_recommendations:
            raise HTTPException(status_code=500, detail=ai_recommendations["error"])
        
        # Process and save recommendations
        recommendations_to_save = []
        for rec in ai_recommendations.get("recommendations", []):
            event_id = rec.get("event_id")
            if event_id:
                try:
                    event_uuid = uuid.UUID(event_id)
                    
                    # Save recommendation to database
                    recommendation = models.EventRecommendation(
                        user_id=current_user.id,
                        event_id=event_uuid,
                        recommendation_reason=rec.get("reason", ""),
                        relevance_score=rec.get("relevance_score", 0.5),
                        user_interest_tags=request.interests
                    )
                    db.add(recommendation)
                    recommendations_to_save.append(recommendation)
                    
                except ValueError:
                    logger.warning(f"Invalid event ID in recommendation: {event_id}")
        
        if recommendations_to_save:
            db.commit()
        
        return {
            "city": city.name,
            "travel_dates": request.travel_dates,
            "total_events_found": len(available_events),
            "recommendations": ai_recommendations.get("recommendations", []),
            "general_advice": ai_recommendations.get("general_advice", ""),
            "generated_at": datetime.utcnow()
        }
        
    except Exception as e:
        logger.error(f"Event recommendation error: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate event recommendations")

@router.get("/my-recommendations")
async def get_user_event_recommendations(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Get user's saved event recommendations"""
    
    recommendations = db.query(
        models.EventRecommendation, 
        models.Event,
        models.City
    ).join(
        models.Event, models.EventRecommendation.event_id == models.Event.id
    ).join(
        models.City, models.Event.city_id == models.City.id
    ).filter(
        models.EventRecommendation.user_id == current_user.id
    ).order_by(
        models.EventRecommendation.recommended_at.desc()
    ).limit(50).all()
    
    return [
        {
            "recommendation_id": str(rec.EventRecommendation.id),
            "event": {
                "id": str(rec.Event.id),
                "name": rec.Event.name,
                "description": rec.Event.description,
                "event_type": rec.Event.event_type,
                "start_date": rec.Event.start_date,
                "venue_name": rec.Event.venue_name,
                "price_range": rec.Event.price_range,
                "booking_url": rec.Event.booking_url
            },
            "city": rec.City.name,
            "recommendation_reason": rec.EventRecommendation.recommendation_reason,
            "relevance_score": rec.EventRecommendation.relevance_score,
            "user_interest_tags": rec.EventRecommendation.user_interest_tags,
            "recommended_at": rec.EventRecommendation.recommended_at,
            "user_response": rec.EventRecommendation.user_response
        }
        for rec in recommendations
    ]

@router.post("/recommendations/{recommendation_id}/respond")
async def respond_to_recommendation(
    recommendation_id: str,
    response: str,  # interested, not_interested, attended
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Respond to an event recommendation"""
    
    try:
        rec_uuid = uuid.UUID(recommendation_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid recommendation ID")
    
    recommendation = db.query(models.EventRecommendation).filter(
        models.EventRecommendation.id == rec_uuid,
        models.EventRecommendation.user_id == current_user.id
    ).first()
    
    if not recommendation:
        raise HTTPException(status_code=404, detail="Recommendation not found")
    
    if response not in ["interested", "not_interested", "attended"]:
        raise HTTPException(
            status_code=400, 
            detail="Response must be 'interested', 'not_interested', or 'attended'"
        )
    
    recommendation.user_response = response
    db.commit()
    
    return {"message": f"Response '{response}' recorded successfully"}

@router.get("/types")
async def get_event_types(db: Session = Depends(get_db)):
    """Get available event types"""
    
    # Get unique event types from database
    event_types = db.query(models.Event.event_type).distinct().all()
    
    types_list = [event_type[0] for event_type in event_types if event_type[0]]
    
    # Add common event types if database is empty
    if not types_list:
        types_list = [
            "festival", "concert", "exhibition", "market", "theater",
            "sports", "conference", "workshop", "tour", "celebration",
            "food-event", "nightlife", "cultural", "outdoor", "family"
        ]
    
    return {
        "event_types": sorted(set(types_list)),
        "popular_types": [
            {"type": "festival", "description": "Local festivals and celebrations"},
            {"type": "concert", "description": "Musical performances and shows"},
            {"type": "exhibition", "description": "Art galleries and museum exhibitions"},
            {"type": "market", "description": "Local markets and food events"},
            {"type": "cultural", "description": "Cultural events and traditions"},
            {"type": "outdoor", "description": "Outdoor activities and nature events"}
        ]
    }

@router.get("/search")
async def search_events(
    q: str,
    city_id: Optional[int] = None,
    event_type: Optional[str] = None,
    days_ahead: int = 30,
    db: Session = Depends(get_db)
):
    """Search events by name, description, or venue"""
    
    query = db.query(models.Event, models.City).join(
        models.City, models.Event.city_id == models.City.id
    ).filter(
        models.Event.start_date >= datetime.utcnow(),
        models.Event.start_date <= datetime.utcnow() + timedelta(days=days_ahead)
    )
    
    # Text search
    search_term = f"%{q.lower()}%"
    query = query.filter(
        models.Event.name.ilike(search_term) |
        models.Event.description.ilike(search_term) |
        models.Event.venue_name.ilike(search_term)
    )
    
    if city_id:
        query = query.filter(models.Event.city_id == city_id)
    
    if event_type:
        query = query.filter(models.Event.event_type.ilike(f"%{event_type}%"))
    
    results = query.order_by(models.Event.start_date).limit(50).all()
    
    return [
        {
            "id": str(result.Event.id),
            "name": result.Event.name,
            "description": result.Event.description,
            "event_type": result.Event.event_type,
            "start_date": result.Event.start_date,
            "city": result.City.name,
            "venue_name": result.Event.venue_name,
            "price_range": result.Event.price_range,
            "booking_url": result.Event.booking_url
        }
        for result in results
    ]

@router.post("/discover")
async def discover_events_with_ai(
    location: str,
    interests: List[str] = [],
    db: Session = Depends(get_db)
):
    """Use AI to discover and suggest events based on interests and location"""
    
    try:
        # Find city
        city = db.query(models.City).filter(
            models.City.name.ilike(f"%{location}%")
        ).first()
        
        if not city:
            raise HTTPException(status_code=404, detail=f"City '{location}' not found")
        
        # Get upcoming events
        upcoming_events = db.query(models.Event).filter(
            models.Event.city_id == city.id,
            models.Event.start_date >= datetime.utcnow(),
            models.Event.start_date <= datetime.utcnow() + timedelta(days=60)
        ).limit(50).all()
        
        # Use AI to suggest event discovery strategies
        prompt = f"""Suggest creative ways to discover events and activities in {city.name}, France.
        
        User interests: {', '.join(interests) if interests else 'General travel'}
        
        Provide:
        1. Specific local event sources and websites
        2. Types of events that match these interests
        3. Best times to visit for events
        4. Local event discovery tips
        5. Hidden event gems that tourists miss
        
        Make it practical and actionable for travelers."""
        
        ai_suggestions = await claude_service.general_ai_assistance(
            prompt,
            {"location": city.name, "interests": interests},
            "event_curator"
        )
        
        return {
            "location": city.name,
            "current_events_count": len(upcoming_events),
            "user_interests": interests,
            "ai_discovery_guide": ai_suggestions,
            "current_events": [
                {
                    "id": str(event.id),
                    "name": event.name,
                    "event_type": event.event_type,
                    "start_date": event.start_date,
                    "description": event.description[:200] + "..." if len(event.description) > 200 else event.description
                }
                for event in upcoming_events[:10]
            ]
        }
        
    except Exception as e:
        logger.error(f"Event discovery error: {e}")
        raise HTTPException(status_code=500, detail="Failed to discover events")