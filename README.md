# Wanderlog AI - French Hidden Gems Discovery Platform

![Wanderlog AI](https://img.shields.io/badge/Wanderlog-AI-blue)
![Python](https://img.shields.io/badge/Python-3.11+-green)
![FastAPI](https://img.shields.io/badge/FastAPI-0.109-red)
![Claude](https://img.shields.io/badge/Claude-3%20Sonnet-purple)

A smart travel platform that discovers hidden gems in France using AI-powered analysis of local mentions, Reddit discussions, and authentic travel data.

## 🎯 Features

- **AI-Powered Discovery**: Uses Claude AI to analyze and extract place information from text
- **Hidden Gem Scoring**: Proprietary algorithm to identify authentic, non-touristy places
- **Reddit Integration**: Scrapes local subreddits for genuine recommendations
- **Interactive Chat**: Claude-powered travel assistant for personalized advice
- **Itinerary Generation**: AI-generated travel plans with hidden gems
- **Geospatial Data**: PostGIS integration for location-based features

## 🏗️ Architecture

- **Backend**: FastAPI with SQLAlchemy and PostgreSQL/PostGIS
- **AI**: Anthropic Claude API integration
- **Caching**: Redis for performance optimization
- **Authentication**: JWT-based user authentication
- **Background Tasks**: Celery for scraping and scoring
- **Deployment**: Docker containerization with multiple platform support

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- PostgreSQL 15+ with PostGIS
- Redis
- Anthropic API key

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/wanderlog-ai.git
cd wanderlog-ai
```

2. **Set up virtual environment**
```bash
cd backend
python -m venv venv
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure environment**
```bash
cp .env.example .env
# Edit .env with your API keys and database URL
```

5. **Set up database**
```bash
# Create PostgreSQL database
createdb wanderlog_db

# Run migrations
alembic upgrade head
```

6. **Start the application**
```bash
uvicorn app.main:app --reload
```

Visit http://localhost:8000/api/docs for the API documentation.

## 🐳 Docker Setup

### Development with Docker Compose

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f backend

# Stop services
docker-compose down
```

### Production Docker Build

```bash
# Build the image
docker build -t wanderlog-ai ./backend

# Run with environment variables
docker run -p 8000:8000 \
  -e DATABASE_URL=your_db_url \
  -e REDIS_URL=your_redis_url \
  -e ANTHROPIC_API_KEY=your_key \
  wanderlog-ai
```

## 📊 API Endpoints

### Cities
- `GET /api/v1/cities/` - List all French cities
- `GET /api/v1/cities/{city_id}` - Get city details
- `GET /api/v1/cities/{city_id}/gems` - Get hidden gems for a city

### Places
- `GET /api/v1/places/{place_id}` - Get place details with scores
- `GET /api/v1/places/search/` - Search places

### Chat
- `POST /api/v1/chat/` - Chat with AI travel assistant
- `DELETE /api/v1/chat/{conversation_id}` - Clear conversation

### Authentication
- `POST /api/v1/auth/register` - Register new user
- `POST /api/v1/auth/token` - Login and get token
- `GET /api/v1/auth/me` - Get current user info

### Itineraries
- `POST /api/v1/itineraries/` - Create AI-generated itinerary
- `GET /api/v1/itineraries/` - Get user's itineraries
- `GET /api/v1/itineraries/{itinerary_id}` - Get specific itinerary

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_api.py -v
```

## 🚀 Deployment Options

### 1. Railway.app (Recommended - Easiest)

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login and deploy
railway login
railway init
railway add postgresql
railway add redis
railway up

# Set environment variables
railway variables set ANTHROPIC_API_KEY=your-key
```

### 2. Render.com (Free Tier Available)

1. Connect your GitHub repository to Render
2. Create a PostgreSQL database
3. Create a Redis instance
4. Deploy the web service
5. Set environment variables in Render dashboard

### 3. Heroku

```bash
# Create app
heroku create wanderlog-ai

# Add add-ons
heroku addons:create heroku-postgresql:mini
heroku addons:create heroku-redis:mini

# Set environment variables
heroku config:set ANTHROPIC_API_KEY=your-key

# Deploy
git push heroku main
```

### 4. DigitalOcean App Platform

1. Connect GitHub repository
2. Configure build and run commands
3. Add PostgreSQL and Redis services
4. Set environment variables
5. Deploy

## 🔑 Environment Variables

```env
# Required
DATABASE_URL=postgresql://user:pass@host:port/db
REDIS_URL=redis://localhost:6379/0
ANTHROPIC_API_KEY=sk-ant-api03-...

# Optional
REDDIT_CLIENT_ID=your_reddit_client_id
REDDIT_CLIENT_SECRET=your_reddit_client_secret
SECRET_KEY=your-secret-key
DEBUG=False
ENVIRONMENT=production
```

## 📈 Monitoring & Performance

### Health Checks

- `GET /health` - Application health status
- Monitor database connections
- Redis connectivity checks

### Logging

```python
import logging
logging.basicConfig(level=logging.INFO)
```

### Metrics

- API response times
- Claude API usage and costs
- Database query performance
- Redis cache hit rates

## 🛡️ Security

- JWT-based authentication
- Password hashing with bcrypt
- CORS configuration
- Input validation with Pydantic
- SQL injection prevention with SQLAlchemy
- Rate limiting (implement with slowapi)

## 💰 Cost Estimates

### Claude API (Anthropic)
- Input tokens: ~$3 per million
- Output tokens: ~$15 per million
- Estimated monthly cost: $20-50

### Hosting (Railway.app)
- Starter plan: $5/month
- PostgreSQL: $5-10/month
- Redis: $5/month
- Total: ~$15-20/month

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details

## 🆘 Support

- Create an issue for bugs or feature requests
- Check the API documentation at `/api/docs`
- Review the deployment guides above

## 🎯 Roadmap

- [ ] Mobile app with React Native
- [ ] Real-time notifications
- [ ] Social features (share itineraries)
- [ ] Integration with booking platforms
- [ ] Multi-language support
- [ ] Machine learning recommendation engine
- [ ] Offline mode support

---

Built with ❤️ using FastAPI, Claude AI, and modern Python tools.