from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .core.config import settings
from .routes import influencers_router, videos_router, analytics_router

app = FastAPI(
    title=settings.app_name,
    version=settings.version,
    description="API para gerenciar vídeos patrocinados de influenciadores da El Dorado",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(influencers_router)
app.include_router(videos_router)
app.include_router(analytics_router)


@app.get("/")
def root():
    """API root endpoint with basic information"""
    return {
        "service": settings.app_name,
        "version": settings.version,
        "description": "Sistema de gerenciamento de vídeos patrocinados de influenciadores",
        "docs": "/docs",
        "health": "/health",
        "endpoints": {
            "influencers": "/api/v1/influencers",
            "videos": "/api/v1/videos", 
            "analytics": "/api/v1/analytics"
        }
    }


@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": settings.app_name,
        "version": settings.version
    }