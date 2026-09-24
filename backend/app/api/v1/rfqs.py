from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.models.user import User
from app.schemas.rfq import RFQCreate, RFQResponse
from app.services.rfq_service import RFQService
from app.services.auction_service import AuctionService
from app.api.deps import get_current_user, get_current_buyer

router = APIRouter(prefix="/rfqs", tags=["RFQs"])


@router.post("", response_model=RFQResponse, status_code=status.HTTP_201_CREATED)
async def create_rfq(
    rfq_in: RFQCreate,
    current_buyer: User = Depends(get_current_buyer),
    db: AsyncSession = Depends(get_db)
):
    try:
        rfq = await RFQService.create_rfq(db, current_buyer, rfq_in)
        # Fetch enriched RFQ response
        lowest_bid, bid_count, supplier_count = await AuctionService.get_auction_stats(db, rfq.id)
        current_close = rfq.auction_config.current_close_time if rfq.auction_config else rfq.bid_close_time
        effective_status = AuctionService.get_effective_status(rfq, current_close)

        return RFQResponse(
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
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("", response_model=List[RFQResponse])
async def list_rfqs(
    status: Optional[str] = Query(None, description="Filter by status: ACTIVE, CLOSED, FORCE_CLOSED, SCHEDULED, DRAFT, ALL"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    return await RFQService.list_rfqs(db, status_filter=status)


@router.get("/{rfq_id}", response_model=RFQResponse)
async def get_rfq(
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

    current_close = rfq.auction_config.current_close_time if rfq.auction_config else rfq.bid_close_time
    effective_status = AuctionService.get_effective_status(rfq, current_close)
    lowest_bid, bid_count, supplier_count = await AuctionService.get_auction_stats(db, rfq.id)

    return RFQResponse(
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
