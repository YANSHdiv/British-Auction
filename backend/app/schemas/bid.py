from datetime import datetime
from decimal import Decimal
from typing import Optional, List
from uuid import UUID
from pydantic import BaseModel, Field, model_validator, ConfigDict
from app.schemas.user import UserResponse


class BidBase(BaseModel):
    carrier_name: str = Field(..., min_length=1, max_length=255)
    freight_charges: Decimal = Field(..., ge=0)
    origin_charges: Decimal = Field(..., ge=0)
    destination_charges: Decimal = Field(..., ge=0)
    transit_time_days: int = Field(..., gt=0)
    validity_date: datetime


class BidCreate(BidBase):
    pass


class BidResponse(BidBase):
    id: UUID
    rfq_id: UUID
    supplier_id: UUID
    total_amount: Decimal
    created_at: datetime
    rank_label: Optional[str] = None
    supplier: Optional[UserResponse] = None

    model_config = ConfigDict(from_attributes=True)


class SupplierRankingItem(BaseModel):
    rank: int
    rank_label: str  # L1, L2, L3...
    supplier_id: UUID
    supplier_name: str
    company_name: str
    best_bid_id: UUID
    total_amount: Decimal
    freight_charges: Decimal
    origin_charges: Decimal
    destination_charges: Decimal
    transit_time_days: int
    validity_date: datetime
    submitted_at: datetime
    bid_count: int


class AuctionRankingResponse(BaseModel):
    rfq_id: UUID
    rankings: List[SupplierRankingItem]
    lowest_bid_amount: Optional[Decimal] = None
    l1_supplier_id: Optional[UUID] = None
