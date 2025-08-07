from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
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

router = APIRouter(prefix="/budget", tags=["Intelligent Budget & Expense Tracking"])

claude_service = ClaudeAIService()

# Budget and expense models
class ExpenseCreate(BaseModel):
    trip_id: Optional[str] = None
    category_id: int
    amount: float
    currency: str = "EUR"
    description: str
    location: Optional[str] = None
    expense_date: datetime
    is_shared_expense: bool = False
    split_count: int = 1

class ExpenseResponse(BaseModel):
    id: str
    category_name: str
    amount: float
    currency: str
    description: str
    location: Optional[str]
    expense_date: datetime
    created_at: datetime

class BudgetAnalysisRequest(BaseModel):
    trip_id: Optional[str] = None
    total_budget: float
    currency: str = "EUR"
    analyze_period_days: int = 30

# Initialize expense categories if not exists
@router.on_event("startup")
async def create_default_categories():
    """Create default expense categories"""
    # This would typically be done in a migration
    pass

@router.get("/categories")
async def get_expense_categories(db: Session = Depends(get_db)):
    """Get all expense categories"""
    
    categories = db.query(models.ExpenseCategory).all()
    
    # If no categories exist, create defaults
    if not categories:
        default_categories = [
            {"name": "Accommodation", "icon": "🏨", "color": "#FF6B6B", "default_budget_percentage": 35.0},
            {"name": "Food & Dining", "icon": "🍽️", "color": "#4ECDC4", "default_budget_percentage": 25.0},
            {"name": "Transportation", "icon": "🚗", "color": "#45B7D1", "default_budget_percentage": 20.0},
            {"name": "Activities & Tours", "icon": "🎭", "color": "#F9CA24", "default_budget_percentage": 15.0},
            {"name": "Shopping", "icon": "🛍️", "color": "#6C5CE7", "default_budget_percentage": 3.0},
            {"name": "Miscellaneous", "icon": "💰", "color": "#A0A0A0", "default_budget_percentage": 2.0}
        ]
        
        for cat_data in default_categories:
            category = models.ExpenseCategory(**cat_data)
            db.add(category)
        
        db.commit()
        categories = db.query(models.ExpenseCategory).all()
    
    return [
        {
            "id": cat.id,
            "name": cat.name,
            "icon": cat.icon,
            "color": cat.color,
            "default_budget_percentage": cat.default_budget_percentage
        }
        for cat in categories
    ]

@router.post("/expenses", response_model=ExpenseResponse)
async def add_expense(
    expense: ExpenseCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Add a new expense"""
    
    # Validate category exists
    category = db.query(models.ExpenseCategory).filter(
        models.ExpenseCategory.id == expense.category_id
    ).first()
    
    if not category:
        raise HTTPException(status_code=404, detail="Expense category not found")
    
    # Validate trip if provided
    trip_uuid = None
    if expense.trip_id:
        try:
            trip_uuid = uuid.UUID(expense.trip_id)
            trip = db.query(models.Itinerary).filter(
                models.Itinerary.id == trip_uuid,
                models.Itinerary.user_id == current_user.id
            ).first()
            if not trip:
                raise HTTPException(status_code=404, detail="Trip not found")
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid trip ID")
    
    # Create expense
    new_expense = models.Expense(
        user_id=current_user.id,
        trip_id=trip_uuid,
        category_id=expense.category_id,
        amount=expense.amount,
        currency=expense.currency,
        description=expense.description,
        location=expense.location,
        expense_date=expense.expense_date,
        is_shared_expense=expense.is_shared_expense,
        split_count=expense.split_count
    )
    
    db.add(new_expense)
    db.commit()
    db.refresh(new_expense)
    
    return {
        "id": str(new_expense.id),
        "category_name": category.name,
        "amount": new_expense.amount,
        "currency": new_expense.currency,
        "description": new_expense.description,
        "location": new_expense.location,
        "expense_date": new_expense.expense_date,
        "created_at": new_expense.created_at
    }

@router.get("/expenses")
async def get_user_expenses(
    trip_id: Optional[str] = None,
    category_id: Optional[int] = None,
    days: int = 30,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Get user's expenses with optional filters"""
    
    query = db.query(models.Expense, models.ExpenseCategory).join(
        models.ExpenseCategory
    ).filter(
        models.Expense.user_id == current_user.id,
        models.Expense.expense_date >= datetime.utcnow() - timedelta(days=days)
    )
    
    if trip_id:
        try:
            trip_uuid = uuid.UUID(trip_id)
            query = query.filter(models.Expense.trip_id == trip_uuid)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid trip ID")
    
    if category_id:
        query = query.filter(models.Expense.category_id == category_id)
    
    expenses = query.order_by(models.Expense.expense_date.desc()).all()
    
    return [
        {
            "id": str(expense.Expense.id),
            "category_name": expense.ExpenseCategory.name,
            "category_icon": expense.ExpenseCategory.icon,
            "amount": expense.Expense.amount,
            "currency": expense.Expense.currency,
            "description": expense.Expense.description,
            "location": expense.Expense.location,
            "expense_date": expense.Expense.expense_date,
            "is_shared": expense.Expense.is_shared_expense,
            "split_count": expense.Expense.split_count,
            "created_at": expense.Expense.created_at
        }
        for expense in expenses
    ]

@router.post("/analyze")
async def analyze_budget_with_ai(
    request: BudgetAnalysisRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Get AI-powered budget analysis and recommendations"""
    
    try:
        # Get expenses for analysis
        query = db.query(models.Expense, models.ExpenseCategory).join(
            models.ExpenseCategory
        ).filter(
            models.Expense.user_id == current_user.id,
            models.Expense.expense_date >= datetime.utcnow() - timedelta(days=request.analyze_period_days)
        )
        
        if request.trip_id:
            try:
                trip_uuid = uuid.UUID(request.trip_id)
                query = query.filter(models.Expense.trip_id == trip_uuid)
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid trip ID")
        
        expenses_data = query.all()
        
        # Prepare expense data for AI analysis
        expenses_for_ai = [
            {
                "category": expense.ExpenseCategory.name,
                "amount": expense.Expense.amount,
                "description": expense.Expense.description,
                "location": expense.Expense.location,
                "date": expense.Expense.expense_date.isoformat()
            }
            for expense in expenses_data
        ]
        
        # Get trip information if available
        trip_info = {}
        if request.trip_id:
            trip = db.query(models.Itinerary).filter(
                models.Itinerary.id == uuid.UUID(request.trip_id)
            ).first()
            if trip:
                city = db.query(models.City).filter(models.City.id == trip.city_id).first()
                trip_info = {
                    "destination": city.name if city else "France",
                    "duration": (trip.end_date - trip.start_date).days if trip.start_date and trip.end_date else None,
                    "travel_style": trip.preferences.get("travel_style", "moderate") if trip.preferences else "moderate"
                }
        
        # Get AI analysis
        budget_info = {
            "total_budget": request.total_budget,
            "currency": request.currency,
            "duration_days": request.analyze_period_days,
            **trip_info
        }
        
        ai_analysis = await claude_service.analyze_budget(expenses_for_ai, budget_info)
        
        if "error" in ai_analysis:
            raise HTTPException(status_code=500, detail=ai_analysis["error"])
        
        # Calculate summary statistics
        total_spent = sum(exp.Expense.amount for exp in expenses_data)
        category_breakdown = {}
        for expense in expenses_data:
            cat_name = expense.ExpenseCategory.name
            category_breakdown[cat_name] = category_breakdown.get(cat_name, 0) + expense.Expense.amount
        
        # Save analysis to database
        analysis_record = models.BudgetAnalysis(
            user_id=current_user.id,
            trip_id=uuid.UUID(request.trip_id) if request.trip_id else None,
            total_budget=request.total_budget,
            total_spent=total_spent,
            currency=request.currency,
            category_breakdown=category_breakdown,
            ai_insights=ai_analysis.get("insights", ""),
            budget_alerts=ai_analysis.get("alerts", []),
            money_saving_tips=ai_analysis.get("money_saving_tips", "")
        )
        
        db.add(analysis_record)
        db.commit()
        
        return {
            "analysis_id": str(analysis_record.id),
            "total_budget": request.total_budget,
            "total_spent": total_spent,
            "remaining_budget": request.total_budget - total_spent,
            "budget_utilization_percent": (total_spent / request.total_budget * 100) if request.total_budget > 0 else 0,
            "category_breakdown": category_breakdown,
            "ai_analysis": ai_analysis.get("analysis", ""),
            "ai_insights": ai_analysis.get("insights", ""),
            "recommendations": ai_analysis.get("recommendations", []),
            "alerts": ai_analysis.get("alerts", []),
            "money_saving_tips": ai_analysis.get("money_saving_tips", ""),
            "currency": request.currency,
            "analysis_period_days": request.analyze_period_days
        }
        
    except Exception as e:
        logger.error(f"Budget analysis error: {e}")
        raise HTTPException(status_code=500, detail="Failed to analyze budget")

@router.get("/analysis-history")
async def get_budget_analysis_history(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Get user's budget analysis history"""
    
    analyses = db.query(models.BudgetAnalysis).filter(
        models.BudgetAnalysis.user_id == current_user.id
    ).order_by(models.BudgetAnalysis.analysis_date.desc()).limit(10).all()
    
    return [
        {
            "id": str(analysis.id),
            "total_budget": analysis.total_budget,
            "total_spent": analysis.total_spent,
            "currency": analysis.currency,
            "category_breakdown": analysis.category_breakdown,
            "ai_insights": analysis.ai_insights[:200] + "..." if len(analysis.ai_insights) > 200 else analysis.ai_insights,
            "analysis_date": analysis.analysis_date,
            "trip_id": str(analysis.trip_id) if analysis.trip_id else None
        }
        for analysis in analyses
    ]

@router.get("/summary")
async def get_budget_summary(
    trip_id: Optional[str] = None,
    days: int = 30,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Get budget summary for dashboard"""
    
    query = db.query(models.Expense, models.ExpenseCategory).join(
        models.ExpenseCategory
    ).filter(
        models.Expense.user_id == current_user.id,
        models.Expense.expense_date >= datetime.utcnow() - timedelta(days=days)
    )
    
    if trip_id:
        try:
            trip_uuid = uuid.UUID(trip_id)
            query = query.filter(models.Expense.trip_id == trip_uuid)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid trip ID")
    
    expenses = query.all()
    
    # Calculate summary
    total_spent = sum(exp.Expense.amount for exp in expenses)
    
    category_totals = {}
    daily_spending = {}
    
    for expense in expenses:
        # Category totals
        cat_name = expense.ExpenseCategory.name
        category_totals[cat_name] = category_totals.get(cat_name, 0) + expense.Expense.amount
        
        # Daily spending
        date_str = expense.Expense.expense_date.strftime('%Y-%m-%d')
        daily_spending[date_str] = daily_spending.get(date_str, 0) + expense.Expense.amount
    
    # Calculate averages
    days_with_spending = len(daily_spending)
    avg_daily_spending = total_spent / max(1, days_with_spending)
    
    return {
        "period_days": days,
        "total_spent": total_spent,
        "total_expenses": len(expenses),
        "average_daily_spending": avg_daily_spending,
        "days_with_spending": days_with_spending,
        "category_breakdown": category_totals,
        "daily_spending": daily_spending,
        "currency": "EUR",  # Default currency
        "top_category": max(category_totals.items(), key=lambda x: x[1])[0] if category_totals else None,
        "top_category_amount": max(category_totals.values()) if category_totals else 0
    }

@router.delete("/expenses/{expense_id}")
async def delete_expense(
    expense_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Delete an expense"""
    
    try:
        expense_uuid = uuid.UUID(expense_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid expense ID")
    
    expense = db.query(models.Expense).filter(
        models.Expense.id == expense_uuid,
        models.Expense.user_id == current_user.id
    ).first()
    
    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found")
    
    db.delete(expense)
    db.commit()
    
    return {"message": "Expense deleted successfully"}

@router.get("/insights/tips")
async def get_money_saving_tips(
    location: str = "France",
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Get AI-generated money saving tips for a location"""
    
    try:
        # Get recent expenses for context
        recent_expenses = db.query(models.Expense, models.ExpenseCategory).join(
            models.ExpenseCategory
        ).filter(
            models.Expense.user_id == current_user.id,
            models.Expense.expense_date >= datetime.utcnow() - timedelta(days=30)
        ).limit(50).all()
        
        expenses_for_ai = [
            {
                "category": exp.ExpenseCategory.name,
                "amount": exp.Expense.amount,
                "location": exp.Expense.location or location
            }
            for exp in recent_expenses
        ]
        
        # Use general AI assistance for tips
        prompt = f"""Provide specific money-saving tips for travelers in {location}. 
        Consider these recent expense categories: {[exp['category'] for exp in expenses_for_ai[:10]]}
        
        Give practical, actionable advice for:
        1. Accommodation savings
        2. Food and dining on a budget
        3. Transportation hacks
        4. Free and low-cost activities
        5. Shopping and souvenir tips
        
        Be specific to French culture and locations."""
        
        tips = await claude_service.general_ai_assistance(
            prompt, 
            {"location": location, "user_expenses": expenses_for_ai[:5]}, 
            "budget_advisor"
        )
        
        return {
            "location": location,
            "tips": tips,
            "generated_at": datetime.utcnow()
        }
        
    except Exception as e:
        logger.error(f"Tips generation error: {e}")
        return {
            "location": location,
            "tips": f"Here are some general money-saving tips for {location}: Use public transportation, eat at local markets, book accommodations in advance, and look for free walking tours.",
            "generated_at": datetime.utcnow()
        }