from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from ..core.database import get_db
from ..models import Influencer, InfluencerIds
from ..schemas import (
    InfluencerCreate,
    InfluencerUpdate, 
    InfluencerResponse,
    InfluencerIdsResponse
)
from ..services import ScrapTikService

router = APIRouter(prefix="/api/v1/influencers", tags=["influencers"])


@router.get("/", response_model=List[InfluencerResponse])
def list_influencers(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """List all influencers with pagination"""
    influencers = db.query(Influencer).offset(skip).limit(limit).all()
    return influencers


@router.post("/", response_model=InfluencerResponse, status_code=status.HTTP_201_CREATED)
def create_influencer(
    influencer_data: InfluencerCreate,
    db: Session = Depends(get_db)
):
    """Create new influencer and optionally set TikTok username"""
    
    # Check if eldorado_username already exists
    existing = db.query(Influencer).filter(
        Influencer.eldorado_username == influencer_data.eldorado_username
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Influencer with eldorado_username '{influencer_data.eldorado_username}' already exists"
        )
    
    # Create influencer
    db_influencer = Influencer(
        first_name=influencer_data.first_name,
        eldorado_username=influencer_data.eldorado_username,
        phone=influencer_data.phone,
        country=influencer_data.country,
        owner=influencer_data.owner
    )
    
    db.add(db_influencer)
    db.commit()
    db.refresh(db_influencer)
    
    # Create influencer_ids record if TikTok username provided
    if influencer_data.tiktok_username:
        influencer_ids = InfluencerIds(
            eldorado_username=influencer_data.eldorado_username,
            tiktok_username=influencer_data.tiktok_username
        )
        db.add(influencer_ids)
        db.commit()
    
    return db_influencer


@router.get("/{eldorado_username}", response_model=InfluencerResponse)
def get_influencer(
    eldorado_username: str,
    db: Session = Depends(get_db)
):
    """Get influencer by eldorado_username"""
    influencer = db.query(Influencer).filter(
        Influencer.eldorado_username == eldorado_username
    ).first()
    
    if not influencer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Influencer '{eldorado_username}' not found"
        )
    
    return influencer


@router.put("/{eldorado_username}", response_model=InfluencerResponse)
def update_influencer(
    eldorado_username: str,
    influencer_data: InfluencerUpdate,
    db: Session = Depends(get_db)
):
    """Update influencer data"""
    influencer = db.query(Influencer).filter(
        Influencer.eldorado_username == eldorado_username
    ).first()
    
    if not influencer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Influencer '{eldorado_username}' not found"
        )
    
    # Update only provided fields
    for field, value in influencer_data.dict(exclude_unset=True).items():
        setattr(influencer, field, value)
    
    db.commit()
    db.refresh(influencer)
    
    return influencer


@router.delete("/{eldorado_username}", status_code=status.HTTP_204_NO_CONTENT)
def delete_influencer(
    eldorado_username: str,
    db: Session = Depends(get_db)
):
    """Delete influencer and all related data"""
    influencer = db.query(Influencer).filter(
        Influencer.eldorado_username == eldorado_username
    ).first()
    
    if not influencer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Influencer '{eldorado_username}' not found"
        )
    
    db.delete(influencer)
    db.commit()


@router.get("/{eldorado_username}/social-ids", response_model=InfluencerIdsResponse)
def get_influencer_social_ids(
    eldorado_username: str,
    db: Session = Depends(get_db)
):
    """Get social media IDs for influencer"""
    influencer_ids = db.query(InfluencerIds).filter(
        InfluencerIds.eldorado_username == eldorado_username
    ).first()
    
    if not influencer_ids:
        # Return empty structure if no social IDs exist yet
        return InfluencerIdsResponse(eldorado_username=eldorado_username)
    
    return influencer_ids


@router.post("/{eldorado_username}/sync-tiktok-id")
def sync_tiktok_id(
    eldorado_username: str,
    db: Session = Depends(get_db)
):
    """Sync TikTok ID from username using ScrapTik API"""
    
    # Get influencer
    influencer = db.query(Influencer).filter(
        Influencer.eldorado_username == eldorado_username
    ).first()
    
    if not influencer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Influencer '{eldorado_username}' not found"
        )
    
    # Get or create influencer_ids record
    influencer_ids = db.query(InfluencerIds).filter(
        InfluencerIds.eldorado_username == eldorado_username
    ).first()
    
    if not influencer_ids or not influencer_ids.tiktok_username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"No TikTok username found for '{eldorado_username}'"
        )
    
    # Use ScrapTik API to get user ID
    scraptik = ScrapTikService()
    tiktok_id = scraptik.get_user_id_from_username(influencer_ids.tiktok_username)
    
    if not tiktok_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Could not find TikTok ID for username '{influencer_ids.tiktok_username}'"
        )
    
    # Update TikTok ID
    influencer_ids.tiktok_id = tiktok_id
    db.commit()
    
    return {
        "success": True,
        "message": f"TikTok ID synced successfully",
        "eldorado_username": eldorado_username,
        "tiktok_username": influencer_ids.tiktok_username,
        "tiktok_id": tiktok_id
    }