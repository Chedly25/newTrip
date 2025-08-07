from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
import uuid

from app import models, schemas
from app.database import get_db

router = APIRouter(prefix="/places", tags=["places"])

@router.get("/{place_id}")
async def get_place(place_id: str, db: Session = Depends(get_db)):
    """Get place details with latest scores"""
    
    try:
        place_uuid = uuid.UUID(place_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid place ID format")
    
    place = db.query(models.Place).filter(models.Place.id == place_uuid).first()
    
    if not place:
        raise HTTPException(status_code=404, detail="Place not found")
    
    # Get latest gem score
    latest_score = db.query(models.GemScore).filter(
        models.GemScore.place_id == place_uuid
    ).order_by(models.GemScore.score_date.desc()).first()
    
    # Get recent mentions
    recent_mentions = db.query(models.Mention).filter(
        models.Mention.place_id == place_uuid
    ).order_by(models.Mention.mention_date.desc()).limit(5).all()
    
    return {
        "id": str(place.id),
        "name": place.name,
        "category": place.category,
        "subcategory": place.subcategory,
        "address": place.address,
        "arrondissement": place.arrondissement,
        "metro_station": place.metro_station,
        "price_level": place.price_level,
        "michelin_stars": place.michelin_stars,
        "local_tips": place.local_tips,
        "gem_score": {
            "hidden_gem_score": latest_score.hidden_gem_score if latest_score else 0,
            "authenticity_score": latest_score.authenticity_score if latest_score else 0,
            "trending_score": latest_score.trending_score if latest_score else 0,
            "local_mentions_7d": latest_score.local_mentions_7d if latest_score else 0
        } if latest_score else None,
        "recent_mentions": [
            {
                "source_type": mention.source_type,
                "mention_text": mention.mention_text[:200] + "..." if len(mention.mention_text) > 200 else mention.mention_text,
                "sentiment_score": mention.sentiment_score,
                "is_local": mention.is_local_author,
                "date": mention.mention_date
            }
            for mention in recent_mentions
        ]
    }

@router.get("/search/")
async def search_places(
    q: str,
    city_id: Optional[int] = None,
    category: Optional[str] = None,
    limit: int = 20,
    db: Session = Depends(get_db)
):
    """Search places by name or description"""
    
    query = db.query(models.Place).filter(
        models.Place.name.ilike(f"%{q}%")
    )
    
    if city_id:
        query = query.filter(models.Place.city_id == city_id)
    
    if category:
        query = query.filter(models.Place.category == category)
    
    places = query.limit(limit).all()
    
    return [
        {
            "id": str(place.id),
            "name": place.name,
            "category": place.category,
            "address": place.address,
            "city_id": place.city_id
        }
        for place in places
    ]