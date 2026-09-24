from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field, ConfigDict
from app.models.auction import ExtensionTriggerType


class AuctionConfigBase(BaseModel):
    british_auction_enabled: bool = True
    trigger_window_minutes: int = Field(default=10, ge=0, description="Trigger window X in minutes")
    extension_duration_minutes: int = Field(default=5, gt=0, description="Extension duration Y in minutes")
    extension_trigger_type: ExtensionTriggerType = ExtensionTriggerType.BID_RECEIVED


class AuctionConfigCreate(AuctionConfigBase):
    pass


class AuctionConfigUpdate(BaseModel):
    british_auction_enabled: bool | None = None
    trigger_window_minutes: int | None = Field(default=None, ge=0)
    extension_duration_minutes: int | None = Field(default=None, gt=0)
    extension_trigger_type: ExtensionTriggerType | None = None


class AuctionConfigResponse(AuctionConfigBase):
    id: UUID
    rfq_id: UUID
    current_close_time: datetime
    extension_count: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
