import praw
import httpx
from bs4 import BeautifulSoup
from typing import List, Dict
import re
import asyncio
from datetime import datetime
import logging

from app.config import settings

logger = logging.getLogger(__name__)

class RedditScraper:
    """Scrape Reddit for place mentions"""
    
    def __init__(self):
        if settings.REDDIT_CLIENT_ID:
            self.reddit = praw.Reddit(
                client_id=settings.REDDIT_CLIENT_ID,
                client_secret=settings.REDDIT_CLIENT_SECRET,
                user_agent="WanderlogBot/1.0"
            )
        else:
            self.reddit = None
            
        self.place_patterns = [
            r"(?:aller à|essayer|visiter|recommande)\s+([A-Z][^.!?,;]{2,30})",
            r"([A-Z][^.!?,;]{2,30})\s+(?:est super|est génial|est top)",
            r"(?:restaurant|café|bar|bistrot)\s+(?:appelé)?\s*([A-Z][^.!?,;]{2,30})",
        ]
    
    async def scrape_subreddit(self, subreddit_name: str, limit: int = 50) -> List[Dict]:
        """Scrape subreddit for place mentions"""
        if not self.reddit:
            logger.warning("Reddit API not configured")
            return []
            
        mentions = []
        
        try:
            subreddit = self.reddit.subreddit(subreddit_name)
            
            for submission in subreddit.hot(limit=limit):
                if submission.selftext:
                    places = self._extract_places(submission.selftext)
                    
                    for place in places:
                        mentions.append({
                            'source_type': 'reddit',
                            'source_url': f"https://reddit.com{submission.permalink}",
                            'text': submission.selftext[:1000],
                            'place_name': place,
                            'date': datetime.fromtimestamp(submission.created_utc),
                            'engagement': submission.score,
                            'is_local': self._is_local_mention(submission.selftext)
                        })
                
                await asyncio.sleep(1)  # Rate limiting
                
        except Exception as e:
            logger.error(f"Reddit scraping error: {e}")
            
        return mentions
    
    def _extract_places(self, text: str) -> List[str]:
        """Extract potential place names"""
        places = []
        
        for pattern in self.place_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            places.extend([m.strip() for m in matches if len(m.strip()) > 2])
        
        # Filter common words
        stopwords = {'les', 'des', 'une', 'dans', 'avec', 'pour'}
        places = [p for p in places if p.lower() not in stopwords]
        
        return list(set(places))
    
    def _is_local_mention(self, text: str) -> bool:
        """Check if author seems local"""
        local_indicators = ['habitant', 'j\'habite', 'local', 'quartier', 'voisin']
        text_lower = text.lower()
        return any(indicator in text_lower for indicator in local_indicators)

class WebScraper:
    """Scrape websites and blogs"""
    
    def __init__(self):
        self.client = httpx.AsyncClient(timeout=30.0)
    
    async def scrape_blog(self, url: str) -> List[Dict]:
        """Scrape blog for place mentions"""
        mentions = []
        
        try:
            response = await self.client.get(url)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Extract text content
                article = soup.find('article') or soup.find('main')
                if article:
                    text = article.get_text()
                    
                    # Look for place mentions
                    # ... (extraction logic)
                    
        except Exception as e:
            logger.error(f"Web scraping error: {e}")
            
        return mentions
    
    async def close(self):
        """Close the HTTP client"""
        await self.client.aclose()