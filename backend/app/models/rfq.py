import enum
import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, ForeignKey, Enum as SAEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.core.database import Base


class RFQStatus(str, enum.Enum):
    DRAFT = "DRAFT"
    SCHEDULED = "SCHEDULED"
    ACTIVE = "ACTIVE"
    CLOSED = "CLOSED"
    FORCE_CLOSED = "FORCE_CLOSED"


class RFQ(Base):
    __tablename__ = "rfqs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    reference_id = Column(String(100), unique=True, index=True, nullable=False)
    pickup_service_date = Column(DateTime(timezone=True), nullable=False)
    status = Column(SAEnum(RFQStatus, name="rfq_status", native_enum=False), default=RFQStatus.DRAFT, nullable=False, index=True)
    buyer_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)

    bid_start_time = Column(DateTime(timezone=True), nullable=False)
    bid_close_time = Column(DateTime(timezone=True), nullable=False)
    forced_bid_close_time = Column(DateTime(timezone=True), nullable=False)

    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    buyer = relationship("User", back_populates="rfqs", lazy="selectin")
    auction_config = relationship("AuctionConfiguration", back_populates="rfq", uselist=False, cascade="all, delete-orphan", lazy="selectin")
    bids = relationship("Bid", back_populates="rfq", cascade="all, delete-orphan", order_by="Bid.created_at.desc()", lazy="selectin")
    activity_logs = relationship("ActivityLog", back_populates="rfq", cascade="all, delete-orphan", order_by="ActivityLog.created_at.desc()", lazy="selectin")
