from typing import List, Dict
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func
import logging

from app import models

logger = logging.getLogger(__name__)

class PlaceScorer:
    """Calculate hidden gem scores"""
    
    @staticmethod
    def calculate_gem_score(
        local_mentions: int,
        tourist_mentions: int,
        sentiment: float,
        days_since_discovery: int = 30
    ) -> float:
        """Calculate hidden gem score (0-100)"""
        
        # Base score: high local, low tourist
        if tourist_mentions == 0:
            tourist_ratio = 0
        else:
            tourist_ratio = tourist_mentions / (local_mentions + tourist_mentions)
        
        base_score = (1 - tourist_ratio) * 100
        
        # Adjust for sentiment
        sentiment_multiplier = max(0.5, min(1.5, sentiment + 1))
        
        # Freshness bonus
        freshness_bonus = max(0, 30 - days_since_discovery) / 30 * 20
        
        # Calculate final score
        score = (base_score * sentiment_multiplier) + freshness_bonus
        
        return min(100, max(0, score))
    
    @staticmethod
    def calculate_authenticity_score(
        place: models.Place,
        db: Session
    ) -> float:
        """Calculate authenticity score based on multiple factors"""
        
        score = 100
        
        # Deduct for tourist indicators
        if place.michelin_stars:
            score -= 20  # Michelin stars attract tourists
            
        if "tour eiffel" in place.address.lower() if place.address else False:
            score -= 30  # Near major tourist attractions
            
        # Add for local indicators
        recent_mentions = db.query(models.Mention).filter(
            models.Mention.place_id == place.id,
            models.Mention.is_local_author == True,
            models.Mention.mention_date > datetime.utcnow() - timedelta(days=30)
        ).count()
        
        if recent_mentions > 10:
            score += 20
            
        return min(100, max(0, score))
    
    @staticmethod
    def update_all_scores(db: Session, city_id: int):
        """Update gem scores for all places in a city"""
        
        places = db.query(models.Place).filter(
            models.Place.city_id == city_id
        ).all()
        
        for place in places:
            # Calculate mentions
            local_mentions = db.query(models.Mention).filter(
                models.Mention.place_id == place.id,
                models.Mention.is_local_author == True,
                models.Mention.mention_date > datetime.utcnow() - timedelta(days=7)
            ).count()
            
            tourist_mentions = db.query(models.Mention).filter(
                models.Mention.place_id == place.id,
                models.Mention.is_local_author == False,
                models.Mention.mention_date > datetime.utcnow() - timedelta(days=7)
            ).count()
            
            # Calculate average sentiment
            avg_sentiment = db.query(func.avg(models.Mention.sentiment_score)).filter(
                models.Mention.place_id == place.id
            ).scalar() or 0
            
            # Calculate scores
            gem_score = PlaceScorer.calculate_gem_score(
                local_mentions,
                tourist_mentions,
                avg_sentiment
            )
            
            authenticity_score = PlaceScorer.calculate_authenticity_score(place, db)
            
            # Update or create gem score
            existing_score = db.query(models.GemScore).filter(
                models.GemScore.place_id == place.id,
                func.date(models.GemScore.score_date) == datetime.utcnow().date()
            ).first()
            
            if existing_score:
                existing_score.hidden_gem_score = gem_score
                existing_score.authenticity_score = authenticity_score
                existing_score.local_mentions_7d = local_mentions
            else:
                new_score = models.GemScore(
                    place_id=place.id,
                    hidden_gem_score=gem_score,
                    authenticity_score=authenticity_score,
                    local_mentions_7d=local_mentions,
                    tourism_saturation=tourist_mentions / max(1, local_mentions + tourist_mentions)
                )
                db.add(new_score)
        
        db.commit()
        logger.info(f"Updated scores for {len(places)} places in city {city_id}")