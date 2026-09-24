from datetime import datetime
from typing import Optional, Any, Dict
from uuid import UUID
from pydantic import BaseModel, ConfigDict
from app.models.activity import ActivityEventType


class ActivityLogResponse(BaseModel):
    id: UUID
    rfq_id: UUID
    event_type: ActivityEventType
    supplier_id: Optional[UUID] = None
    supplier_name: Optional[str] = None
    bid_id: Optional[UUID] = None
    old_close_time: Optional[datetime] = None
    new_close_time: Optional[datetime] = None
    extension_reason: Optional[str] = None
    metadata_json: Optional[Dict[str, Any]] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
