from celery import current_app as celery_app
from app.services.scraper import RedditScraper
from app.services.place_scorer import PlaceScorer
from app.database import get_db_session
import logging

logger = logging.getLogger(__name__)

@celery_app.task
def scrape_reddit_mentions(subreddit_name: str, limit: int = 50):
    """Background task to scrape Reddit for place mentions"""
    try:
        scraper = RedditScraper()
        mentions = scraper.scrape_subreddit(subreddit_name, limit)
        logger.info(f"Scraped {len(mentions)} mentions from r/{subreddit_name}")
        return {"status": "success", "mentions_count": len(mentions)}
    except Exception as e:
        logger.error(f"Error scraping Reddit: {e}")
        return {"status": "error", "message": str(e)}

@celery_app.task
def update_gem_scores(city_id: int):
    """Background task to update gem scores for a city"""
    try:
        with get_db_session() as db:
            PlaceScorer.update_all_scores(db, city_id)
        logger.info(f"Updated gem scores for city {city_id}")
        return {"status": "success", "city_id": city_id}
    except Exception as e:
        logger.error(f"Error updating scores: {e}")
        return {"status": "error", "message": str(e)}

@celery_app.task
def health_check():
    """Simple health check task"""
    return {"status": "healthy", "message": "Celery is working!"}