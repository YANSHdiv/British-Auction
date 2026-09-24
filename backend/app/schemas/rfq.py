from datetime import datetime
from decimal import Decimal
from typing import Optional, List
from uuid import UUID
from pydantic import BaseModel, Field, model_validator, ConfigDict
from app.models.rfq import RFQStatus
from app.schemas.auction import AuctionConfigCreate, AuctionConfigResponse


class RFQBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=255)
    reference_id: str = Field(..., min_length=2, max_length=100)
    pickup_service_date: datetime
    bid_start_time: datetime
    bid_close_time: datetime
    forced_bid_close_time: datetime


class RFQCreate(RFQBase):
    auction_config: Optional[AuctionConfigCreate] = None

    @model_validator(mode="after")
    def validate_dates(self) -> "RFQCreate":
        if self.bid_close_time <= self.bid_start_time:
            raise ValueError("Bid Close Time must be strictly later than Bid Start Time.")
        if self.forced_bid_close_time <= self.bid_close_time:
            raise ValueError("Forced Bid Close Time must be strictly later than Bid Close Time.")
        return self


class RFQUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=255)
    pickup_service_date: Optional[datetime] = None
    status: Optional[RFQStatus] = None


class RFQResponse(RFQBase):
    id: UUID
    status: RFQStatus
    buyer_id: UUID
    effective_status: RFQStatus
    current_close_time: datetime
    lowest_bid_amount: Optional[Decimal] = None
    bid_count: int = 0
    supplier_count: int = 0
    auction_config: Optional[AuctionConfigResponse] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class RFQListResponse(BaseModel):
    items: List[RFQResponse]
    total: int
