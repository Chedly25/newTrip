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
# Heroku working directory is /app (repository root)
possible_paths = [
    "/app/frontend/dist",           # Absolute path on Heroku
    "frontend/dist",                # Relative from /app working directory
    "./frontend/dist",              # Same as above with explicit ./
    os.path.join(os.getcwd(), "frontend", "dist"),  # Dynamic based on current working directory
]

static_dir = None
for path in possible_paths:
    if os.path.exists(path):
        static_dir = path
        logger.info(f"Found frontend build at: {path}")
        break

if static_dir and os.path.exists(os.path.join(static_dir, "index.html")):
    # Mount static files
    app.mount("/static", StaticFiles(directory=static_dir), name="static")
    
    @app.get("/")
    async def serve_frontend():
        """Serve the main frontend application"""
        index_file = os.path.join(static_dir, "index.html")
        return FileResponse(index_file)
    
    # Catch-all route for SPA routing - this must be last
    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        """Handle SPA routing for frontend"""
        # Don't intercept API routes, docs, or health checks
        if (full_path.startswith("api/") or 
            full_path.startswith("docs") or 
            full_path.startswith("redoc") or 
            full_path == "health"):
            # Let FastAPI handle these routes normally
            from fastapi import HTTPException
            raise HTTPException(status_code=404, detail="Not found")
        
        # Serve the frontend for all other routes
        index_file = os.path.join(static_dir, "index.html")
        return FileResponse(index_file)
        
    logger.info("✅ Frontend successfully mounted and ready to serve!")
    
else:
    logger.warning("⚠️  Frontend build not found. Make sure to run 'npm run build' in the frontend directory.")
    
    @app.get("/")
    async def root():
        return {
            "message": "Wanderlog AI - Premium Travel Companion",
            "version": settings.VERSION,
            "status": "Backend Ready",
            "docs": "/api/docs",
            "frontend_status": "Building... Please wait a moment and refresh.",
            "build_paths_checked": possible_paths
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