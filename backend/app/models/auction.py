import enum
import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, Boolean, DateTime, ForeignKey, Enum as SAEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.core.database import Base


class ExtensionTriggerType(str, enum.Enum):
    BID_RECEIVED = "BID_RECEIVED"
    ANY_RANK_CHANGE = "ANY_RANK_CHANGE"
    L1_RANK_CHANGE = "L1_RANK_CHANGE"


class AuctionConfiguration(Base):
    __tablename__ = "auction_configurations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    rfq_id = Column(UUID(as_uuid=True), ForeignKey("rfqs.id", ondelete="CASCADE"), unique=True, nullable=False, index=True)

    british_auction_enabled = Column(Boolean, default=True, nullable=False)
    trigger_window_minutes = Column(Integer, default=10, nullable=False)  # X
    extension_duration_minutes = Column(Integer, default=5, nullable=False)  # Y
    extension_trigger_type = Column(
        SAEnum(ExtensionTriggerType, name="extension_trigger_type", native_enum=False),
        default=ExtensionTriggerType.BID_RECEIVED,
        nullable=False
    )

    current_close_time = Column(DateTime(timezone=True), nullable=False)
    extension_count = Column(Integer, default=0, nullable=False)

    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    rfq = relationship("RFQ", back_populates="auction_config")
