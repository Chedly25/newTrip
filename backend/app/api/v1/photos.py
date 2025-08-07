from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, Dict, List
import uuid
import base64
import os
from datetime import datetime
import logging

from app import models
from app.database import get_db
from app.api.v1.auth import get_current_user
from app.core.claude_ai import ClaudeAIService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/photos", tags=["Smart Photo Analysis"])

claude_service = ClaudeAIService()

# Photo analysis models
class PhotoAnalysisRequest(BaseModel):
    image_data: str  # Base64 encoded image
    location: Optional[str] = None
    context: Optional[Dict] = {}

class PhotoAnalysisResponse(BaseModel):
    photo_id: str
    identified_places: List[Dict]
    cultural_context: str
    photography_tips: str
    similar_locations: List[Dict]
    local_insights: str
    confidence_score: float

@router.post("/upload", response_model=PhotoAnalysisResponse)
async def upload_and_analyze_photo(
    file: UploadFile = File(...),
    location: Optional[str] = Form(None),
    context: Optional[str] = Form("{}"),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Upload a photo and get AI analysis with place recognition"""
    
    try:
        # Validate file type
        if not file.content_type.startswith("image/"):
            raise HTTPException(status_code=400, detail="File must be an image")
        
        # Read and encode image
        image_content = await file.read()
        image_b64 = base64.b64encode(image_content).decode()
        
        # Create photo upload record
        photo_upload = models.PhotoUpload(
            user_id=current_user.id,
            file_name=file.filename,
            file_size=len(image_content),
            mime_type=file.content_type,
            ai_analysis_status="processing"
        )
        db.add(photo_upload)
        db.commit()
        db.refresh(photo_upload)
        
        # Parse context
        import json
        try:
            context_dict = json.loads(context) if context != "{}" else {}
        except:
            context_dict = {}
        
        if location:
            context_dict["location"] = location
        
        # Get AI analysis
        analysis_result = await claude_service.analyze_photo(image_b64, context_dict)
        
        if "error" in analysis_result:
            photo_upload.ai_analysis_status = "failed"
            db.commit()
            raise HTTPException(status_code=500, detail=analysis_result["error"])
        
        # Save analysis results
        photo_analysis = models.PhotoAnalysis(
            photo_id=photo_upload.id,
            identified_places=analysis_result.get("identified_places", []),
            suggested_locations=analysis_result.get("similar_locations", []),
            cultural_context=analysis_result.get("cultural_context", ""),
            photography_tips=analysis_result.get("photography_tips", ""),
            local_insights=analysis_result.get("local_insights", ""),
            confidence_score=analysis_result.get("confidence_score", 0.0)
        )
        db.add(photo_analysis)
        
        # Update status
        photo_upload.ai_analysis_status = "completed"
        db.commit()
        
        return {
            "photo_id": str(photo_upload.id),
            "identified_places": analysis_result.get("identified_places", []),
            "cultural_context": analysis_result.get("cultural_context", ""),
            "photography_tips": analysis_result.get("photography_tips", ""),
            "similar_locations": analysis_result.get("similar_locations", []),
            "local_insights": analysis_result.get("local_insights", ""),
            "confidence_score": analysis_result.get("confidence_score", 0.0)
        }
        
    except Exception as e:
        logger.error(f"Photo analysis error: {e}")
        if 'photo_upload' in locals():
            photo_upload.ai_analysis_status = "failed"
            db.commit()
        raise HTTPException(status_code=500, detail="Failed to analyze photo")

@router.post("/analyze-base64", response_model=PhotoAnalysisResponse)
async def analyze_base64_image(
    request: PhotoAnalysisRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Analyze a base64 encoded image"""
    
    try:
        # Create photo upload record
        photo_upload = models.PhotoUpload(
            user_id=current_user.id,
            file_name="base64_upload.jpg",
            file_size=len(request.image_data),
            mime_type="image/jpeg",
            ai_analysis_status="processing"
        )
        db.add(photo_upload)
        db.commit()
        db.refresh(photo_upload)
        
        # Get AI analysis
        analysis_result = await claude_service.analyze_photo(request.image_data, request.context)
        
        if "error" in analysis_result:
            photo_upload.ai_analysis_status = "failed"
            db.commit()
            raise HTTPException(status_code=500, detail=analysis_result["error"])
        
        # Save analysis results
        photo_analysis = models.PhotoAnalysis(
            photo_id=photo_upload.id,
            identified_places=analysis_result.get("identified_places", []),
            suggested_locations=analysis_result.get("similar_locations", []),
            cultural_context=analysis_result.get("cultural_context", ""),
            photography_tips=analysis_result.get("photography_tips", ""),
            local_insights=analysis_result.get("local_insights", ""),
            confidence_score=analysis_result.get("confidence_score", 0.0)
        )
        db.add(photo_analysis)
        
        # Update status
        photo_upload.ai_analysis_status = "completed"
        db.commit()
        
        return {
            "photo_id": str(photo_upload.id),
            "identified_places": analysis_result.get("identified_places", []),
            "cultural_context": analysis_result.get("cultural_context", ""),
            "photography_tips": analysis_result.get("photography_tips", ""),
            "similar_locations": analysis_result.get("similar_locations", []),
            "local_insights": analysis_result.get("local_insights", ""),
            "confidence_score": analysis_result.get("confidence_score", 0.0)
        }
        
    except Exception as e:
        logger.error(f"Photo analysis error: {e}")
        if 'photo_upload' in locals():
            photo_upload.ai_analysis_status = "failed"
            db.commit()
        raise HTTPException(status_code=500, detail="Failed to analyze photo")

@router.get("/my-photos")
async def get_user_photos(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Get all user's uploaded photos with analysis"""
    
    photos = db.query(models.PhotoUpload).filter(
        models.PhotoUpload.user_id == current_user.id
    ).order_by(models.PhotoUpload.created_at.desc()).all()
    
    result = []
    for photo in photos:
        photo_data = {
            "id": str(photo.id),
            "file_name": photo.file_name,
            "uploaded_at": photo.created_at,
            "analysis_status": photo.ai_analysis_status,
            "analysis": None
        }
        
        if photo.analysis_results:
            analysis = photo.analysis_results[0]  # Get first analysis
            photo_data["analysis"] = {
                "identified_places": analysis.identified_places,
                "cultural_context": analysis.cultural_context,
                "photography_tips": analysis.photography_tips,
                "similar_locations": analysis.suggested_locations,
                "local_insights": analysis.local_insights,
                "confidence_score": analysis.confidence_score
            }
        
        result.append(photo_data)
    
    return result

@router.get("/{photo_id}/analysis")
async def get_photo_analysis(
    photo_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Get detailed analysis for a specific photo"""
    
    try:
        photo_uuid = uuid.UUID(photo_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid photo ID")
    
    photo = db.query(models.PhotoUpload).filter(
        models.PhotoUpload.id == photo_uuid,
        models.PhotoUpload.user_id == current_user.id
    ).first()
    
    if not photo:
        raise HTTPException(status_code=404, detail="Photo not found")
    
    if not photo.analysis_results:
        raise HTTPException(status_code=404, detail="No analysis available for this photo")
    
    analysis = photo.analysis_results[0]
    
    return {
        "photo_id": photo_id,
        "identified_places": analysis.identified_places,
        "cultural_context": analysis.cultural_context,
        "photography_tips": analysis.photography_tips,
        "similar_locations": analysis.suggested_locations,
        "local_insights": analysis.local_insights,
        "confidence_score": analysis.confidence_score,
        "analyzed_at": analysis.analysis_timestamp
    }

@router.post("/{photo_id}/reanalyze")
async def reanalyze_photo(
    photo_id: str,
    context: Optional[Dict] = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Reanalyze a photo with updated context"""
    
    try:
        photo_uuid = uuid.UUID(photo_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid photo ID")
    
    photo = db.query(models.PhotoUpload).filter(
        models.PhotoUpload.id == photo_uuid,
        models.PhotoUpload.user_id == current_user.id
    ).first()
    
    if not photo:
        raise HTTPException(status_code=404, detail="Photo not found")
    
    # Note: In a real implementation, you'd need to retrieve the original image data
    # For this example, we'll return an error message
    
    raise HTTPException(
        status_code=501,
        detail="Reanalysis requires the original image data. Please upload the photo again."
    )

@router.delete("/{photo_id}")
async def delete_photo(
    photo_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Delete a photo and its analysis"""
    
    try:
        photo_uuid = uuid.UUID(photo_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid photo ID")
    
    photo = db.query(models.PhotoUpload).filter(
        models.PhotoUpload.id == photo_uuid,
        models.PhotoUpload.user_id == current_user.id
    ).first()
    
    if not photo:
        raise HTTPException(status_code=404, detail="Photo not found")
    
    # Delete analysis first
    db.query(models.PhotoAnalysis).filter(
        models.PhotoAnalysis.photo_id == photo_uuid
    ).delete()
    
    # Delete photo record
    db.delete(photo)
    db.commit()
    
    return {"message": "Photo deleted successfully"}