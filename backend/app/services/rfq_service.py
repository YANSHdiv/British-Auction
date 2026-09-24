from datetime import datetime, timezone
from typing import List, Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.models.rfq import RFQ, RFQStatus
from app.models.auction import AuctionConfiguration, ExtensionTriggerType
from app.models.activity import ActivityLog, ActivityEventType
from app.models.user import User
from app.schemas.rfq import RFQCreate, RFQResponse
from app.services.auction_service import AuctionService


class RFQService:
    @staticmethod
    async def create_rfq(db: AsyncSession, buyer: User, rfq_in: RFQCreate) -> RFQ:
        # Check reference_id uniqueness
        existing = await db.execute(select(RFQ).where(RFQ.reference_id == rfq_in.reference_id.strip()))
        if existing.scalars().first():
            raise ValueError(f"RFQ Reference ID '{rfq_in.reference_id}' already exists.")

        # Ensure UTC timezone
        start_time = rfq_in.bid_start_time if rfq_in.bid_start_time.tzinfo else rfq_in.bid_start_time.replace(tzinfo=timezone.utc)
        close_time = rfq_in.bid_close_time if rfq_in.bid_close_time.tzinfo else rfq_in.bid_close_time.replace(tzinfo=timezone.utc)
        forced_close = rfq_in.forced_bid_close_time if rfq_in.forced_bid_close_time.tzinfo else rfq_in.forced_bid_close_time.replace(tzinfo=timezone.utc)
        pickup_date = rfq_in.pickup_service_date if rfq_in.pickup_service_date.tzinfo else rfq_in.pickup_service_date.replace(tzinfo=timezone.utc)

        # Initial status
        now = datetime.now(timezone.utc)
        initial_status = RFQStatus.SCHEDULED if now < start_time else RFQStatus.ACTIVE

        rfq = RFQ(
            name=rfq_in.name.strip(),
            reference_id=rfq_in.reference_id.strip(),
            pickup_service_date=pickup_date,
            status=initial_status,
            buyer_id=buyer.id,
            bid_start_time=start_time,
            bid_close_time=close_time,
            forced_bid_close_time=forced_close,
        )
        db.add(rfq)
        await db.flush()  # populate rfq.id

        # Create AuctionConfiguration
        cfg = rfq_in.auction_config
        auction_config = AuctionConfiguration(
            rfq_id=rfq.id,
            british_auction_enabled=cfg.british_auction_enabled if cfg else True,
            trigger_window_minutes=cfg.trigger_window_minutes if cfg else 10,
            extension_duration_minutes=cfg.extension_duration_minutes if cfg else 5,
            extension_trigger_type=cfg.extension_trigger_type if cfg else ExtensionTriggerType.BID_RECEIVED,
            current_close_time=close_time,
            extension_count=0,
        )
        db.add(auction_config)

        # Log Activity
        activity = ActivityLog(
            rfq_id=rfq.id,
            event_type=ActivityEventType.RFQ_CREATED,
            metadata_json={
                "buyer_name": buyer.full_name,
                "company_name": buyer.company_name,
                "trigger_window_minutes": auction_config.trigger_window_minutes,
                "extension_duration_minutes": auction_config.extension_duration_minutes,
                "trigger_type": auction_config.extension_trigger_type.value,
            }
        )
        db.add(activity)

        await db.commit()
        await db.refresh(rfq, ["auction_config", "buyer"])
        return rfq

    @staticmethod
    async def get_rfq_by_id(db: AsyncSession, rfq_id: UUID) -> Optional[RFQ]:
        stmt = (
            select(RFQ)
            .options(
                selectinload(RFQ.auction_config),
                selectinload(RFQ.buyer),
            )
            .where(RFQ.id == rfq_id)
        )
        result = await db.execute(stmt)
        return result.scalars().first()

    @staticmethod
    async def list_rfqs(db: AsyncSession, status_filter: Optional[str] = None) -> List[RFQResponse]:
        stmt = (
            select(RFQ)
            .options(
                selectinload(RFQ.auction_config),
                selectinload(RFQ.buyer),
            )
            .order_by(RFQ.created_at.desc())
        )
        result = await db.execute(stmt)
        rfqs = result.scalars().all()

        responses: List[RFQResponse] = []
        for rfq in rfqs:
            current_close = rfq.auction_config.current_close_time if rfq.auction_config else rfq.bid_close_time
            effective_status = AuctionService.get_effective_status(rfq, current_close)

            # Apply status filter if supplied
            if status_filter and status_filter.upper() != "ALL":
                if effective_status.value != status_filter.upper():
                    continue

            lowest_bid, bid_count, supplier_count = await AuctionService.get_auction_stats(db, rfq.id)

            res = RFQResponse(
                id=rfq.id,
                name=rfq.name,
                reference_id=rfq.reference_id,
                pickup_service_date=rfq.pickup_service_date,
                status=rfq.status,
                buyer_id=rfq.buyer_id,
                bid_start_time=rfq.bid_start_time,
                bid_close_time=rfq.bid_close_time,
                forced_bid_close_time=rfq.forced_bid_close_time,
                effective_status=effective_status,
                current_close_time=current_close,
                lowest_bid_amount=lowest_bid,
                bid_count=bid_count,
                supplier_count=supplier_count,
                auction_config=rfq.auction_config,
                created_at=rfq.created_at,
                updated_at=rfq.updated_at,
            )
            responses.append(res)

        return responses
