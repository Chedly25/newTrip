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

router = APIRouter(prefix="/safety", tags=["AI Travel Risk Assessment & Safety"])

claude_service = ClaudeAIService()

# Safety assessment models
class SafetyAssessmentRequest(BaseModel):
    city_id: int
    travel_dates: List[str]
    traveler_profile: Dict = {}
    specific_concerns: List[str] = []

class TravelAlertCreate(BaseModel):
    city_id: int
    alert_type: str  # weather, security, health, transport
    severity: str    # low, medium, high, critical
    title: str
    description: str
    affected_areas: List[str] = []
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    source: str = "AI_Assessment"

@router.post("/assess")
async def assess_travel_safety(
    request: SafetyAssessmentRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Get comprehensive AI safety assessment for travel"""
    
    try:
        # Get city information
        city = db.query(models.City).filter(models.City.id == request.city_id).first()
        if not city:
            raise HTTPException(status_code=404, detail="City not found")
        
        # Get existing safety assessment if recent
        recent_assessment = db.query(models.SafetyAssessment).filter(
            models.SafetyAssessment.city_id == request.city_id,
            models.SafetyAssessment.assessment_date >= datetime.utcnow() - timedelta(days=7)
        ).first()
        
        # Default traveler profile
        traveler_profile = {
            "experience_level": "intermediate",
            "group_type": "solo",
            "risk_tolerance": "medium",
            "special_needs": [],
            **request.traveler_profile
        }
        
        # Get AI safety assessment
        ai_assessment = await claude_service.assess_travel_safety(
            city.name,
            request.travel_dates,
            traveler_profile
        )
        
        if "error" in ai_assessment:
            raise HTTPException(status_code=500, detail=ai_assessment["error"])
        
        # Save or update assessment
        if recent_assessment:
            # Update existing assessment
            recent_assessment.overall_safety_score = ai_assessment.get("safety_score", 7.0)
            recent_assessment.crime_risk = ai_assessment.get("caution_areas", {})
            recent_assessment.health_alerts = ai_assessment.get("health_notes", {})
            recent_assessment.transportation_safety = ai_assessment.get("transport_safety", {})
            recent_assessment.emergency_contacts = ai_assessment.get("emergency_info", {})
            recent_assessment.safety_tips = ai_assessment.get("safety_tips", "")
            recent_assessment.confidence_level = 0.85
            
            db.commit()
            assessment = recent_assessment
            
        else:
            # Create new assessment
            assessment = models.SafetyAssessment(
                city_id=request.city_id,
                overall_safety_score=ai_assessment.get("safety_score", 7.0),
                crime_risk=ai_assessment.get("caution_areas", {}),
                health_alerts=ai_assessment.get("health_notes", {}),
                transportation_safety=ai_assessment.get("transport_safety", {}),
                emergency_contacts=ai_assessment.get("emergency_info", {}),
                safe_areas=ai_assessment.get("safe_areas", {}),
                areas_to_avoid=ai_assessment.get("caution_areas", {}),
                safety_tips=ai_assessment.get("safety_tips", ""),
                data_sources=["AI_Analysis", "Official_Sources"],
                confidence_level=0.85
            )
            
            db.add(assessment)
            db.commit()
            db.refresh(assessment)
        
        return {
            "assessment_id": str(assessment.id),
            "city": city.name,
            "assessment_date": assessment.assessment_date,
            "overall_safety_score": assessment.overall_safety_score,
            "safety_level": "High" if assessment.overall_safety_score >= 8 else "Good" if assessment.overall_safety_score >= 6 else "Moderate",
            "current_conditions": ai_assessment.get("current_conditions", "Generally safe for travelers"),
            "caution_areas": ai_assessment.get("caution_areas", {}),
            "transport_safety": ai_assessment.get("transport_safety", {}),
            "health_considerations": ai_assessment.get("health_notes", {}),
            "emergency_info": ai_assessment.get("emergency_info", {}),
            "safety_tips": ai_assessment.get("safety_tips", ""),
            "cultural_considerations": ai_assessment.get("cultural_considerations", ""),
            "confidence_level": assessment.confidence_level,
            "travel_dates": request.travel_dates,
            "traveler_profile": traveler_profile
        }
        
    except Exception as e:
        logger.error(f"Safety assessment error: {e}")
        raise HTTPException(status_code=500, detail="Failed to assess travel safety")

@router.get("/city/{city_id}")
async def get_city_safety_info(
    city_id: int,
    db: Session = Depends(get_db)
):
    """Get latest safety information for a city"""
    
    city = db.query(models.City).filter(models.City.id == city_id).first()
    if not city:
        raise HTTPException(status_code=404, detail="City not found")
    
    # Get latest assessment
    latest_assessment = db.query(models.SafetyAssessment).filter(
        models.SafetyAssessment.city_id == city_id
    ).order_by(models.SafetyAssessment.assessment_date.desc()).first()
    
    # Get active alerts
    active_alerts = db.query(models.TravelAlert).filter(
        models.TravelAlert.city_id == city_id,
        models.TravelAlert.is_active == True,
        models.TravelAlert.end_date >= datetime.utcnow()
    ).all()
    
    result = {
        "city": city.name,
        "region": city.region,
        "has_recent_assessment": latest_assessment is not None,
        "active_alerts_count": len(active_alerts)
    }
    
    if latest_assessment:
        result.update({
            "overall_safety_score": latest_assessment.overall_safety_score,
            "assessment_date": latest_assessment.assessment_date,
            "safety_tips": latest_assessment.safety_tips,
            "emergency_contacts": latest_assessment.emergency_contacts,
            "confidence_level": latest_assessment.confidence_level
        })
    
    if active_alerts:
        result["alerts"] = [
            {
                "id": str(alert.id),
                "type": alert.alert_type,
                "severity": alert.severity,
                "title": alert.title,
                "description": alert.description[:200] + "..." if len(alert.description) > 200 else alert.description,
                "start_date": alert.start_date,
                "end_date": alert.end_date
            }
            for alert in active_alerts
        ]
    
    return result

@router.get("/alerts")
async def get_travel_alerts(
    city_id: Optional[int] = None,
    alert_type: Optional[str] = None,
    severity: Optional[str] = None,
    active_only: bool = True,
    db: Session = Depends(get_db)
):
    """Get travel alerts with optional filters"""
    
    query = db.query(models.TravelAlert, models.City).join(
        models.City, models.TravelAlert.city_id == models.City.id
    )
    
    if active_only:
        query = query.filter(
            models.TravelAlert.is_active == True,
            models.TravelAlert.end_date >= datetime.utcnow()
        )
    
    if city_id:
        query = query.filter(models.TravelAlert.city_id == city_id)
    
    if alert_type:
        query = query.filter(models.TravelAlert.alert_type == alert_type)
    
    if severity:
        query = query.filter(models.TravelAlert.severity == severity)
    
    alerts = query.order_by(
        models.TravelAlert.severity.desc(),
        models.TravelAlert.start_date.desc()
    ).limit(100).all()
    
    return [
        {
            "id": str(alert.TravelAlert.id),
            "city": alert.City.name,
            "alert_type": alert.TravelAlert.alert_type,
            "severity": alert.TravelAlert.severity,
            "title": alert.TravelAlert.title,
            "description": alert.TravelAlert.description,
            "ai_impact_analysis": alert.TravelAlert.ai_impact_analysis,
            "recommended_actions": alert.TravelAlert.recommended_actions,
            "affected_areas": alert.TravelAlert.affected_areas,
            "start_date": alert.TravelAlert.start_date,
            "end_date": alert.TravelAlert.end_date,
            "source": alert.TravelAlert.source,
            "is_active": alert.TravelAlert.is_active
        }
        for alert in alerts
    ]

@router.post("/emergency-guide")
async def get_emergency_guide(
    city_id: int,
    emergency_type: str,
    db: Session = Depends(get_db)
):
    """Get AI-generated emergency response guide"""
    
    try:
        city = db.query(models.City).filter(models.City.id == city_id).first()
        if not city:
            raise HTTPException(status_code=404, detail="City not found")
        
        emergency_types = {
            "medical": "medical emergency or health issue",
            "crime": "crime or theft",
            "natural": "natural disaster or weather emergency",
            "transport": "transportation emergency or being stranded",
            "lost": "being lost or separated from group",
            "communication": "communication problems or language barriers",
            "financial": "financial emergency or lost money/cards",
            "legal": "legal issues or problems with authorities"
        }
        
        if emergency_type not in emergency_types:
            raise HTTPException(
                status_code=400,
                detail=f"Emergency type must be one of: {list(emergency_types.keys())}"
            )
        
        prompt = f"""Create a detailed emergency response guide for a {emergency_types[emergency_type]} in {city.name}, France.
        
        Include:
        1. Immediate steps to take
        2. Important phone numbers and contacts
        3. Key French phrases for emergency situations
        4. Where to go for help
        5. What documents/information to have ready
        6. How to contact embassy/consulate if needed
        7. Common mistakes to avoid
        8. Recovery steps after the emergency
        
        Make it actionable and specific to France's systems and culture."""
        
        emergency_guide = await claude_service.general_ai_assistance(
            prompt,
            {
                "city": city.name,
                "region": city.region,
                "emergency_type": emergency_type,
                "country": "France"
            },
            "safety_advisor"
        )
        
        return {
            "city": city.name,
            "emergency_type": emergency_type,
            "guide": emergency_guide,
            "generated_at": datetime.utcnow(),
            "disclaimer": "This is AI-generated guidance. In a real emergency, contact local emergency services immediately."
        }
        
    except Exception as e:
        logger.error(f"Emergency guide error: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate emergency guide")

@router.get("/safety-tips")
async def get_general_safety_tips(
    category: str = "general",
    traveler_type: str = "general"
):
    """Get AI-generated safety tips by category and traveler type"""
    
    try:
        categories = {
            "general": "general travel safety",
            "solo": "solo traveler safety",
            "female": "female traveler safety",
            "night": "nighttime safety",
            "transport": "transportation safety",
            "accommodation": "accommodation safety",
            "scam": "avoiding scams and fraud",
            "health": "health and medical safety",
            "digital": "digital security and privacy"
        }
        
        if category not in categories:
            category = "general"
        
        prompt = f"""Provide comprehensive safety tips for {categories[category]} while traveling in France.
        
        Traveler profile: {traveler_type}
        
        Include:
        1. Specific, actionable safety advice
        2. Common risks to be aware of
        3. Preventive measures
        4. What to do if something goes wrong
        5. Cultural considerations
        6. Practical tips for staying safe
        
        Make it practical and non-alarmist."""
        
        safety_tips = await claude_service.general_ai_assistance(
            prompt,
            {"category": category, "traveler_type": traveler_type, "location": "France"},
            "safety_advisor"
        )
        
        return {
            "category": category,
            "traveler_type": traveler_type,
            "location": "France",
            "tips": safety_tips,
            "generated_at": datetime.utcnow()
        }
        
    except Exception as e:
        logger.error(f"Safety tips error: {e}")
        return {
            "category": category,
            "tips": "Stay aware of your surroundings, keep important documents secure, trust your instincts, and have emergency contacts readily available.",
            "error": "Detailed tips unavailable"
        }

@router.get("/emergency-contacts")
async def get_emergency_contacts(
    city_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """Get emergency contact information"""
    
    # France universal emergency numbers
    base_contacts = {
        "emergency_services": {
            "all_emergencies": "112",
            "police": "17",
            "fire_department": "18",
            "medical_emergency": "15",
            "description": "These work throughout France"
        },
        "tourist_assistance": {
            "tourist_police": "Available in major cities",
            "tourist_hotline": "3975 (from France)"
        },
        "embassies": {
            "us_embassy": "+33 1 43 12 22 22",
            "uk_embassy": "+33 1 44 51 31 00",
            "canadian_embassy": "+33 1 44 43 29 00",
            "australian_embassy": "+33 1 40 59 33 00"
        }
    }
    
    result = {
        "country": "France",
        "emergency_contacts": base_contacts
    }
    
    if city_id:
        city = db.query(models.City).filter(models.City.id == city_id).first()
        if city:
            result["city"] = city.name
            
            # Get city-specific contacts from latest assessment
            latest_assessment = db.query(models.SafetyAssessment).filter(
                models.SafetyAssessment.city_id == city_id
            ).order_by(models.SafetyAssessment.assessment_date.desc()).first()
            
            if latest_assessment and latest_assessment.emergency_contacts:
                result["city_specific_contacts"] = latest_assessment.emergency_contacts
    
    return result

@router.get("/risk-factors")
async def get_travel_risk_factors():
    """Get information about travel risk factors and how they're assessed"""
    
    return {
        "risk_categories": [
            {
                "category": "crime",
                "description": "Theft, fraud, violent crime",
                "factors": ["crime rates", "tourist targeting", "safe areas", "police presence"]
            },
            {
                "category": "health",
                "description": "Disease outbreaks, medical facilities",
                "factors": ["current health alerts", "hospital quality", "vaccination requirements", "air quality"]
            },
            {
                "category": "natural_disasters",
                "description": "Weather, earthquakes, floods",
                "factors": ["seasonal weather patterns", "natural disaster history", "emergency preparedness"]
            },
            {
                "category": "political_stability",
                "description": "Civil unrest, government stability",
                "factors": ["political climate", "protest activity", "government stability", "civil unrest"]
            },
            {
                "category": "transportation",
                "description": "Transport safety and reliability",
                "factors": ["road safety", "public transport quality", "airport security", "infrastructure quality"]
            }
        ],
        "safety_score_explanation": {
            "9-10": "Excellent - Very safe with minimal risks",
            "7-8": "Good - Generally safe with standard precautions",
            "5-6": "Moderate - Some risks, extra caution advised",
            "3-4": "Poor - Significant risks, careful planning needed",
            "1-2": "High Risk - Avoid travel if possible"
        },
        "data_sources": [
            "Government travel advisories",
            "Local police reports",
            "Tourist incident reports",
            "Health organization alerts",
            "Real-time news monitoring",
            "Local safety assessments"
        ]
    }