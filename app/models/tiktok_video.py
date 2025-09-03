from sqlalchemy import Column, String, Integer, DateTime, Text, ForeignKey, text, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..core.database import Base


class TikTokVideo(Base):
    __tablename__ = "tiktok_videos"

    id = Column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    eldorado_username = Column(String(100), ForeignKey("influencers.eldorado_username"), nullable=False)
    tiktok_username = Column(String(100), nullable=False)
    tiktok_video_id = Column(String(255), unique=True, nullable=False, index=True)
    description = Column(Text)
    
    # Métricas
    view_count = Column(Integer, default=0)
    like_count = Column(Integer, default=0) 
    comment_count = Column(Integer, default=0)
    share_count = Column(Integer, default=0)
    
    # URLs
    public_video_url = Column(String(1000))
    watermark_free_url = Column(String(1000))
    
    # Transcrição
    transcription = Column(Text, nullable=True)
    
    # Timestamps
    published_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    influencer = relationship("Influencer", back_populates="tiktok_videos")

    # Índices para performance
    __table_args__ = (
        Index("idx_eldorado_username", "eldorado_username"),
        Index("idx_published_date", "published_at"),
        Index("idx_likes", "like_count"),
        Index("idx_views", "view_count"),
    )

    def __repr__(self):
        return f"<TikTokVideo(id='{self.tiktok_video_id}', username='{self.eldorado_username}', likes={self.like_count})>"
    
    @property
    def engagement_rate(self) -> float:
        """Calculate engagement rate as (likes + comments + shares) / views * 100"""
        if self.view_count == 0:
            return 0.0
        return round((self.like_count + self.comment_count + self.share_count) / self.view_count * 100, 2)