from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, ForeignKey, JSON, ARRAY, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
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
    latitude = Column(Float)
    longitude = Column(Float)
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
    latitude = Column(Float)
    longitude = Column(Float)
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

# =============================================================================
# NEW AI-POWERED FEATURES MODELS
# =============================================================================

# Feature 1: AI Travel Companion Chat
class Conversation(Base):
    __tablename__ = "conversations"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    session_id = Column(String(255))
    conversation_type = Column(String(50), default="travel_companion")  # travel_companion, trip_planner, food_guide
    context_location = Column(String(255))  # Current city/region
    context_data = Column(JSON)  # User preferences, current trip info
    created_at = Column(DateTime, default=datetime.utcnow)
    last_activity = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    messages = relationship("ConversationMessage", back_populates="conversation")

class ConversationMessage(Base):
    __tablename__ = "conversation_messages"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    conversation_id = Column(UUID(as_uuid=True), ForeignKey("conversations.id"))
    role = Column(String(20))  # user, assistant, system
    content = Column(Text)
    message_metadata = Column(JSON)  # Additional context, function calls, etc.
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    conversation = relationship("Conversation", back_populates="messages")

# Feature 2: Smart Photo Analysis & Place Recognition
class PhotoUpload(Base):
    __tablename__ = "photo_uploads"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    file_path = Column(String(500))
    file_name = Column(String(255))
    file_size = Column(Integer)
    mime_type = Column(String(100))
    latitude = Column(Float)
    longitude = Column(Float)
    ai_analysis_status = Column(String(50), default="pending")  # pending, processing, completed, failed
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    analysis_results = relationship("PhotoAnalysis", back_populates="photo")

class PhotoAnalysis(Base):
    __tablename__ = "photo_analysis"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    photo_id = Column(UUID(as_uuid=True), ForeignKey("photo_uploads.id"))
    identified_places = Column(JSON)  # List of recognized places/landmarks
    suggested_locations = Column(JSON)  # Similar places Claude suggests
    cultural_context = Column(Text)  # Historical/cultural information
    photography_tips = Column(Text)  # Claude's photography advice
    local_insights = Column(Text)  # Local knowledge about the area
    confidence_score = Column(Float)
    analysis_timestamp = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    photo = relationship("PhotoUpload", back_populates="analysis_results")

# Feature 3: AI Content Generator for Travel
class GeneratedContent(Base):
    __tablename__ = "generated_content"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    content_type = Column(String(50))  # blog_post, social_media, trip_summary, itinerary_narrative
    title = Column(String(500))
    content = Column(Text)
    prompt_used = Column(Text)
    target_audience = Column(String(100))
    tone = Column(String(50))  # casual, professional, humorous, poetic
    language = Column(String(10), default="en")
    related_places = Column(ARRAY(String))
    related_trip_id = Column(UUID(as_uuid=True), ForeignKey("itineraries.id"), nullable=True)
    word_count = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)

# Feature 4: Intelligent Expense Tracker & Budget Advisor
class ExpenseCategory(Base):
    __tablename__ = "expense_categories"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    icon = Column(String(50))
    color = Column(String(20))
    default_budget_percentage = Column(Float)  # Suggested % of total budget

class Expense(Base):
    __tablename__ = "expenses"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    trip_id = Column(UUID(as_uuid=True), ForeignKey("itineraries.id"), nullable=True)
    category_id = Column(Integer, ForeignKey("expense_categories.id"))
    amount = Column(Float)
    currency = Column(String(3), default="EUR")
    description = Column(String(255))
    location = Column(String(255))
    expense_date = Column(DateTime)
    receipt_photo = Column(String(500))  # File path
    is_shared_expense = Column(Boolean, default=False)
    split_count = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.utcnow)

class BudgetAnalysis(Base):
    __tablename__ = "budget_analysis"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    trip_id = Column(UUID(as_uuid=True), ForeignKey("itineraries.id"), nullable=True)
    total_budget = Column(Float)
    total_spent = Column(Float)
    currency = Column(String(3), default="EUR")
    category_breakdown = Column(JSON)
    ai_insights = Column(Text)  # Claude's analysis and recommendations
    budget_alerts = Column(JSON)  # Overspending warnings, recommendations
    money_saving_tips = Column(Text)
    analysis_date = Column(DateTime, default=datetime.utcnow)

# Feature 5: AI-Powered Local Events & Activities Finder
class Event(Base):
    __tablename__ = "events"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    city_id = Column(Integer, ForeignKey("cities.id"))
    name = Column(String(255), nullable=False)
    description = Column(Text)
    event_type = Column(String(100))  # festival, concert, exhibition, market, etc.
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    latitude = Column(Float)
    longitude = Column(Float)
    venue_name = Column(String(255))
    venue_address = Column(Text)
    price_range = Column(String(50))
    booking_url = Column(String(500))
    source_url = Column(String(500))
    is_recurring = Column(Boolean, default=False)
    local_popularity_score = Column(Float)
    tourist_friendly_score = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)

class EventRecommendation(Base):
    __tablename__ = "event_recommendations"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    event_id = Column(UUID(as_uuid=True), ForeignKey("events.id"))
    trip_id = Column(UUID(as_uuid=True), ForeignKey("itineraries.id"), nullable=True)
    recommendation_reason = Column(Text)  # Claude's explanation
    relevance_score = Column(Float)
    user_interest_tags = Column(ARRAY(String))
    recommended_at = Column(DateTime, default=datetime.utcnow)
    user_response = Column(String(20))  # interested, not_interested, attended

# Feature 6: Smart Translation & Cultural Context
class TranslationRequest(Base):
    __tablename__ = "translation_requests"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    source_text = Column(Text)
    source_language = Column(String(10))
    target_language = Column(String(10))
    translated_text = Column(Text)
    cultural_context = Column(Text)  # Claude's cultural explanation
    usage_tips = Column(Text)  # When and how to use this phrase
    formality_level = Column(String(20))  # formal, informal, casual
    context_type = Column(String(50))  # restaurant, hotel, emergency, shopping, etc.
    confidence_score = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)

class CulturalInsight(Base):
    __tablename__ = "cultural_insights"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    city_id = Column(Integer, ForeignKey("cities.id"))
    category = Column(String(100))  # etiquette, traditions, customs, holidays, etc.
    title = Column(String(255))
    insight = Column(Text)
    practical_tips = Column(Text)
    do_dont_list = Column(JSON)
    relevance_level = Column(String(20))  # essential, helpful, interesting
    source_type = Column(String(50), default="ai_generated")
    created_at = Column(DateTime, default=datetime.utcnow)

# Feature 7: AI Review Analyzer & Sentiment Insights
class ReviewAnalysis(Base):
    __tablename__ = "review_analysis"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    place_id = Column(UUID(as_uuid=True), ForeignKey("places.id"))
    platform = Column(String(50))  # google, tripadvisor, yelp, etc.
    total_reviews_analyzed = Column(Integer)
    average_sentiment = Column(Float)
    positive_themes = Column(JSON)  # Array of common positive mentions
    negative_themes = Column(JSON)  # Array of common complaints
    local_vs_tourist_breakdown = Column(JSON)
    seasonal_patterns = Column(JSON)
    ai_summary = Column(Text)  # Claude's overall assessment
    authenticity_indicators = Column(JSON)
    recommendation_confidence = Column(Float)
    analysis_date = Column(DateTime, default=datetime.utcnow)

class PlaceReview(Base):
    __tablename__ = "place_reviews"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    place_id = Column(UUID(as_uuid=True), ForeignKey("places.id"))
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    rating = Column(Float)
    review_text = Column(Text)
    visit_date = Column(DateTime)
    reviewer_type = Column(String(20))  # local, tourist, business_traveler
    sentiment_score = Column(Float)
    authenticity_score = Column(Float)
    helpfulness_votes = Column(Integer, default=0)
    verified_visit = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

# Feature 8: Personalized Food & Restaurant AI Recommendations
class FoodPreference(Base):
    __tablename__ = "food_preferences"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    dietary_restrictions = Column(ARRAY(String))  # vegetarian, vegan, gluten-free, etc.
    cuisine_preferences = Column(JSON)  # Liked/disliked cuisines with weights
    spice_tolerance = Column(String(20))  # mild, medium, hot, extreme
    price_range_preference = Column(JSON)  # Budget distribution preferences
    meal_type_preferences = Column(JSON)  # breakfast, lunch, dinner, snacks
    adventure_level = Column(String(20))  # conservative, moderate, adventurous
    allergies = Column(ARRAY(String))
    favorite_ingredients = Column(ARRAY(String))
    disliked_ingredients = Column(ARRAY(String))
    updated_at = Column(DateTime, default=datetime.utcnow)

class RestaurantRecommendation(Base):
    __tablename__ = "restaurant_recommendations"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    place_id = Column(UUID(as_uuid=True), ForeignKey("places.id"))
    recommendation_reason = Column(Text)  # Claude's personalized explanation
    match_score = Column(Float)  # How well it matches user preferences
    dish_recommendations = Column(JSON)  # Specific dishes to try
    dining_tips = Column(Text)  # When to go, what to expect
    price_estimate = Column(JSON)  # Estimated cost per person
    reservation_difficulty = Column(String(20))  # easy, moderate, hard
    local_authenticity = Column(Float)
    recommended_at = Column(DateTime, default=datetime.utcnow)

# Feature 9: AI Travel Risk Assessment & Safety Advisor
class SafetyAssessment(Base):
    __tablename__ = "safety_assessments"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    city_id = Column(Integer, ForeignKey("cities.id"))
    assessment_date = Column(DateTime, default=datetime.utcnow)
    overall_safety_score = Column(Float)  # 1-10 scale
    crime_risk = Column(JSON)  # Different types of crime risks
    health_alerts = Column(JSON)  # Current health concerns
    natural_disaster_risk = Column(JSON)
    political_stability = Column(Float)
    tourist_specific_risks = Column(JSON)
    transportation_safety = Column(JSON)
    emergency_contacts = Column(JSON)
    safe_areas = Column(JSON)  # Recommended safe neighborhoods
    areas_to_avoid = Column(JSON)
    safety_tips = Column(Text)  # Claude's personalized advice
    data_sources = Column(ARRAY(String))
    confidence_level = Column(Float)

class TravelAlert(Base):
    __tablename__ = "travel_alerts"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    city_id = Column(Integer, ForeignKey("cities.id"))
    alert_type = Column(String(50))  # weather, security, health, transport
    severity = Column(String(20))  # low, medium, high, critical
    title = Column(String(255))
    description = Column(Text)
    ai_impact_analysis = Column(Text)  # Claude's analysis of impact on travelers
    recommended_actions = Column(JSON)
    affected_areas = Column(JSON)
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    source = Column(String(100))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

# Feature 10: Enhanced AI Itinerary Planning
class ItineraryTemplate(Base):
    __tablename__ = "itinerary_templates"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255))
    description = Column(Text)
    city_id = Column(Integer, ForeignKey("cities.id"))
    duration_days = Column(Integer)
    traveler_type = Column(String(50))  # solo, couple, family, friends, business
    budget_level = Column(String(20))  # budget, mid-range, luxury
    interests = Column(ARRAY(String))
    template_data = Column(JSON)  # Full itinerary structure
    popularity_score = Column(Float)
    created_by_ai = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class ItineraryDay(Base):
    __tablename__ = "itinerary_days"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    itinerary_id = Column(UUID(as_uuid=True), ForeignKey("itineraries.id"))
    day_number = Column(Integer)
    theme = Column(String(100))  # e.g., "Historic Paris", "Foodie Adventures"
    activities = Column(JSON)  # Structured list of activities with times
    transport_suggestions = Column(JSON)
    meal_recommendations = Column(JSON)
    budget_estimate = Column(Float)
    ai_narrative = Column(Text)  # Claude's description of the day
    backup_activities = Column(JSON)  # Alternative options for weather/closures
    energy_level = Column(String(20))  # low, medium, high intensity day
    walking_distance = Column(Float)  # Estimated km of walking

# User Profile Extensions for AI Personalization
class UserTravelProfile(Base):
    __tablename__ = "user_travel_profiles"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    travel_style = Column(String(50))  # explorer, relaxer, cultural_immersion, adventure
    preferred_pace = Column(String(20))  # slow, moderate, fast
    group_preference = Column(String(20))  # solo, small_groups, large_groups
    accommodation_type = Column(ARRAY(String))
    transport_preferences = Column(JSON)
    activity_preferences = Column(JSON)  # Weights for different activity types
    cultural_interests = Column(ARRAY(String))
    language_skills = Column(JSON)  # Languages and proficiency levels
    accessibility_needs = Column(JSON)
    travel_experience_level = Column(String(20))  # beginner, intermediate, expert
    risk_tolerance = Column(String(20))  # low, medium, high
    sustainability_preference = Column(Float)  # 1-10 scale
    ai_learning_consent = Column(Boolean, default=True)
    updated_at = Column(DateTime, default=datetime.utcnow)