from datetime import datetime, timezone
from decimal import Decimal
from typing import List, Optional
from uuid import UUID
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from app.models.rfq import RFQ, RFQStatus
from app.models.auction import AuctionConfiguration
from app.models.bid import Bid
from app.models.activity import ActivityLog, ActivityEventType
from app.models.user import User
from app.schemas.bid import BidCreate, BidResponse, SupplierRankingItem
from app.services.auction_service import AuctionService
from app.services.ranking_service import RankingService
from app.services.extension_engine import ExtensionEngine


class BidService:
    @staticmethod
    async def place_bid(
        db: AsyncSession,
        rfq_id: UUID,
        supplier: User,
        bid_in: BidCreate,
        simulated_now: Optional[datetime] = None
    ) -> BidResponse:
        """
        Transactional bid submission with pessimistic locking (FOR UPDATE)
        to prevent race conditions, accurately rank bids, and trigger extensions.
        """
        now = simulated_now or datetime.now(timezone.utc)
        if now.tzinfo is None:
            now = now.replace(tzinfo=timezone.utc)

        # 1. Pessimistic lock on RFQ and its AuctionConfiguration
        # In SQLite (during tests), FOR UPDATE is ignored by dialect or supported gracefully,
        # but in PostgreSQL it locks the specific row.
        rfq_query = (
            select(RFQ)
            .options(selectinload(RFQ.auction_config))
            .where(RFQ.id == rfq_id)
            .with_for_update()
        )
        result = await db.execute(rfq_query)
        rfq = result.scalars().first()

        if not rfq:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"RFQ with ID {rfq_id} was not found."
            )

        auction_config = rfq.auction_config
        if not auction_config:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Auction configuration is missing for this RFQ."
            )

        # 2. Authoritative auction state check
        effective_status = AuctionService.get_effective_status(rfq, auction_config.current_close_time, now)

        if effective_status == RFQStatus.SCHEDULED:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Auction has not started yet. Bidding is not allowed."
            )
        elif effective_status == RFQStatus.FORCE_CLOSED:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Auction has reached its Forced Bid Close Time and is permanently closed."
            )
        elif effective_status == RFQStatus.CLOSED:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Auction is closed. Bidding time has expired."
            )
        elif effective_status != RFQStatus.ACTIVE:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Bidding is not allowed for an auction in {effective_status.value} status."
            )

        # Double check exact timestamps
        current_close = auction_config.current_close_time
        if current_close.tzinfo is None:
            current_close = current_close.replace(tzinfo=timezone.utc)

        forced_close = rfq.forced_bid_close_time
        if forced_close.tzinfo is None:
            forced_close = forced_close.replace(tzinfo=timezone.utc)

        if now >= current_close:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Bid rejected: Current bid close time has passed."
            )
        if now >= forced_close:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Bid rejected: Forced bid close time has been reached."
            )

        # 3. Financial validation: total amount calculation & non-negativity
        total_calculated = (
            Decimal(str(bid_in.freight_charges)) +
            Decimal(str(bid_in.origin_charges)) +
            Decimal(str(bid_in.destination_charges))
        )

        if total_calculated <= Decimal("0"):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Total bid amount must be strictly greater than 0."
            )

        # 4. British Auction Rule: Supplier's new bid must be strictly lower than their own prior best valid bid
        supplier_prior_bids = await db.execute(
            select(Bid)
            .where(Bid.rfq_id == rfq_id, Bid.supplier_id == supplier.id)
            .order_by(Bid.total_amount.asc())
        )
        best_prior_bid = supplier_prior_bids.scalars().first()

        if best_prior_bid is not None:
            if total_calculated >= best_prior_bid.total_amount:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=(
                        f"British Auction Rule: New bid (${total_calculated:,.2f}) must be strictly lower than "
                        f"your previous best bid (${best_prior_bid.total_amount:,.2f})."
                    )
                )

        # 5. Snapshot rankings BEFORE new bid
        old_rankings = await RankingService.get_current_rankings(db, rfq_id)

        # 6. Insert new Bid record
        validity = bid_in.validity_date
        if validity.tzinfo is None:
            validity = validity.replace(tzinfo=timezone.utc)

        new_bid = Bid(
            rfq_id=rfq_id,
            supplier_id=supplier.id,
            carrier_name=bid_in.carrier_name.strip(),
            freight_charges=Decimal(str(bid_in.freight_charges)),
            origin_charges=Decimal(str(bid_in.origin_charges)),
            destination_charges=Decimal(str(bid_in.destination_charges)),
            total_amount=total_calculated,
            transit_time_days=bid_in.transit_time_days,
            validity_date=validity,
            created_at=now,
        )
        db.add(new_bid)
        await db.flush()  # assign new_bid.id

        # 7. Snapshot rankings AFTER new bid
        new_rankings = await RankingService.get_current_rankings(db, rfq_id)

        # Determine supplier's new rank
        supplier_new_rank = next((item for item in new_rankings if item.supplier_id == supplier.id), None)
        rank_label = supplier_new_rank.rank_label if supplier_new_rank else None

        # 8. Check rank changes
        any_rank_changed, l1_changed, old_l1_name, new_l1_name = RankingService.detect_rank_changes(
            old_rankings, new_rankings
        )

        # 9. Evaluate auction extension
        should_extend, new_close_time, extension_reason = ExtensionEngine.evaluate_extension(
            rfq=rfq,
            auction_config=auction_config,
            bid_timestamp=now,
            bid_amount=total_calculated,
            supplier=supplier,
            any_rank_changed=any_rank_changed,
            l1_changed=l1_changed,
            old_l1_name=old_l1_name,
            new_l1_name=new_l1_name,
        )

        old_close_time_val = auction_config.current_close_time

        if should_extend and new_close_time:
            auction_config.current_close_time = new_close_time
            auction_config.extension_count += 1

            # Log extension event
            ext_log = ActivityLog(
                rfq_id=rfq_id,
                event_type=ActivityEventType.AUCTION_EXTENDED,
                supplier_id=supplier.id,
                bid_id=new_bid.id,
                old_close_time=old_close_time_val,
                new_close_time=new_close_time,
                extension_reason=extension_reason,
                metadata_json={
                    "trigger_type": auction_config.extension_trigger_type.value,
                    "extension_duration_minutes": auction_config.extension_duration_minutes,
                    "trigger_window_minutes": auction_config.trigger_window_minutes,
                    "bid_amount": str(total_calculated),
                    "supplier_company": supplier.company_name,
                }
            )
            db.add(ext_log)

        # 10. Log bid submission event
        bid_log = ActivityLog(
            rfq_id=rfq_id,
            event_type=ActivityEventType.BID_SUBMITTED,
            supplier_id=supplier.id,
            bid_id=new_bid.id,
            metadata_json={
                "total_amount": str(total_calculated),
                "freight_charges": str(bid_in.freight_charges),
                "origin_charges": str(bid_in.origin_charges),
                "destination_charges": str(bid_in.destination_charges),
                "carrier_name": bid_in.carrier_name.strip(),
                "rank_label": rank_label,
                "extended": should_extend,
            }
        )
        db.add(bid_log)

        # 11. Commit transaction atomically
        await db.commit()
        await db.refresh(new_bid)

        # Load supplier relationship for response
        res_bid = await db.execute(
            select(Bid)
            .options(selectinload(Bid.supplier))
            .where(Bid.id == new_bid.id)
        )
        loaded_bid = res_bid.scalars().first()

        return BidResponse(
            id=loaded_bid.id,
            rfq_id=loaded_bid.rfq_id,
            supplier_id=loaded_bid.supplier_id,
            carrier_name=loaded_bid.carrier_name,
            freight_charges=loaded_bid.freight_charges,
            origin_charges=loaded_bid.origin_charges,
            destination_charges=loaded_bid.destination_charges,
            total_amount=loaded_bid.total_amount,
            transit_time_days=loaded_bid.transit_time_days,
            validity_date=loaded_bid.validity_date,
            created_at=loaded_bid.created_at,
            rank_label=rank_label,
            supplier=loaded_bid.supplier,
        )

    @staticmethod
    async def get_rfq_bids(db: AsyncSession, rfq_id: UUID) -> List[BidResponse]:
        """
        Retrieves all bids for an RFQ, sorted by total_amount ASC, created_at ASC.
        """
        stmt = (
            select(Bid)
            .options(selectinload(Bid.supplier))
            .where(Bid.rfq_id == rfq_id)
            .order_by(Bid.total_amount.asc(), Bid.created_at.asc())
        )
        result = await db.execute(stmt)
        bids = result.scalars().all()

        rankings = await RankingService.get_current_rankings(db, rfq_id)
        supplier_rank_map = {item.supplier_id: item.rank_label for item in rankings}

        responses: List[BidResponse] = []
        for b in bids:
            responses.append(
                BidResponse(
                    id=b.id,
                    rfq_id=b.rfq_id,
                    supplier_id=b.supplier_id,
                    carrier_name=b.carrier_name,
                    freight_charges=b.freight_charges,
                    origin_charges=b.origin_charges,
                    destination_charges=b.destination_charges,
                    total_amount=b.total_amount,
                    transit_time_days=b.transit_time_days,
                    validity_date=b.validity_date,
                    created_at=b.created_at,
                    rank_label=supplier_rank_map.get(b.supplier_id),
                    supplier=b.supplier,
                )
            )
        return responses
