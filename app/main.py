from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .core.config import settings
from .routes import influencers_router, videos_router, analytics_router
import os
import subprocess

# Run migrations on startup (only in production)
if os.getenv("RAILWAY_ENVIRONMENT") or os.getenv("PORT"):  # Railway environment
    try:
        print("🚀 Running database migrations...")
        result = subprocess.run(["alembic", "upgrade", "head"], 
                              capture_output=True, text=True, cwd="/app")
        if result.returncode == 0:
            print("✅ Migrations completed successfully")
        else:
            print(f"❌ Migration failed: {result.stderr}")
    except Exception as e:
        print(f"⚠️ Migration error: {e}")

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


@app.post("/admin/clean-invalid-owners")
def clean_invalid_owners():
    """Emergency endpoint to clean invalid owner data"""
    from .core.database import get_db
    from .models import Influencer
    
    db = next(get_db())
    try:
        # Find all records
        all_influencers = db.query(Influencer).all()
        
        # Delete records that would cause enum errors
        deleted_count = 0
        for influencer in all_influencers:
            try:
                # Try to access the owner field - this will fail if invalid
                _ = influencer.owner
            except:
                # If accessing owner fails, delete this record
                db.delete(influencer)
                deleted_count += 1
        
        db.commit()
        
        return {
            "success": True,
            "deleted_records": deleted_count,
            "message": f"Deleted {deleted_count} records with invalid owner values"
        }
    except Exception as e:
        db.rollback()
        return {
            "success": False,
            "error": str(e)
        }
    finally:
        db.close()