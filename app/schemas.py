from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum
from uuid import UUID


class OwnerType(str, Enum):
    alejandra = "alejandra"
    alessandro = "alessandro"
    bianca = "bianca"
    camilo = "camilo"
    jesus = "jesus"
    julia = "julia"
    samuel = "samuel"


# Owner Schemas
class OwnerBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=50)
    display_name: Optional[str] = Field(None, max_length=100)
    email: Optional[str] = Field(None, max_length=255)
    is_active: bool = True


class OwnerCreate(OwnerBase):
    pass


class OwnerUpdate(BaseModel):
    display_name: Optional[str] = Field(None, max_length=100)
    email: Optional[str] = Field(None, max_length=255)
    is_active: Optional[bool] = None


class OwnerResponse(OwnerBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Influencer Schemas
class InfluencerBase(BaseModel):
    first_name: str = Field(..., min_length=1, max_length=255)
    eldorado_username: str = Field(..., min_length=1, max_length=100)
    phone: Optional[str] = Field(None, max_length=20)
    country: Optional[str] = Field(None, max_length=100)
    owner: OwnerType


class InfluencerCreate(InfluencerBase):
    tiktok_username: Optional[str] = Field(None, max_length=100)


class InfluencerUpdate(BaseModel):
    first_name: Optional[str] = Field(None, min_length=1, max_length=255)
    phone: Optional[str] = Field(None, max_length=20)
    country: Optional[str] = Field(None, max_length=100)
    owner: Optional[OwnerType] = None
    status: Optional[str] = Field(None, max_length=20)


class InfluencerResponse(InfluencerBase):
    id: UUID
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# InfluencerIds Schemas
class InfluencerIdsResponse(BaseModel):
    eldorado_username: str
    tiktok_username: Optional[str] = None
    tiktok_id: Optional[str] = None
    instagram_username: Optional[str] = None
    instagram_id: Optional[str] = None
    facebook_username: Optional[str] = None
    facebook_id: Optional[str] = None
    x_username: Optional[str] = None
    x_id: Optional[str] = None

    class Config:
        from_attributes = True


# TikTok Video Schemas
class TikTokVideoResponse(BaseModel):
    id: UUID
    eldorado_username: str
    tiktok_username: str
    tiktok_video_id: str
    description: Optional[str] = None
    view_count: int
    like_count: int
    comment_count: int
    share_count: int
    public_video_url: Optional[str] = None
    watermark_free_url: Optional[str] = None
    watermark_free_url_alt1: Optional[str] = None
    watermark_free_url_alt2: Optional[str] = None
    transcription: Optional[str] = None
    published_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class VideoSyncResponse(BaseModel):
    success: bool
    message: str
    videos_processed: int
    new_videos: int
    updated_videos: int
    errors: List[str] = []


# Analytics Schemas
class TopVideo(BaseModel):
    eldorado_username: str
    tiktok_username: str
    tiktok_video_id: str
    description: str
    metric_value: int
    published_at: datetime


class InfluencerStats(BaseModel):
    eldorado_username: str
    total_videos: int
    avg_likes: float
    avg_views: float
    best_performance: int
    last_video_date: Optional[datetime] = None


class DashboardStats(BaseModel):
    total_influencers: int
    total_videos: int
    total_views: int
    total_likes: int
    avg_engagement_rate: float
    videos_this_month: int


# Video Transcription Schemas
class VideoTranscriptionRequest(BaseModel):
    tiktok_url: str = Field(..., min_length=1, description="TikTok video URL")


class VideoTranscriptionResponse(BaseModel):
    success: bool
    message: str
    video_found: Optional[bool] = None
    is_influencer_video: Optional[bool] = None
    eldorado_username: Optional[str] = None
    transcription: Optional[str] = None
    video_info: Optional[TikTokVideoResponse] = None