from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .core.config import settings
from .routes import influencers_router, videos_router, analytics_router, owners_router
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
app.include_router(owners_router)
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
            "owners": "/api/v1/owners",
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


@app.post("/admin/reset-database")
def reset_database():
    """Emergency endpoint to clear all influencer data"""
    from .core.database import get_db
    from sqlalchemy import text
    
    db = next(get_db())
    try:
        # Delete all records using raw SQL to bypass enum issues
        result = db.execute(text("DELETE FROM influencers"))
        db.commit()
        
        count = result.rowcount
        return {
            "success": True,
            "deleted_records": count,
            "message": f"Cleared all {count} records from influencers table"
        }
    except Exception as e:
        db.rollback()
        return {
            "success": False,
            "error": str(e)
        }
    finally:
        db.close()