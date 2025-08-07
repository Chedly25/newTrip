import pytest
from fastapi.testclient import TestClient
from app import models
from tests.conftest import client, db_session

def test_read_root(client):
    """Test the root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert data["message"] == "Wanderlog AI API"

def test_health_check(client):
    """Test the health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

def test_get_cities_empty(client):
    """Test getting cities when none exist"""
    response = client.get("/api/v1/cities/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) == 0

def test_create_and_get_city(client, db_session):
    """Test creating a city and retrieving it"""
    # Create a test city
    city = models.City(
        name="Test City",
        region="Test Region",
        country="France",
        population=100000
    )
    db_session.add(city)
    db_session.commit()
    
    # Get cities
    response = client.get("/api/v1/cities/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["name"] == "Test City"
    assert data[0]["region"] == "Test Region"

def test_get_nonexistent_city(client):
    """Test getting a city that doesn't exist"""
    response = client.get("/api/v1/cities/999")
    assert response.status_code == 404

def test_search_places_empty(client):
    """Test searching places when none exist"""
    response = client.get("/api/v1/places/search/?q=test")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) == 0

def test_get_nonexistent_place(client):
    """Test getting a place that doesn't exist"""
    import uuid
    fake_id = str(uuid.uuid4())
    response = client.get(f"/api/v1/places/{fake_id}")
    assert response.status_code == 404

def test_chat_without_anthropic_key(client):
    """Test chat endpoint without Anthropic API key"""
    # This will fail gracefully if no API key is configured
    response = client.post("/api/v1/chat/", json={
        "message": "Hello"
    })
    # Should return 200 even if Claude service fails gracefully
    assert response.status_code == 200
    data = response.json()
    assert "response" in data
    assert "conversation_id" in data

@pytest.mark.asyncio
async def test_claude_service():
    """Test Claude AI service initialization"""
    from app.core.claude_ai import ClaudeAIService
    
    service = ClaudeAIService()
    assert service is not None
    assert service.model == "claude-3-sonnet-20241022"

def test_place_scorer():
    """Test place scoring algorithm"""
    from app.services.place_scorer import PlaceScorer
    
    score = PlaceScorer.calculate_gem_score(
        local_mentions=10,
        tourist_mentions=2,
        sentiment=0.5,
        days_since_discovery=15
    )
    
    assert 0 <= score <= 100
    assert isinstance(score, float)

def test_redis_cache_wrapper():
    """Test Redis cache wrapper"""
    from app.core.cache import cache_key_wrapper
    
    # Test that the decorator can be applied
    @cache_key_wrapper("test", 60)
    async def dummy_function():
        return {"test": "data"}
    
    assert callable(dummy_function)