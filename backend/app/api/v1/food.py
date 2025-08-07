from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from pydantic import BaseModel
from typing import Optional, List, Dict
import uuid
import logging

from app import models
from app.database import get_db
from app.api.v1.auth import get_current_user
from app.core.claude_ai import ClaudeAIService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/food", tags=["Personalized Food & Restaurant AI"])

claude_service = ClaudeAIService()

# Food preference models
class FoodPreferencesCreate(BaseModel):
    dietary_restrictions: List[str] = []  # vegetarian, vegan, gluten-free, etc.
    cuisine_preferences: Dict[str, float] = {}  # cuisine: preference_weight (-1 to 1)
    spice_tolerance: str = "medium"  # mild, medium, hot, extreme
    price_range_preference: Dict[str, float] = {}  # budget distribution
    meal_type_preferences: Dict[str, float] = {}  # breakfast, lunch, dinner weights
    adventure_level: str = "moderate"  # conservative, moderate, adventurous
    allergies: List[str] = []
    favorite_ingredients: List[str] = []
    disliked_ingredients: List[str] = []

class RestaurantRecommendationRequest(BaseModel):
    city_id: int
    meal_type: str = "dinner"  # breakfast, lunch, dinner, snack
    budget_level: str = "moderate"  # budget, moderate, high-end, luxury
    special_occasion: bool = False
    group_size: int = 2
    preferred_time: Optional[str] = None

@router.post("/preferences")
async def set_food_preferences(
    preferences: FoodPreferencesCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Set or update user's food preferences"""
    
    # Check if preferences already exist
    existing_prefs = db.query(models.FoodPreference).filter(
        models.FoodPreference.user_id == current_user.id
    ).first()
    
    if existing_prefs:
        # Update existing preferences
        existing_prefs.dietary_restrictions = preferences.dietary_restrictions
        existing_prefs.cuisine_preferences = preferences.cuisine_preferences
        existing_prefs.spice_tolerance = preferences.spice_tolerance
        existing_prefs.price_range_preference = preferences.price_range_preference
        existing_prefs.meal_type_preferences = preferences.meal_type_preferences
        existing_prefs.adventure_level = preferences.adventure_level
        existing_prefs.allergies = preferences.allergies
        existing_prefs.favorite_ingredients = preferences.favorite_ingredients
        existing_prefs.disliked_ingredients = preferences.disliked_ingredients
        existing_prefs.updated_at = func.now()
        
        db.commit()
        food_prefs = existing_prefs
        
    else:
        # Create new preferences
        food_prefs = models.FoodPreference(
            user_id=current_user.id,
            dietary_restrictions=preferences.dietary_restrictions,
            cuisine_preferences=preferences.cuisine_preferences,
            spice_tolerance=preferences.spice_tolerance,
            price_range_preference=preferences.price_range_preference,
            meal_type_preferences=preferences.meal_type_preferences,
            adventure_level=preferences.adventure_level,
            allergies=preferences.allergies,
            favorite_ingredients=preferences.favorite_ingredients,
            disliked_ingredients=preferences.disliked_ingredients
        )
        
        db.add(food_prefs)
        db.commit()
        db.refresh(food_prefs)
    
    return {
        "id": str(food_prefs.id),
        "message": "Food preferences saved successfully",
        "preferences": {
            "dietary_restrictions": food_prefs.dietary_restrictions,
            "cuisine_preferences": food_prefs.cuisine_preferences,
            "spice_tolerance": food_prefs.spice_tolerance,
            "adventure_level": food_prefs.adventure_level,
            "allergies": food_prefs.allergies
        }
    }

@router.get("/preferences")
async def get_food_preferences(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Get user's food preferences"""
    
    preferences = db.query(models.FoodPreference).filter(
        models.FoodPreference.user_id == current_user.id
    ).first()
    
    if not preferences:
        return {
            "message": "No food preferences set",
            "default_preferences": {
                "dietary_restrictions": [],
                "cuisine_preferences": {"french": 0.8, "italian": 0.6, "mediterranean": 0.7},
                "spice_tolerance": "medium",
                "adventure_level": "moderate",
                "allergies": []
            }
        }
    
    return {
        "id": str(preferences.id),
        "dietary_restrictions": preferences.dietary_restrictions,
        "cuisine_preferences": preferences.cuisine_preferences,
        "spice_tolerance": preferences.spice_tolerance,
        "price_range_preference": preferences.price_range_preference,
        "meal_type_preferences": preferences.meal_type_preferences,
        "adventure_level": preferences.adventure_level,
        "allergies": preferences.allergies,
        "favorite_ingredients": preferences.favorite_ingredients,
        "disliked_ingredients": preferences.disliked_ingredients,
        "updated_at": preferences.updated_at
    }

@router.post("/recommendations")
async def get_restaurant_recommendations(
    request: RestaurantRecommendationRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Get AI-powered restaurant recommendations"""
    
    try:
        # Get city information
        city = db.query(models.City).filter(models.City.id == request.city_id).first()
        if not city:
            raise HTTPException(status_code=404, detail="City not found")
        
        # Get user's food preferences
        food_prefs = db.query(models.FoodPreference).filter(
            models.FoodPreference.user_id == current_user.id
        ).first()
        
        # Default preferences if none set
        preferences_dict = {
            "dietary_restrictions": [],
            "cuisine_preferences": {"french": 0.8},
            "spice_tolerance": "medium",
            "price_range_preference": {"moderate": 0.7},
            "adventure_level": "moderate",
            "allergies": []
        }
        
        if food_prefs:
            preferences_dict = {
                "dietary_restrictions": food_prefs.dietary_restrictions,
                "cuisine_preferences": food_prefs.cuisine_preferences,
                "spice_tolerance": food_prefs.spice_tolerance,
                "price_range_preference": food_prefs.price_range_preference,
                "adventure_level": food_prefs.adventure_level,
                "allergies": food_prefs.allergies
            }
        
        # Get restaurants from places (filtering for food-related places)
        restaurants = db.query(models.Place).filter(
            models.Place.city_id == request.city_id,
            models.Place.category.in_(['restaurant', 'cafe', 'bar', 'bistrot', 'brasserie'])
        ).limit(50).all()
        
        # Prepare restaurant data for AI
        restaurant_data = [
            {
                "name": restaurant.name,
                "category": restaurant.category,
                "subcategory": restaurant.subcategory,
                "price_level": restaurant.price_level,
                "michelin_stars": restaurant.michelin_stars,
                "address": restaurant.address,
                "local_tips": restaurant.local_tips
            }
            for restaurant in restaurants
        ]
        
        # Get AI recommendations
        ai_recommendations = await claude_service.recommend_restaurants(
            preferences_dict,
            city.name,
            restaurant_data
        )
        
        if "error" in ai_recommendations:
            raise HTTPException(status_code=500, detail=ai_recommendations["error"])
        
        # Save recommendations to database
        saved_recommendations = []
        for rec in ai_recommendations.get("recommendations", []):
            restaurant_name = rec.get("restaurant_name", "")
            
            # Find the actual place in database
            matching_place = None
            for place in restaurants:
                if place.name.lower() in restaurant_name.lower() or restaurant_name.lower() in place.name.lower():
                    matching_place = place
                    break
            
            if matching_place:
                recommendation = models.RestaurantRecommendation(
                    user_id=current_user.id,
                    place_id=matching_place.id,
                    recommendation_reason=rec.get("match_reason", ""),
                    match_score=rec.get("match_score", 0.5),
                    dish_recommendations=rec.get("recommended_dishes", []),
                    dining_tips=rec.get("dining_tips", ""),
                    price_estimate=rec.get("price_estimate", {}),
                    reservation_difficulty=rec.get("reservation_difficulty", "moderate")
                )
                
                db.add(recommendation)
                saved_recommendations.append(recommendation)
        
        if saved_recommendations:
            db.commit()
        
        return {
            "city": city.name,
            "meal_type": request.meal_type,
            "budget_level": request.budget_level,
            "total_restaurants_analyzed": len(restaurant_data),
            "recommendations": ai_recommendations.get("recommendations", []),
            "general_dining_advice": f"Great dining options in {city.name} for your preferences!",
            "preferences_used": {
                "dietary_restrictions": preferences_dict.get("dietary_restrictions", []),
                "adventure_level": preferences_dict.get("adventure_level", "moderate"),
                "allergies": preferences_dict.get("allergies", [])
            }
        }
        
    except Exception as e:
        logger.error(f"Restaurant recommendation error: {e}")
        raise HTTPException(status_code=500, detail="Failed to get restaurant recommendations")

@router.get("/recommendations/saved")
async def get_saved_restaurant_recommendations(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Get user's saved restaurant recommendations"""
    
    recommendations = db.query(
        models.RestaurantRecommendation,
        models.Place,
        models.City
    ).join(
        models.Place, models.RestaurantRecommendation.place_id == models.Place.id
    ).join(
        models.City, models.Place.city_id == models.City.id
    ).filter(
        models.RestaurantRecommendation.user_id == current_user.id
    ).order_by(
        models.RestaurantRecommendation.recommended_at.desc()
    ).limit(50).all()
    
    return [
        {
            "recommendation_id": str(rec.RestaurantRecommendation.id),
            "restaurant": {
                "id": str(rec.Place.id),
                "name": rec.Place.name,
                "category": rec.Place.category,
                "price_level": rec.Place.price_level,
                "michelin_stars": rec.Place.michelin_stars,
                "address": rec.Place.address
            },
            "city": rec.City.name,
            "recommendation_reason": rec.RestaurantRecommendation.recommendation_reason,
            "match_score": rec.RestaurantRecommendation.match_score,
            "recommended_dishes": rec.RestaurantRecommendation.dish_recommendations,
            "dining_tips": rec.RestaurantRecommendation.dining_tips,
            "price_estimate": rec.RestaurantRecommendation.price_estimate,
            "reservation_difficulty": rec.RestaurantRecommendation.reservation_difficulty,
            "recommended_at": rec.RestaurantRecommendation.recommended_at
        }
        for rec in recommendations
    ]

@router.post("/cuisine-guide")
async def get_cuisine_guide(
    city_id: int,
    cuisine_type: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get AI-generated guide to local cuisine"""
    
    try:
        city = db.query(models.City).filter(models.City.id == city_id).first()
        if not city:
            raise HTTPException(status_code=404, detail="City not found")
        
        # Generate cuisine guide with AI
        if cuisine_type:
            prompt = f"Provide a detailed guide to {cuisine_type} cuisine in {city.name}, France."
        else:
            prompt = f"Provide a comprehensive guide to the local cuisine and food culture in {city.name}, France."
        
        prompt += """
        
        Include:
        1. Signature dishes and specialties
        2. Best places to try authentic food
        3. Local food customs and etiquette
        4. Seasonal ingredients and dishes
        5. Price ranges and where to find good value
        6. Hidden food gems locals love
        7. What to avoid (tourist traps)
        8. Food experiences unique to this region
        
        Make it practical and engaging for travelers."""
        
        cuisine_guide = await claude_service.general_ai_assistance(
            prompt,
            {"city": city.name, "region": city.region, "cuisine_type": cuisine_type},
            "food_expert"
        )
        
        return {
            "city": city.name,
            "region": city.region,
            "cuisine_type": cuisine_type or "local cuisine",
            "guide": cuisine_guide,
            "generated_at": func.now()
        }
        
    except Exception as e:
        logger.error(f"Cuisine guide error: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate cuisine guide")

@router.get("/dietary-options")
async def get_dietary_restriction_options():
    """Get available dietary restriction and preference options"""
    
    return {
        "dietary_restrictions": [
            {"value": "vegetarian", "label": "Vegetarian"},
            {"value": "vegan", "label": "Vegan"},
            {"value": "gluten-free", "label": "Gluten-Free"},
            {"value": "dairy-free", "label": "Dairy-Free"},
            {"value": "nut-free", "label": "Nut-Free"},
            {"value": "halal", "label": "Halal"},
            {"value": "kosher", "label": "Kosher"},
            {"value": "keto", "label": "Ketogenic"},
            {"value": "paleo", "label": "Paleo"},
            {"value": "low-carb", "label": "Low Carb"}
        ],
        "spice_levels": [
            {"value": "mild", "label": "Mild - I prefer subtle flavors"},
            {"value": "medium", "label": "Medium - I enjoy some spice"},
            {"value": "hot", "label": "Hot - I love spicy food"},
            {"value": "extreme", "label": "Extreme - The spicier the better"}
        ],
        "adventure_levels": [
            {"value": "conservative", "label": "Conservative - Stick to familiar foods"},
            {"value": "moderate", "label": "Moderate - Open to trying some new things"},
            {"value": "adventurous", "label": "Adventurous - I'll try almost anything"}
        ],
        "cuisine_types": [
            {"value": "french", "label": "French"},
            {"value": "italian", "label": "Italian"},
            {"value": "mediterranean", "label": "Mediterranean"},
            {"value": "asian", "label": "Asian"},
            {"value": "indian", "label": "Indian"},
            {"value": "mexican", "label": "Mexican"},
            {"value": "middle-eastern", "label": "Middle Eastern"},
            {"value": "american", "label": "American"},
            {"value": "japanese", "label": "Japanese"},
            {"value": "chinese", "label": "Chinese"},
            {"value": "thai", "label": "Thai"},
            {"value": "vietnamese", "label": "Vietnamese"}
        ],
        "common_allergies": [
            "nuts", "peanuts", "dairy", "eggs", "soy", "wheat", 
            "fish", "shellfish", "sesame", "mustard"
        ]
    }

@router.post("/wine-pairing")
async def get_wine_pairing_suggestions(
    dish_description: str,
    city_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """Get AI wine pairing suggestions for dishes"""
    
    try:
        city_context = ""
        if city_id:
            city = db.query(models.City).filter(models.City.id == city_id).first()
            if city:
                city_context = f" in {city.name}, {city.region}"
        
        prompt = f"""Suggest wine pairings for this dish: {dish_description}
        
        Context: Dining{city_context}, France
        
        Provide:
        1. Specific wine recommendations (include French wines)
        2. Why these pairings work
        3. Alternative options for different budgets
        4. Local wine regions to look for
        5. What to ask the sommelier/server
        6. Non-alcoholic alternatives
        
        Make it practical for travelers in France."""
        
        wine_suggestions = await claude_service.general_ai_assistance(
            prompt,
            {"dish": dish_description, "location": city_context},
            "food_expert"
        )
        
        return {
            "dish": dish_description,
            "location": city_context.strip(),
            "wine_pairings": wine_suggestions,
            "generated_at": func.now()
        }
        
    except Exception as e:
        logger.error(f"Wine pairing error: {e}")
        return {
            "dish": dish_description,
            "wine_pairings": "For this dish, consider a medium-bodied red wine or a crisp white wine. Ask your server for local recommendations!",
            "error": "Detailed pairing unavailable"
        }

@router.get("/local-specialties/{city_id}")
async def get_local_food_specialties(
    city_id: int,
    db: Session = Depends(get_db)
):
    """Get local food specialties and must-try dishes"""
    
    city = db.query(models.City).filter(models.City.id == city_id).first()
    if not city:
        raise HTTPException(status_code=404, detail="City not found")
    
    try:
        prompt = f"""List the must-try local food specialties in {city.name}, France.
        
        For each specialty, provide:
        1. The dish name in French and English
        2. Brief description
        3. Where to find the best version
        4. Average price range
        5. When it's typically eaten
        6. Any cultural significance
        
        Focus on authentic local dishes that aren't tourist traps."""
        
        specialties = await claude_service.general_ai_assistance(
            prompt,
            {"city": city.name, "region": city.region},
            "food_expert"
        )
        
        return {
            "city": city.name,
            "region": city.region,
            "local_specialties": specialties
        }
        
    except Exception as e:
        logger.error(f"Local specialties error: {e}")
        return {
            "city": city.name,
            "local_specialties": f"Explore the wonderful local cuisine of {city.name}! Ask locals for their favorite restaurants and try regional specialties.",
            "error": "Detailed information unavailable"
        }