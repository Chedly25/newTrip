from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional

from app import models, schemas
from app.database import get_db
from app.core.cache import cache_key_wrapper

router = APIRouter(prefix="/cities", tags=["cities"])

@router.get("/", response_model=List[schemas.City])
@cache_key_wrapper("cities", 3600)
async def get_cities(
    db: Session = Depends(get_db),
    region: Optional[str] = None
):
    """Get all French cities with statistics"""
    
    query = db.query(
        models.City,
        func.count(models.Place.id).label("place_count")
    ).outerjoin(models.Place).group_by(models.City.id)
    
    if region:
        query = query.filter(models.City.region == region)
    
    cities = query.all()
    
    return [
        {
            "id": city.City.id,
            "name": city.City.name,
            "region": city.City.region,
            "department": city.City.department,
            "population": city.City.population,
            "place_count": city.place_count,
            "tourist_season": city.City.tourist_season
        }
        for city in cities
    ]

@router.get("/{city_id}/gems")
async def get_city_gems(
    city_id: int,
    db: Session = Depends(get_db),
    category: Optional[str] = None,
    min_score: float = Query(20.0, ge=0, le=100),
    limit: int = Query(30, ge=1, le=100)
):
    """Get hidden gems for a city"""
    
    query = db.query(
        models.Place,
        models.GemScore
    ).join(
        models.GemScore
    ).filter(
        models.Place.city_id == city_id,
        models.GemScore.hidden_gem_score >= min_score
    )
    
    if category:
        query = query.filter(models.Place.category == category)
    
    query = query.order_by(
        models.GemScore.authenticity_score.desc(),
        models.GemScore.hidden_gem_score.desc()
    ).limit(limit)
    
    results = query.all()
    
    gems = []
    for place, score in results:
        gem = {
            "id": str(place.id),
            "name": place.name,
            "category": place.category,
            "subcategory": place.subcategory,
            "address": place.address,
            "arrondissement": place.arrondissement,
            "metro_station": place.metro_station,
            "price_level": place.price_level,
            "hidden_gem_score": score.hidden_gem_score,
            "authenticity_score": score.authenticity_score,
            "trending_score": score.trending_score,
            "local_mentions_7d": score.local_mentions_7d,
            "local_tips": place.local_tips
        }
        gems.append(gem)
    
    return {
        "city_id": city_id,
        "total_gems": len(gems),
        "gems": gems
    }

@router.get("/{city_id}")
async def get_city(city_id: int, db: Session = Depends(get_db)):
    """Get city details"""
    
    city = db.query(models.City).filter(models.City.id == city_id).first()
    
    if not city:
        raise HTTPException(status_code=404, detail="City not found")
    
    place_count = db.query(models.Place).filter(models.Place.city_id == city_id).count()
    
    return {
        "id": city.id,
        "name": city.name,
        "region": city.region,
        "department": city.department,
        "population": city.population,
        "place_count": place_count,
        "tourist_season": city.tourist_season
    }