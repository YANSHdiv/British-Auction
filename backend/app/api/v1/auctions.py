from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.core.database import get_db
from app.models.activity import ActivityLog
from app.models.bid import Bid
from app.models.user import User
from app.schemas.bid import BidResponse, AuctionRankingResponse, SupplierRankingItem
from app.schemas.activity import ActivityLogResponse
from app.services.rfq_service import RFQService
from app.services.auction_service import AuctionService
from app.services.ranking_service import RankingService
from app.services.bid_service import BidService
from app.api.deps import get_current_user

router = APIRouter(prefix="/auctions", tags=["Auctions"])


@router.get("/{rfq_id}/bids", response_model=List[BidResponse])
async def get_auction_bids(
    rfq_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    rfq = await RFQService.get_rfq_by_id(db, rfq_id)
    if not rfq:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"RFQ with ID {rfq_id} was not found."
        )
    return await BidService.get_rfq_bids(db, rfq_id)


@router.get("/{rfq_id}/ranking", response_model=AuctionRankingResponse)
async def get_auction_rankings(
    rfq_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    rfq = await RFQService.get_rfq_by_id(db, rfq_id)
    if not rfq:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"RFQ with ID {rfq_id} was not found."
        )

    rankings = await RankingService.get_current_rankings(db, rfq_id)
    lowest_amount = rankings[0].total_amount if rankings else None
    l1_id = rankings[0].supplier_id if rankings else None

    return AuctionRankingResponse(
        rfq_id=rfq_id,
        rankings=rankings,
        lowest_bid_amount=lowest_amount,
        l1_supplier_id=l1_id,
    )


@router.get("/{rfq_id}/activity", response_model=List[ActivityLogResponse])
async def get_auction_activity(
    rfq_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    rfq = await RFQService.get_rfq_by_id(db, rfq_id)
    if not rfq:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"RFQ with ID {rfq_id} was not found."
        )

    stmt = (
        select(ActivityLog)
        .options(selectinload(ActivityLog.supplier))
        .where(ActivityLog.rfq_id == rfq_id)
        .order_by(ActivityLog.created_at.desc())
    )
    result = await db.execute(stmt)
    logs = result.scalars().all()

    responses: List[ActivityLogResponse] = []
    for log in logs:
        supplier_name = None
        if log.supplier:
            supplier_name = log.supplier.company_name or log.supplier.full_name

        responses.append(
            ActivityLogResponse(
                id=log.id,
                rfq_id=log.rfq_id,
                event_type=log.event_type,
                supplier_id=log.supplier_id,
                supplier_name=supplier_name,
                bid_id=log.bid_id,
                old_close_time=log.old_close_time,
                new_close_time=log.new_close_time,
                extension_reason=log.extension_reason,
                metadata_json=log.metadata_json,
                created_at=log.created_at,
            )
        )
    return responses


@router.get("/{rfq_id}/my-bid", response_model=Optional[SupplierRankingItem])
async def get_my_current_bid(
    rfq_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    rankings = await RankingService.get_current_rankings(db, rfq_id)
    for rank_item in rankings:
        if rank_item.supplier_id == current_user.id:
            return rank_item
    return None
