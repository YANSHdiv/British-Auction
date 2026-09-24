from datetime import datetime, timezone
from decimal import Decimal
from typing import Optional, Tuple
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from app.models.rfq import RFQ, RFQStatus
from app.models.auction import AuctionConfiguration
from app.models.bid import Bid


class AuctionService:
    @staticmethod
    def get_effective_status(rfq: RFQ, current_close_time: datetime, now: Optional[datetime] = None) -> RFQStatus:
        """
        Determines the authoritative status of an auction at the given timestamp (or server current UTC).
        """
        if rfq.status == RFQStatus.DRAFT:
            return RFQStatus.DRAFT

        if now is None:
            now = datetime.now(timezone.utc)
        elif now.tzinfo is None:
            now = now.replace(tzinfo=timezone.utc)

        start_time = rfq.bid_start_time
        if start_time.tzinfo is None:
            start_time = start_time.replace(tzinfo=timezone.utc)

        forced_close = rfq.forced_bid_close_time
        if forced_close.tzinfo is None:
            forced_close = forced_close.replace(tzinfo=timezone.utc)

        if current_close_time.tzinfo is None:
            current_close_time = current_close_time.replace(tzinfo=timezone.utc)

        if now < start_time:
            return RFQStatus.SCHEDULED
        elif now >= forced_close:
            return RFQStatus.FORCE_CLOSED
        elif now >= current_close_time:
            return RFQStatus.CLOSED
        else:
            return RFQStatus.ACTIVE

    @staticmethod
    async def get_auction_stats(db: AsyncSession, rfq_id: UUID) -> Tuple[Optional[Decimal], int, int]:
        """
        Returns (lowest_bid_amount, total_bids_count, unique_suppliers_count).
        """
        stats_stmt = (
            select(
                func.min(Bid.total_amount).label("min_amount"),
                func.count(Bid.id).label("bid_count"),
                func.count(func.distinct(Bid.supplier_id)).label("supplier_count")
            )
            .where(Bid.rfq_id == rfq_id)
        )
        result = await db.execute(stats_stmt)
        row = result.first()
        if row:
            return row.min_amount, row.bid_count or 0, row.supplier_count or 0
        return None, 0, 0
