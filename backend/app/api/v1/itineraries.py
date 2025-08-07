from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import uuid

from app import models, schemas
from app.database import get_db
from app.api.v1.auth import get_current_user
from app.core.claude_ai import ClaudeAIService

router = APIRouter(prefix="/itineraries", tags=["itineraries"])
claude_service = ClaudeAIService()

@router.post("/", response_model=schemas.Itinerary)
async def create_itinerary(
    itinerary: schemas.ItineraryCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Create a new itinerary with AI suggestions"""
    
    # Get city gems for itinerary
    gems_query = db.query(models.Place, models.GemScore).join(models.GemScore).filter(
        models.Place.city_id == itinerary.city_id,
        models.GemScore.hidden_gem_score >= 30
    ).order_by(models.GemScore.authenticity_score.desc()).limit(20)
    
    gems = gems_query.all()
    
    # Format places for AI
    places_data = []
    for place, score in gems:
        places_data.append({
            "id": str(place.id),
            "name": place.name,
            "category": place.category,
            "address": place.address,
            "authenticity_score": score.authenticity_score,
            "local_tips": place.local_tips
        })
    
    # Generate AI suggestions
    ai_narrative = await claude_service.generate_itinerary_narrative(
        places_data,
        itinerary.preferences
    )
    
    # Create itinerary
    db_itinerary = models.Itinerary(
        id=uuid.uuid4(),
        user_id=current_user.id,
        city_id=itinerary.city_id,
        start_date=itinerary.start_date,
        end_date=itinerary.end_date,
        preferences=itinerary.preferences,
        generated_plan={"places": places_data},
        ai_suggestions={"narrative": ai_narrative}
    )
    
    db.add(db_itinerary)
    db.commit()
    db.refresh(db_itinerary)
    
    return db_itinerary

@router.get("/", response_model=List[schemas.Itinerary])
async def get_user_itineraries(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Get all itineraries for current user"""
    
    itineraries = db.query(models.Itinerary).filter(
        models.Itinerary.user_id == current_user.id
    ).order_by(models.Itinerary.created_at.desc()).all()
    
    return itineraries

@router.get("/{itinerary_id}", response_model=schemas.Itinerary)
async def get_itinerary(
    itinerary_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Get specific itinerary"""
    
    try:
        itinerary_uuid = uuid.UUID(itinerary_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid itinerary ID format")
    
    itinerary = db.query(models.Itinerary).filter(
        models.Itinerary.id == itinerary_uuid,
        models.Itinerary.user_id == current_user.id
    ).first()
    
    if not itinerary:
        raise HTTPException(status_code=404, detail="Itinerary not found")
    
    return itinerary

@router.delete("/{itinerary_id}")
async def delete_itinerary(
    itinerary_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Delete itinerary"""
    
    try:
        itinerary_uuid = uuid.UUID(itinerary_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid itinerary ID format")
    
    itinerary = db.query(models.Itinerary).filter(
        models.Itinerary.id == itinerary_uuid,
        models.Itinerary.user_id == current_user.id
    ).first()
    
    if not itinerary:
        raise HTTPException(status_code=404, detail="Itinerary not found")
    
    db.delete(itinerary)
    db.commit()
    
    return {"message": "Itinerary deleted"}