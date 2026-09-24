from uuid import UUID
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.models.user import User
from app.schemas.bid import BidCreate, BidResponse
from app.services.bid_service import BidService
from app.api.deps import get_current_supplier

router = APIRouter(prefix="/auctions", tags=["Bidding"])


@router.post("/{rfq_id}/bids", response_model=BidResponse, status_code=status.HTTP_201_CREATED)
async def submit_bid(
    rfq_id: UUID,
    bid_in: BidCreate,
    current_supplier: User = Depends(get_current_supplier),
    db: AsyncSession = Depends(get_db)
):
    """
    Submits a new bid for the specified RFQ.
    Transactions and pessimistic locks ensure race-free execution,
    British Auction price rule enforcement, ranking recalculation,
    and automatic time extension evaluation.
    """
    return await BidService.place_bid(
        db=db,
        rfq_id=rfq_id,
        supplier=current_supplier,
        bid_in=bid_in
    )
