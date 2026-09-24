import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Numeric, Integer, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.core.database import Base


class Bid(Base):
    __tablename__ = "bids"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    rfq_id = Column(UUID(as_uuid=True), ForeignKey("rfqs.id", ondelete="CASCADE"), nullable=False, index=True)
    supplier_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)

    carrier_name = Column(String(255), nullable=False)
    freight_charges = Column(Numeric(12, 2), nullable=False)
    origin_charges = Column(Numeric(12, 2), nullable=False)
    destination_charges = Column(Numeric(12, 2), nullable=False)
    total_amount = Column(Numeric(12, 2), nullable=False, index=True)

    transit_time_days = Column(Integer, nullable=False)
    validity_date = Column(DateTime(timezone=True), nullable=False)

    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False, index=True)

    # Relationships
    rfq = relationship("RFQ", back_populates="bids", lazy="selectin")
    supplier = relationship("User", back_populates="bids", lazy="selectin")
    activity_logs = relationship("ActivityLog", back_populates="bid", cascade="all, delete-orphan", lazy="selectin")
