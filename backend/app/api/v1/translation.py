from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List, Dict
import uuid
import logging

from app import models
from app.database import get_db
from app.api.v1.auth import get_current_user
from app.core.claude_ai import ClaudeAIService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/translation", tags=["Smart Translation & Cultural Context"])

claude_service = ClaudeAIService()

# Translation models
class TranslationRequest(BaseModel):
    text: str
    source_language: str = "auto"  # auto-detect or specific language code
    target_language: str = "fr"    # French by default
    context_type: str = "general"  # restaurant, hotel, emergency, shopping, etc.

class CulturalInsightRequest(BaseModel):
    city_id: int
    category: str = "general"  # etiquette, traditions, customs, holidays
    
class PhrasebookRequest(BaseModel):
    category: str
    target_language: str = "fr"

@router.post("/translate")
async def translate_with_cultural_context(
    request: TranslationRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Translate text with cultural context and usage tips"""
    
    try:
        # Get AI translation with context
        translation_result = await claude_service.translate_with_context(
            request.text,
            request.source_language,
            request.target_language,
            request.context_type
        )
        
        if "error" in translation_result:
            raise HTTPException(status_code=500, detail=translation_result["error"])
        
        # Save translation request to database
        translation_record = models.TranslationRequest(
            user_id=current_user.id,
            source_text=request.text,
            source_language=request.source_language,
            target_language=request.target_language,
            translated_text=translation_result.get("translation", ""),
            cultural_context=translation_result.get("cultural_context", ""),
            usage_tips=translation_result.get("usage_tips", ""),
            formality_level=translation_result.get("formality_level", "casual"),
            context_type=request.context_type,
            confidence_score=translation_result.get("confidence_score", 0.9)
        )
        
        db.add(translation_record)
        db.commit()
        db.refresh(translation_record)
        
        return {
            "translation_id": str(translation_record.id),
            "original_text": request.text,
            "translated_text": translation_result.get("translation", ""),
            "source_language": request.source_language,
            "target_language": request.target_language,
            "cultural_context": translation_result.get("cultural_context", ""),
            "usage_tips": translation_result.get("usage_tips", ""),
            "formality_level": translation_result.get("formality_level", "casual"),
            "alternatives": translation_result.get("alternatives", []),
            "etiquette_notes": translation_result.get("etiquette_notes", ""),
            "confidence_score": translation_result.get("confidence_score", 0.9),
            "context_type": request.context_type
        }
        
    except Exception as e:
        logger.error(f"Translation error: {e}")
        raise HTTPException(status_code=500, detail="Translation failed")

@router.get("/history")
async def get_translation_history(
    context_type: Optional[str] = None,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Get user's translation history"""
    
    query = db.query(models.TranslationRequest).filter(
        models.TranslationRequest.user_id == current_user.id
    )
    
    if context_type:
        query = query.filter(models.TranslationRequest.context_type == context_type)
    
    translations = query.order_by(
        models.TranslationRequest.created_at.desc()
    ).limit(limit).all()
    
    return [
        {
            "id": str(translation.id),
            "source_text": translation.source_text,
            "translated_text": translation.translated_text,
            "source_language": translation.source_language,
            "target_language": translation.target_language,
            "context_type": translation.context_type,
            "formality_level": translation.formality_level,
            "created_at": translation.created_at
        }
        for translation in translations
    ]

@router.get("/phrasebook")
async def get_travel_phrasebook(
    request: PhrasebookRequest,
    db: Session = Depends(get_db)
):
    """Get essential travel phrases with cultural context"""
    
    try:
        # Predefined phrase categories
        phrase_categories = {
            "greetings": [
                "Hello", "Good morning", "Good evening", "How are you?", 
                "Nice to meet you", "Goodbye", "See you later"
            ],
            "restaurant": [
                "Table for two please", "What do you recommend?", "I'm vegetarian",
                "The check please", "This is delicious", "I have allergies",
                "Can I see the wine list?"
            ],
            "hotel": [
                "I have a reservation", "What time is check-out?", 
                "Can I have a wake-up call?", "Where is the elevator?",
                "The air conditioning doesn't work", "Can I get extra towels?"
            ],
            "directions": [
                "Where is the bathroom?", "How do I get to...?", 
                "Turn left", "Turn right", "Straight ahead",
                "Is it far?", "Can you show me on the map?"
            ],
            "shopping": [
                "How much does this cost?", "Do you accept credit cards?",
                "Can I try this on?", "Do you have this in a different size?",
                "Where is the fitting room?", "Can I have a receipt?"
            ],
            "emergency": [
                "Help!", "Call the police", "I need a doctor",
                "I'm lost", "I don't speak French", "Can you help me?",
                "Where is the hospital?"
            ],
            "transportation": [
                "Where is the train station?", "What time does the next train leave?",
                "One ticket please", "How much is a taxi to...?",
                "Is this the right platform?", "Does this bus go to...?"
            ]
        }
        
        if request.category not in phrase_categories:
            return {
                "available_categories": list(phrase_categories.keys()),
                "error": f"Category '{request.category}' not found"
            }
        
        phrases = phrase_categories[request.category]
        
        # Translate and get cultural context for each phrase
        translated_phrases = []
        
        for phrase in phrases[:10]:  # Limit to avoid too many API calls
            try:
                result = await claude_service.translate_with_context(
                    phrase,
                    "en",
                    request.target_language,
                    request.category
                )
                
                translated_phrases.append({
                    "english": phrase,
                    "translation": result.get("translation", phrase),
                    "pronunciation": result.get("pronunciation", ""),
                    "cultural_notes": result.get("cultural_context", ""),
                    "usage_tips": result.get("usage_tips", ""),
                    "formality": result.get("formality_level", "neutral")
                })
                
            except Exception as e:
                logger.error(f"Phrase translation error: {e}")
                translated_phrases.append({
                    "english": phrase,
                    "translation": phrase,
                    "error": "Translation failed"
                })
        
        return {
            "category": request.category,
            "target_language": request.target_language,
            "phrases": translated_phrases,
            "cultural_overview": f"Cultural context for {request.category} situations in France"
        }
        
    except Exception as e:
        logger.error(f"Phrasebook error: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate phrasebook")

@router.post("/cultural-insights")
async def get_cultural_insights(
    request: CulturalInsightRequest,
    db: Session = Depends(get_db)
):
    """Get AI-generated cultural insights for a city"""
    
    try:
        # Get city information
        city = db.query(models.City).filter(models.City.id == request.city_id).first()
        if not city:
            raise HTTPException(status_code=404, detail="City not found")
        
        # Check if we have cached insights
        existing_insight = db.query(models.CulturalInsight).filter(
            models.CulturalInsight.city_id == request.city_id,
            models.CulturalInsight.category == request.category
        ).first()
        
        if existing_insight:
            return {
                "city": city.name,
                "category": request.category,
                "title": existing_insight.title,
                "insight": existing_insight.insight,
                "practical_tips": existing_insight.practical_tips,
                "do_dont_list": existing_insight.do_dont_list,
                "relevance_level": existing_insight.relevance_level,
                "cached": True
            }
        
        # Generate new cultural insights with AI
        prompt = f"""Provide detailed cultural insights for travelers visiting {city.name}, France.

        Focus on: {request.category}
        
        Provide:
        1. Key cultural aspects visitors should know
        2. Practical etiquette tips
        3. Common mistakes tourists make
        4. Do's and don'ts list
        5. Local customs and traditions
        6. How to show respect for local culture
        
        Make it practical and respectful, focusing on helping travelers integrate better.
        
        Return as JSON with keys: title, insight, practical_tips, dos_and_donts, importance_level"""
        
        ai_insights = await claude_service.general_ai_assistance(
            prompt,
            {"city": city.name, "category": request.category},
            "cultural_translator"
        )
        
        # Try to parse as JSON, if it fails use as text
        try:
            import json
            insights_data = json.loads(ai_insights)
        except:
            insights_data = {
                "title": f"Cultural Guide for {city.name}",
                "insight": ai_insights,
                "practical_tips": "Follow local customs and be respectful",
                "dos_and_donts": ["Do: Be polite", "Don't: Be loud in public"],
                "importance_level": "helpful"
            }
        
        # Save to database
        cultural_insight = models.CulturalInsight(
            city_id=request.city_id,
            category=request.category,
            title=insights_data.get("title", f"Cultural Guide for {city.name}"),
            insight=insights_data.get("insight", ai_insights),
            practical_tips=insights_data.get("practical_tips", ""),
            do_dont_list=insights_data.get("dos_and_donts", []),
            relevance_level=insights_data.get("importance_level", "helpful")
        )
        
        db.add(cultural_insight)
        db.commit()
        
        return {
            "city": city.name,
            "category": request.category,
            "title": cultural_insight.title,
            "insight": cultural_insight.insight,
            "practical_tips": cultural_insight.practical_tips,
            "do_dont_list": cultural_insight.do_dont_list,
            "relevance_level": cultural_insight.relevance_level,
            "cached": False
        }
        
    except Exception as e:
        logger.error(f"Cultural insights error: {e}")
        raise HTTPException(status_code=500, detail="Failed to get cultural insights")

@router.get("/cultural-insights/{city_id}")
async def get_city_cultural_insights(
    city_id: int,
    db: Session = Depends(get_db)
):
    """Get all cultural insights for a city"""
    
    city = db.query(models.City).filter(models.City.id == city_id).first()
    if not city:
        raise HTTPException(status_code=404, detail="City not found")
    
    insights = db.query(models.CulturalInsight).filter(
        models.CulturalInsight.city_id == city_id
    ).all()
    
    return {
        "city": city.name,
        "insights": [
            {
                "id": str(insight.id),
                "category": insight.category,
                "title": insight.title,
                "insight": insight.insight[:300] + "..." if len(insight.insight) > 300 else insight.insight,
                "relevance_level": insight.relevance_level,
                "created_at": insight.created_at
            }
            for insight in insights
        ]
    }

@router.get("/context-types")
async def get_translation_context_types():
    """Get available translation context types"""
    
    return {
        "context_types": [
            {
                "value": "restaurant",
                "name": "Restaurant & Dining",
                "description": "Food ordering, dining etiquette, restaurant interactions"
            },
            {
                "value": "hotel",
                "name": "Hotel & Accommodation", 
                "description": "Hotel services, room requests, check-in/out"
            },
            {
                "value": "shopping",
                "name": "Shopping & Markets",
                "description": "Price negotiation, purchases, market interactions"
            },
            {
                "value": "transportation",
                "name": "Transportation",
                "description": "Trains, buses, taxis, directions"
            },
            {
                "value": "emergency",
                "name": "Emergency Situations",
                "description": "Medical emergencies, police, urgent help"
            },
            {
                "value": "social",
                "name": "Social Interactions",
                "description": "Meeting people, conversations, social situations"
            },
            {
                "value": "business",
                "name": "Business & Professional",
                "description": "Formal meetings, business interactions"
            },
            {
                "value": "tourism",
                "name": "Tourism & Sightseeing",
                "description": "Museums, tours, tourist information"
            }
        ],
        "cultural_categories": [
            "etiquette", "traditions", "customs", "holidays", 
            "dining", "social_norms", "business_culture", "taboos"
        ]
    }

@router.post("/quick-translate")
async def quick_translate(
    text: str,
    target_lang: str = "fr",
    db: Session = Depends(get_db)
):
    """Quick translation without cultural context (for simple phrases)"""
    
    try:
        # Simple translation without full cultural analysis
        result = await claude_service.translate_with_context(
            text,
            "auto",
            target_lang,
            "general"
        )
        
        return {
            "original": text,
            "translation": result.get("translation", text),
            "confidence": result.get("confidence_score", 0.8)
        }
        
    except Exception as e:
        logger.error(f"Quick translation error: {e}")
        # Fallback response
        return {
            "original": text,
            "translation": text,
            "error": "Translation service unavailable",
            "confidence": 0.0
        }