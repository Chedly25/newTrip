from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os
import logging

from app.config import settings
from app.database import engine, Base
from app.api.v1 import cities, places, itineraries, chat, auth, photos, content, budget, events, translation, food, safety

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database tables are managed by Alembic migrations
# Remove Base.metadata.create_all(bind=engine) to avoid conflicts

# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.VERSION,
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(cities.router, prefix="/api/v1")
app.include_router(places.router, prefix="/api/v1")
app.include_router(itineraries.router, prefix="/api/v1")
app.include_router(chat.router, prefix="/api/v1")
app.include_router(auth.router, prefix="/api/v1")

# NEW AI-POWERED FEATURE ROUTERS
app.include_router(photos.router, prefix="/api/v1")
app.include_router(content.router, prefix="/api/v1")
app.include_router(budget.router, prefix="/api/v1")
app.include_router(events.router, prefix="/api/v1")
app.include_router(translation.router, prefix="/api/v1")
app.include_router(food.router, prefix="/api/v1")
app.include_router(safety.router, prefix="/api/v1")

# Mount static files for frontend
static_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "..", "frontend", "dist")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")
    
    @app.get("/")
    async def serve_frontend():
        index_file = os.path.join(static_dir, "index.html")
        if os.path.exists(index_file):
            return FileResponse(index_file)
        return {
            "message": "Wanderlog AI API",
            "version": settings.VERSION,
            "docs": "/api/docs"
        }
    
    # Catch-all route for SPA routing
    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        # Don't intercept API routes
        if full_path.startswith("api/"):
            return {
                "message": "API endpoint not found",
                "docs": "/api/docs"
            }
        
        index_file = os.path.join(static_dir, "index.html")
        if os.path.exists(index_file):
            return FileResponse(index_file)
        
        return {
            "message": "Wanderlog AI API",
            "version": settings.VERSION,
            "docs": "/api/docs"
        }
else:
    @app.get("/")
    async def root():
        return {
            "message": "Wanderlog AI API",
            "version": settings.VERSION,
            "docs": "/api/docs",
            "frontend": "Not built yet - run 'npm run build' in frontend directory"
        }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )