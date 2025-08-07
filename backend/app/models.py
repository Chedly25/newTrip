from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, ForeignKey, JSON, ARRAY, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from geoalchemy2 import Geography
import uuid
from datetime import datetime

from app.database import Base

class City(Base):
    __tablename__ = "cities"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    region = Column(String(100))
    department = Column(String(100))
    country = Column(String(100), default="France")
    country_code = Column(String(2), default="FR")
    center_point = Column(Geography(geometry_type='POINT', srid=4326))
    population = Column(Integer)
    local_subreddits = Column(ARRAY(Text))
    local_instagram_tags = Column(ARRAY(Text))
    tourist_season = Column(String(50))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    places = relationship("Place", back_populates="city")

class Place(Base):
    __tablename__ = "places"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    city_id = Column(Integer, ForeignKey("cities.id"))
    name = Column(String(255), nullable=False)
    category = Column(String(50))
    subcategory = Column(String(100))
    location = Column(Geography(geometry_type='POINT', srid=4326))
    address = Column(Text)
    arrondissement = Column(String(50))
    metro_station = Column(String(100))
    price_level = Column(Integer)
    michelin_stars = Column(Integer, default=0)
    opening_hours = Column(JSON)
    local_tips = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    city = relationship("City", back_populates="places")
    gem_scores = relationship("GemScore", back_populates="place")
    mentions = relationship("Mention", back_populates="place")

class GemScore(Base):
    __tablename__ = "gem_scores"
    
    id = Column(Integer, primary_key=True)
    place_id = Column(UUID(as_uuid=True), ForeignKey("places.id"))
    score_date = Column(DateTime, default=datetime.utcnow)
    hidden_gem_score = Column(Float)
    trending_score = Column(Float)
    authenticity_score = Column(Float)
    tourism_saturation = Column(Float)
    local_mentions_7d = Column(Integer)
    
    # Relationships
    place = relationship("Place", back_populates="gem_scores")

class User(Base):
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False)
    hashed_password = Column(String(255))
    full_name = Column(String(255))
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    itineraries = relationship("Itinerary", back_populates="user")

class Itinerary(Base):
    __tablename__ = "itineraries"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    city_id = Column(Integer, ForeignKey("cities.id"))
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    preferences = Column(JSON)
    generated_plan = Column(JSON)
    ai_suggestions = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="itineraries")

class Mention(Base):
    __tablename__ = "mentions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    place_id = Column(UUID(as_uuid=True), ForeignKey("places.id"))
    source_type = Column(String(50))
    source_url = Column(Text)
    mention_text = Column(Text)
    mention_date = Column(DateTime)
    is_local_author = Column(Boolean, default=False)
    sentiment_score = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    place = relationship("Place", back_populates="mentions")