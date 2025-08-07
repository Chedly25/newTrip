from pydantic import BaseModel, EmailStr
from typing import Optional, List, Dict, Any
from datetime import datetime
import uuid

class CityBase(BaseModel):
    name: str
    region: Optional[str] = None
    department: Optional[str] = None
    country: str = "France"
    population: Optional[int] = None

class City(CityBase):
    id: int
    place_count: Optional[int] = 0
    tourist_season: Optional[str] = None
    
    class Config:
        from_attributes = True

class PlaceBase(BaseModel):
    name: str
    category: Optional[str] = None
    subcategory: Optional[str] = None
    address: Optional[str] = None
    price_level: Optional[int] = None

class Place(PlaceBase):
    id: str
    city_id: int
    arrondissement: Optional[str] = None
    metro_station: Optional[str] = None
    michelin_stars: Optional[int] = 0
    local_tips: Optional[Dict] = None
    
    class Config:
        from_attributes = True

class GemScore(BaseModel):
    hidden_gem_score: float
    authenticity_score: float
    trending_score: Optional[float] = None
    local_mentions_7d: int
    
    class Config:
        from_attributes = True

class PlaceWithScore(Place):
    gem_score: Optional[GemScore] = None

class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: str
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

class ChatMessage(BaseModel):
    message: str
    conversation_id: Optional[str] = None
    context: Optional[Dict] = {}

class ChatResponse(BaseModel):
    conversation_id: str
    response: str

class ItineraryCreate(BaseModel):
    city_id: int
    start_date: datetime
    end_date: datetime
    preferences: Dict[str, Any]

class Itinerary(BaseModel):
    id: str
    user_id: str
    city_id: int
    start_date: datetime
    end_date: datetime
    preferences: Dict[str, Any]
    generated_plan: Optional[Dict] = None
    ai_suggestions: Optional[Dict] = None
    
    class Config:
        from_attributes = True