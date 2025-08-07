import anthropic
import json
from typing import Dict, List, Optional
import logging

from app.config import settings

logger = logging.getLogger(__name__)

class ClaudeAIService:
    """Claude AI integration for intelligent travel assistance"""
    
    def __init__(self):
        self.client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
        self.model = "claude-3-sonnet-20241022"
    
    async def extract_place_details(self, text: str, city: str) -> Dict:
        """Extract place information from text"""
        try:
            prompt = f"""
            Analyze this text about a place in {city}, France:
            
            "{text}"
            
            Extract the following in JSON format:
            - place_name: Name of the establishment
            - category: Type (restaurant/cafe/bar/attraction)
            - price_level: 1-4 (1=cheap, 4=expensive)
            - is_tourist_trap: true/false
            - local_tips: Insider tips mentioned
            - authenticity_score: 0-100 based on how "local" it seems
            
            Return ONLY valid JSON.
            """
            
            response = self.client.messages.create(
                model=self.model,
                max_tokens=500,
                temperature=0.1,
                messages=[{"role": "user", "content": prompt}]
            )
            
            return json.loads(response.content[0].text)
            
        except Exception as e:
            logger.error(f"Claude AI error: {e}")
            return {}
    
    async def generate_itinerary_narrative(
        self, 
        places: List[Dict], 
        preferences: Dict
    ) -> str:
        """Generate personalized itinerary narrative"""
        try:
            places_text = "\n".join([
                f"- {p['name']}: {p.get('category', 'place')} in {p.get('address', 'location')}"
                for p in places[:10]
            ])
            
            prompt = f"""
            Create an engaging narrative for a day in France visiting these hidden gems:
            
            Places:
            {places_text}
            
            Preferences:
            - Budget: {preferences.get('budget', 'medium')}
            - Style: {preferences.get('travel_style', 'authentic')}
            
            Write 2-3 paragraphs that:
            - Describe the flow of the day
            - Include specific French terms
            - Mention what to eat/drink
            - Create excitement
            
            Be conversational and enthusiastic!
            """
            
            response = self.client.messages.create(
                model=self.model,
                max_tokens=800,
                temperature=0.8,
                messages=[{"role": "user", "content": prompt}]
            )
            
            return response.content[0].text
            
        except Exception as e:
            logger.error(f"Claude AI error: {e}")
            return "Explore these amazing hidden gems!"
    
    async def chat_assistant(
        self, 
        message: str, 
        conversation_history: List[Dict] = None
    ) -> str:
        """Interactive travel assistant"""
        try:
            system_prompt = """You are a knowledgeable French travel expert who knows 
            all the hidden gems. You're enthusiastic about French culture and food. 
            Keep responses concise but informative. Always suggest non-touristy alternatives."""
            
            messages = [
                {"role": "assistant", "content": system_prompt}
            ]
            
            if conversation_history:
                messages.extend(conversation_history[-5:])
            
            messages.append({"role": "user", "content": message})
            
            response = self.client.messages.create(
                model=self.model,
                max_tokens=1000,
                temperature=0.8,
                messages=messages
            )
            
            return response.content[0].text
            
        except Exception as e:
            logger.error(f"Claude AI error: {e}")
            return "I'm having trouble connecting. Please try again!"