from sqlalchemy import Column, String, DateTime, Enum, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..core.database import Base
import enum


class OwnerType(enum.Enum):
    alejandra = "alejandra"
    alessandro = "alessandro"
    bianca = "bianca"
    jesus = "jesus"
    julia = "julia"
    samuel = "samuel"


class Influencer(Base):
    __tablename__ = "influencers"

    id = Column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    first_name = Column(String(255), nullable=False)
    eldorado_username = Column(String(100), unique=True, nullable=False, index=True)
    phone = Column(String(20))
    country = Column(String(100))
    owner = Column(Enum(OwnerType), nullable=False)
    status = Column(String(20), default="active")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    influencer_ids = relationship("InfluencerIds", back_populates="influencer", uselist=False, cascade="all, delete-orphan")
    tiktok_videos = relationship("TikTokVideo", back_populates="influencer", cascade="all, delete-orphan")
    partnerships = relationship("Partnership", back_populates="influencer", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Influencer(eldorado_username='{self.eldorado_username}', first_name='{self.first_name}')>"