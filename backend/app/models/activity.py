import enum
import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, ForeignKey, Text, JSON, Enum as SAEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.core.database import Base


class ActivityEventType(str, enum.Enum):
    RFQ_CREATED = "RFQ_CREATED"
    BID_SUBMITTED = "BID_SUBMITTED"
    AUCTION_EXTENDED = "AUCTION_EXTENDED"
    AUCTION_CLOSED = "AUCTION_CLOSED"
    AUCTION_FORCE_CLOSED = "AUCTION_FORCE_CLOSED"


class ActivityLog(Base):
    __tablename__ = "activity_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    rfq_id = Column(UUID(as_uuid=True), ForeignKey("rfqs.id", ondelete="CASCADE"), nullable=False, index=True)

    event_type = Column(SAEnum(ActivityEventType, name="activity_event_type", native_enum=False), nullable=False, index=True)

    supplier_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    bid_id = Column(UUID(as_uuid=True), ForeignKey("bids.id", ondelete="SET NULL"), nullable=True)

    old_close_time = Column(DateTime(timezone=True), nullable=True)
    new_close_time = Column(DateTime(timezone=True), nullable=True)
    extension_reason = Column(Text, nullable=True)
    metadata_json = Column(JSON, nullable=True)

    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False, index=True)

    # Relationships
    rfq = relationship("RFQ", back_populates="activity_logs", lazy="selectin")
    supplier = relationship("User", lazy="selectin")
    bid = relationship("Bid", back_populates="activity_logs", lazy="selectin")
