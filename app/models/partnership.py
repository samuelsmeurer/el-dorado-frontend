from sqlalchemy import Column, String, Integer, Date, Numeric, DateTime, ForeignKey, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..core.database import Base


class Partnership(Base):
    __tablename__ = "partnerships"

    id = Column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    eldorado_username = Column(String(100), ForeignKey("influencers.eldorado_username"), nullable=False)
    campaign_id = Column(UUID(as_uuid=True), ForeignKey("campaigns.id"))
    contract_value = Column(Numeric(10, 2))
    expected_videos = Column(Integer)
    delivered_videos = Column(Integer, default=0)
    status = Column(String(20), default="active")
    start_date = Column(Date)
    end_date = Column(Date)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    influencer = relationship("Influencer", back_populates="partnerships")
    campaign = relationship("Campaign", back_populates="partnerships")

    def __repr__(self):
        return f"<Partnership(influencer='{self.eldorado_username}', delivered={self.delivered_videos}/{self.expected_videos})>"