from sqlalchemy import Column, String, DateTime, ForeignKey, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..core.database import Base


class InfluencerIds(Base):
    __tablename__ = "influencer_ids"

    id = Column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    eldorado_username = Column(String(100), ForeignKey("influencers.eldorado_username", ondelete="CASCADE"), unique=True, nullable=False)
    
    # TikTok
    tiktok_username = Column(String(100))
    tiktok_id = Column(String(255))
    
    # Instagram
    instagram_username = Column(String(100))
    instagram_id = Column(String(255))
    
    # Facebook  
    facebook_username = Column(String(100))
    facebook_id = Column(String(255))
    
    # X (Twitter)
    x_username = Column(String(100))
    x_id = Column(String(255))
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    influencer = relationship("Influencer", back_populates="influencer_ids")

    def __repr__(self):
        return f"<InfluencerIds(eldorado_username='{self.eldorado_username}', tiktok_username='{self.tiktok_username}')>"