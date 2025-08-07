import anthropic
import json
from typing import Dict, List, Optional, Any
import logging
import base64
from datetime import datetime, timedelta

from app.config import settings

logger = logging.getLogger(__name__)

class ClaudeAIService:
    """Comprehensive Claude AI integration for all travel features"""
    
    def __init__(self):
        self.client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
        self.model = "claude-3-sonnet-20241022"
        
    def _create_system_prompt(self, role: str) -> str:
        """Create specialized system prompts for different AI roles"""
        system_prompts = {
            "travel_companion": """You are Claude, an expert French travel companion with deep knowledge of France's hidden gems, local culture, and authentic experiences. You're enthusiastic, knowledgeable, and always provide practical, insider advice. You speak with the warmth of a local friend who wants to share the best of France.""",
            
            "trip_planner": """You are Claude, a master trip planner specializing in France. You create detailed, personalized itineraries that balance must-see attractions with hidden gems. You consider budget, travel style, group size, and personal interests to craft perfect travel experiences.""",
            
            "photo_analyst": """You are Claude, an expert in French geography, architecture, and culture. You can identify places, landmarks, and provide rich historical and cultural context about locations in France. You offer photography tips and suggest similar places to visit.""",
            
            "content_creator": """You are Claude, a skilled travel writer who creates engaging content about French destinations. You adapt your writing style to match the requested tone and audience, from casual social media posts to professional travel articles.""",
            
            "budget_advisor": """You are Claude, a financial advisor specializing in travel budgets for France. You analyze spending patterns, provide cost-saving tips, and help optimize travel budgets while maintaining quality experiences.""",
            
            "event_curator": """You are Claude, an expert on French events, festivals, and local activities. You know what's happening across France and can recommend events that match personal interests and travel dates.""",
            
            "cultural_translator": """You are Claude, a cultural interpreter who not only translates languages but explains the cultural context, etiquette, and proper usage of phrases in French social situations.""",
            
            "review_analyst": """You are Claude, an expert at analyzing and synthesizing reviews to provide honest, balanced assessments of places and experiences in France.""",
            
            "food_expert": """You are Claude, a French cuisine expert who understands regional specialties, dietary restrictions, and can provide personalized restaurant recommendations with detailed explanations.""",
            
            "safety_advisor": """You are Claude, a travel safety expert specializing in France. You provide current, practical safety advice while being informative without being alarmist."""
        }
        return system_prompts.get(role, system_prompts["travel_companion"])
    
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
    
    # =============================================================================
    # NEW AI-POWERED FEATURES
    # =============================================================================
    
    # Feature 1: Advanced Travel Companion Chat
    async def advanced_travel_chat(
        self, 
        message: str, 
        context: Dict = None,
        conversation_history: List[Dict] = None,
        chat_type: str = "travel_companion"
    ) -> Dict:
        """Advanced travel companion with context awareness"""
        try:
            system_prompt = self._create_system_prompt(chat_type)
            
            # Add context information to the prompt
            context_info = ""
            if context:
                if context.get('current_location'):
                    context_info += f"User is currently in: {context['current_location']}\n"
                if context.get('travel_dates'):
                    context_info += f"Travel dates: {context['travel_dates']}\n"
                if context.get('interests'):
                    context_info += f"User interests: {', '.join(context['interests'])}\n"
                if context.get('budget'):
                    context_info += f"Budget level: {context['budget']}\n"
            
            full_prompt = f"{system_prompt}\n\nContext:\n{context_info}\nUser: {message}"
            
            messages = [{"role": "user", "content": full_prompt}]
            
            if conversation_history:
                # Add recent conversation history
                messages = conversation_history[-8:] + messages
            
            response = self.client.messages.create(
                model=self.model,
                max_tokens=1200,
                temperature=0.8,
                messages=messages
            )
            
            return {
                "response": response.content[0].text,
                "confidence": 0.9,
                "suggestions": []  # Could add follow-up suggestions
            }
            
        except Exception as e:
            logger.error(f"Claude AI error: {e}")
            return {"response": "I'm having trouble connecting. Please try again!", "confidence": 0.0}
    
    # Feature 2: Photo Analysis & Place Recognition
    async def analyze_photo(self, image_data: str, context: Dict = None) -> Dict:
        """Analyze uploaded photo and provide insights"""
        try:
            system_prompt = self._create_system_prompt("photo_analyst")
            
            prompt = f"""Analyze this photo taken in France. Provide:
            1. Identified places/landmarks (if any)
            2. Architectural style and period
            3. Cultural/historical context
            4. Photography tips for this location
            5. Similar places to visit
            6. Local insights about the area
            
            Context: {context.get('location', 'Unknown location') if context else 'No additional context'}
            
            Return as JSON with keys: identified_places, cultural_context, photography_tips, 
            similar_locations, local_insights, confidence_score (0-1)"""
            
            response = self.client.messages.create(
                model=self.model,
                max_tokens=1000,
                temperature=0.3,
                messages=[{
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image", "source": {
                            "type": "base64",
                            "media_type": "image/jpeg",
                            "data": image_data
                        }}
                    ]
                }]
            )
            
            return json.loads(response.content[0].text)
            
        except Exception as e:
            logger.error(f"Photo analysis error: {e}")
            return {"error": "Failed to analyze photo", "confidence_score": 0.0}
    
    # Feature 3: Content Generation
    async def generate_travel_content(
        self, 
        content_type: str, 
        places: List[Dict], 
        context: Dict
    ) -> Dict:
        """Generate various types of travel content"""
        try:
            system_prompt = self._create_system_prompt("content_creator")
            
            places_text = "\n".join([
                f"- {p.get('name', 'Unknown')}: {p.get('description', '')}"
                for p in places[:10]
            ])
            
            content_specs = {
                "blog_post": {
                    "length": "800-1200 words",
                    "style": "engaging narrative with practical tips"
                },
                "social_media": {
                    "length": "280 characters with hashtags",
                    "style": "catchy and inspiring"
                },
                "trip_summary": {
                    "length": "400-600 words",
                    "style": "detailed recap with highlights"
                },
                "itinerary_narrative": {
                    "length": "200-400 words per day",
                    "style": "descriptive and practical"
                }
            }
            
            spec = content_specs.get(content_type, content_specs["blog_post"])
            
            prompt = f"""Create a {content_type} about these French places:
            
            {places_text}
            
            Requirements:
            - Length: {spec['length']}
            - Style: {spec['style']}
            - Tone: {context.get('tone', 'enthusiastic')}
            - Target audience: {context.get('audience', 'general travelers')}
            - Include practical information and hidden gem insights
            - Make it authentic and avoid clichés
            
            Return as JSON with keys: title, content, word_count, hashtags (if applicable)"""
            
            response = self.client.messages.create(
                model=self.model,
                max_tokens=1500,
                temperature=0.8,
                messages=[{"role": "user", "content": prompt}]
            )
            
            return json.loads(response.content[0].text)
            
        except Exception as e:
            logger.error(f"Content generation error: {e}")
            return {"error": "Failed to generate content"}
    
    # Feature 4: Budget Analysis & Advice
    async def analyze_budget(self, expenses: List[Dict], budget_info: Dict) -> Dict:
        """Analyze expenses and provide budget recommendations"""
        try:
            system_prompt = self._create_system_prompt("budget_advisor")
            
            expense_summary = {}
            total_spent = 0
            
            for expense in expenses:
                category = expense.get('category', 'Other')
                amount = expense.get('amount', 0)
                expense_summary[category] = expense_summary.get(category, 0) + amount
                total_spent += amount
            
            prompt = f"""Analyze this travel budget for France:
            
            Total Budget: {budget_info.get('total_budget', 0)}€
            Total Spent: {total_spent}€
            
            Spending by category:
            {json.dumps(expense_summary, indent=2)}
            
            Trip duration: {budget_info.get('duration_days', 'Unknown')} days
            Travel style: {budget_info.get('travel_style', 'Unknown')}
            
            Provide:
            1. Budget analysis and status
            2. Spending pattern insights
            3. Money-saving recommendations specific to France
            4. Category-wise optimization suggestions
            5. Alerts if overspending in any category
            
            Return as JSON with keys: analysis, insights, recommendations, alerts, money_saving_tips"""
            
            response = self.client.messages.create(
                model=self.model,
                max_tokens=1000,
                temperature=0.5,
                messages=[{"role": "user", "content": prompt}]
            )
            
            return json.loads(response.content[0].text)
            
        except Exception as e:
            logger.error(f"Budget analysis error: {e}")
            return {"error": "Failed to analyze budget"}
    
    # Feature 5: Event Recommendations
    async def recommend_events(
        self, 
        user_preferences: Dict, 
        available_events: List[Dict],
        location: str,
        dates: List[str]
    ) -> Dict:
        """Provide personalized event recommendations"""
        try:
            system_prompt = self._create_system_prompt("event_curator")
            
            events_text = "\n".join([
                f"- {event.get('name', 'Unknown')}: {event.get('description', '')} "
                f"({event.get('event_type', 'Unknown type')})"
                for event in available_events[:20]
            ])
            
            prompt = f"""Recommend events for a traveler in {location} from these options:
            
            {events_text}
            
            User preferences:
            - Interests: {user_preferences.get('interests', [])}
            - Travel dates: {', '.join(dates)}
            - Budget: {user_preferences.get('budget', 'moderate')}
            - Travel style: {user_preferences.get('travel_style', 'balanced')}
            
            For each recommendation, provide:
            1. Why it matches their interests
            2. What makes it special or unique
            3. Practical tips for attending
            4. Similar events they might like
            
            Return as JSON with keys: recommendations (array with event_id, reason, tips, similar_events), 
            general_advice"""
            
            response = self.client.messages.create(
                model=self.model,
                max_tokens=1200,
                temperature=0.7,
                messages=[{"role": "user", "content": prompt}]
            )
            
            return json.loads(response.content[0].text)
            
        except Exception as e:
            logger.error(f"Event recommendation error: {e}")
            return {"error": "Failed to recommend events"}
    
    # Feature 6: Translation with Cultural Context
    async def translate_with_context(
        self, 
        text: str, 
        source_lang: str, 
        target_lang: str,
        context_type: str = "general"
    ) -> Dict:
        """Translate text with cultural context and usage tips"""
        try:
            system_prompt = self._create_system_prompt("cultural_translator")
            
            prompt = f"""Translate this {source_lang} text to {target_lang} with cultural context:
            
            Text: "{text}"
            Context type: {context_type}
            
            Provide:
            1. Accurate translation
            2. Cultural context and meaning
            3. When and how to use this phrase appropriately
            4. Formality level (formal/informal/casual)
            5. Common variations or alternatives
            6. Cultural etiquette tips
            
            Return as JSON with keys: translation, cultural_context, usage_tips, 
            formality_level, alternatives, etiquette_notes"""
            
            response = self.client.messages.create(
                model=self.model,
                max_tokens=800,
                temperature=0.3,
                messages=[{"role": "user", "content": prompt}]
            )
            
            return json.loads(response.content[0].text)
            
        except Exception as e:
            logger.error(f"Translation error: {e}")
            return {"error": "Failed to translate with context"}
    
    # Feature 7: Review Analysis
    async def analyze_reviews(self, reviews: List[str], place_name: str) -> Dict:
        """Analyze multiple reviews and extract insights"""
        try:
            system_prompt = self._create_system_prompt("review_analyst")
            
            reviews_text = "\n".join([f"Review {i+1}: {review[:500]}..." 
                                    for i, review in enumerate(reviews[:50])])
            
            prompt = f"""Analyze these reviews for {place_name} in France:
            
            {reviews_text}
            
            Provide comprehensive analysis:
            1. Overall sentiment and themes
            2. Common positive aspects mentioned
            3. Common complaints or issues
            4. Authenticity assessment (tourist trap vs genuine)
            5. Best times to visit based on reviews
            6. Who would enjoy this place most
            7. Balanced recommendation with pros/cons
            
            Return as JSON with keys: overall_sentiment, positive_themes, negative_themes, 
            authenticity_score, best_times, target_audience, recommendation_summary"""
            
            response = self.client.messages.create(
                model=self.model,
                max_tokens=1000,
                temperature=0.4,
                messages=[{"role": "user", "content": prompt}]
            )
            
            return json.loads(response.content[0].text)
            
        except Exception as e:
            logger.error(f"Review analysis error: {e}")
            return {"error": "Failed to analyze reviews"}
    
    # Feature 8: Food & Restaurant Recommendations
    async def recommend_restaurants(
        self, 
        food_preferences: Dict, 
        location: str,
        available_restaurants: List[Dict]
    ) -> Dict:
        """Provide personalized restaurant recommendations"""
        try:
            system_prompt = self._create_system_prompt("food_expert")
            
            restaurants_text = "\n".join([
                f"- {r.get('name', 'Unknown')}: {r.get('cuisine_type', 'Unknown')} "
                f"(Price: {r.get('price_level', 'Unknown')})"
                for r in available_restaurants[:30]
            ])
            
            prompt = f"""Recommend restaurants in {location} for this diner profile:
            
            Available restaurants:
            {restaurants_text}
            
            Diner preferences:
            - Dietary restrictions: {food_preferences.get('dietary_restrictions', [])}
            - Cuisine preferences: {food_preferences.get('cuisine_preferences', {})}
            - Spice tolerance: {food_preferences.get('spice_tolerance', 'medium')}
            - Budget preference: {food_preferences.get('price_range_preference', 'moderate')}
            - Adventure level: {food_preferences.get('adventure_level', 'moderate')}
            - Allergies: {food_preferences.get('allergies', [])}
            
            For each recommendation:
            1. Why it matches their preferences
            2. Specific dishes to try
            3. When to go and reservation tips
            4. Price estimates
            5. Cultural context of the cuisine
            
            Return as JSON with keys: recommendations (array with restaurant_name, match_reason, 
            recommended_dishes, dining_tips, price_estimate, cultural_notes)"""
            
            response = self.client.messages.create(
                model=self.model,
                max_tokens=1200,
                temperature=0.6,
                messages=[{"role": "user", "content": prompt}]
            )
            
            return json.loads(response.content[0].text)
            
        except Exception as e:
            logger.error(f"Restaurant recommendation error: {e}")
            return {"error": "Failed to recommend restaurants"}
    
    # Feature 9: Safety Assessment
    async def assess_travel_safety(self, location: str, travel_dates: List[str], traveler_profile: Dict) -> Dict:
        """Provide personalized safety assessment and advice"""
        try:
            system_prompt = self._create_system_prompt("safety_advisor")
            
            prompt = f"""Provide a safety assessment for traveling to {location}, France:
            
            Travel dates: {', '.join(travel_dates)}
            
            Traveler profile:
            - Travel experience: {traveler_profile.get('experience_level', 'intermediate')}
            - Group type: {traveler_profile.get('group_type', 'unknown')}
            - Risk tolerance: {traveler_profile.get('risk_tolerance', 'medium')}
            - Special considerations: {traveler_profile.get('special_needs', [])}
            
            Provide current, practical advice on:
            1. Overall safety score (1-10)
            2. Current safety considerations
            3. Areas to be cautious about
            4. Transportation safety
            5. Health considerations
            6. Emergency contacts and procedures
            7. Personal safety tips specific to the location and dates
            8. Cultural considerations for safety
            
            Be informative but not alarmist. Focus on practical, actionable advice.
            
            Return as JSON with keys: safety_score, current_conditions, caution_areas, 
            transport_safety, health_notes, emergency_info, safety_tips, cultural_considerations"""
            
            response = self.client.messages.create(
                model=self.model,
                max_tokens=1000,
                temperature=0.3,
                messages=[{"role": "user", "content": prompt}]
            )
            
            return json.loads(response.content[0].text)
            
        except Exception as e:
            logger.error(f"Safety assessment error: {e}")
            return {"error": "Failed to assess safety"}
    
    # Feature 10: Enhanced Itinerary Planning
    async def create_detailed_itinerary(
        self, 
        destination: str, 
        duration: int,
        traveler_profile: Dict,
        preferences: Dict,
        available_places: List[Dict]
    ) -> Dict:
        """Create a comprehensive, personalized itinerary"""
        try:
            system_prompt = self._create_system_prompt("trip_planner")
            
            places_text = "\n".join([
                f"- {p.get('name', 'Unknown')}: {p.get('category', 'Unknown')} "
                f"({p.get('authenticity_score', 0)}/100 authenticity)"
                for p in available_places[:50]
            ])
            
            prompt = f"""Create a detailed {duration}-day itinerary for {destination}, France:
            
            Available places and attractions:
            {places_text}
            
            Traveler profile:
            - Travel style: {traveler_profile.get('travel_style', 'balanced')}
            - Preferred pace: {traveler_profile.get('preferred_pace', 'moderate')}
            - Budget level: {preferences.get('budget', 'moderate')}
            - Interests: {preferences.get('interests', [])}
            - Group size: {traveler_profile.get('group_size', 1)}
            
            For each day, provide:
            1. Daily theme and focus
            2. Morning, afternoon, and evening activities
            3. Restaurant recommendations for meals
            4. Transportation suggestions between locations
            5. Estimated budget for the day
            6. Backup activities for bad weather
            7. Cultural tips and local insights
            8. Energy level assessment (relaxed/moderate/active)
            
            Balance must-see attractions with hidden gems. Include practical details like 
            opening hours, booking requirements, and travel times.
            
            Return as JSON with keys: itinerary_overview, daily_plans (array with day_number, 
            theme, activities, meals, transport, budget, alternatives, cultural_tips, energy_level)"""
            
            response = self.client.messages.create(
                model=self.model,
                max_tokens=2000,
                temperature=0.7,
                messages=[{"role": "user", "content": prompt}]
            )
            
            return json.loads(response.content[0].text)
            
        except Exception as e:
            logger.error(f"Itinerary creation error: {e}")
            return {"error": "Failed to create itinerary"}
    
    # Utility method for general AI assistance
    async def general_ai_assistance(self, prompt: str, context: Dict = None, role: str = "travel_companion") -> str:
        """General AI assistance with flexible prompts"""
        try:
            system_prompt = self._create_system_prompt(role)
            
            full_prompt = f"{system_prompt}\n\n{prompt}"
            if context:
                full_prompt += f"\n\nContext: {json.dumps(context, indent=2)}"
            
            response = self.client.messages.create(
                model=self.model,
                max_tokens=1500,
                temperature=0.7,
                messages=[{"role": "user", "content": full_prompt}]
            )
            
            return response.content[0].text
            
        except Exception as e:
            logger.error(f"General AI assistance error: {e}")
            return "I'm having trouble processing your request. Please try again!"