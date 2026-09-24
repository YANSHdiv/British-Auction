from datetime import datetime, timezone
from decimal import Decimal
from typing import List, Tuple, Optional, Dict
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.models.bid import Bid
from app.models.user import User
from app.schemas.bid import SupplierRankingItem


class RankingService:
    @staticmethod
    async def get_current_rankings(db: AsyncSession, rfq_id: UUID) -> List[SupplierRankingItem]:
        """
        Calculates supplier rankings for an RFQ.
        Each participating supplier is ranked based on their best (lowest) valid bid.
        Ties are broken deterministically by earliest submission timestamp (created_at ASC).
        """
        # Fetch all bids for this RFQ with supplier details loaded
        stmt = (
            select(Bid)
            .options(selectinload(Bid.supplier))
            .where(Bid.rfq_id == rfq_id)
            .order_by(Bid.created_at.asc())
        )
        result = await db.execute(stmt)
        bids = result.scalars().all()

        if not bids:
            return []

        # Find best (lowest) bid per supplier
        supplier_best_bids: Dict[UUID, Bid] = {}
        supplier_bid_counts: Dict[UUID, int] = {}

        def normalize_dt(dt: datetime) -> datetime:
            if dt.tzinfo is None:
                return dt.replace(tzinfo=timezone.utc)
            return dt

        for bid in bids:
            supplier_id = bid.supplier_id
            supplier_bid_counts[supplier_id] = supplier_bid_counts.get(supplier_id, 0) + 1

            if supplier_id not in supplier_best_bids:
                supplier_best_bids[supplier_id] = bid
            else:
                current_best = supplier_best_bids[supplier_id]
                # Lower amount wins; if equal, earlier created_at wins
                if (bid.total_amount < current_best.total_amount) or (
                    bid.total_amount == current_best.total_amount and normalize_dt(bid.created_at) < normalize_dt(current_best.created_at)
                ):
                    supplier_best_bids[supplier_id] = bid

        # Sort suppliers: total_amount ASC, then created_at ASC
        sorted_best_bids = sorted(
            supplier_best_bids.values(),
            key=lambda b: (b.total_amount, normalize_dt(b.created_at))
        )

        rankings: List[SupplierRankingItem] = []
        for index, bid in enumerate(sorted_best_bids, start=1):
            supplier: User = bid.supplier
            rankings.append(
                SupplierRankingItem(
                    rank=index,
                    rank_label=f"L{index}",
                    supplier_id=bid.supplier_id,
                    supplier_name=supplier.full_name if supplier else "Unknown Supplier",
                    company_name=supplier.company_name if supplier else "Unknown Company",
                    best_bid_id=bid.id,
                    total_amount=bid.total_amount,
                    freight_charges=bid.freight_charges,
                    origin_charges=bid.origin_charges,
                    destination_charges=bid.destination_charges,
                    transit_time_days=bid.transit_time_days,
                    validity_date=bid.validity_date,
                    submitted_at=bid.created_at,
                    bid_count=supplier_bid_counts.get(bid.supplier_id, 1),
                )
            )

        return rankings

    @staticmethod
    def detect_rank_changes(
        old_rankings: List[SupplierRankingItem],
        new_rankings: List[SupplierRankingItem]
    ) -> Tuple[bool, bool, Optional[str], Optional[str]]:
        """
        Compares old and new rankings.
        Returns:
            any_rank_changed (bool)
            l1_changed (bool)
            prev_l1_supplier_name (Optional[str])
            new_l1_supplier_name (Optional[str])
        """
        old_l1_supplier_id = old_rankings[0].supplier_id if old_rankings else None
        old_l1_supplier_name = old_rankings[0].company_name if old_rankings else None

        new_l1_supplier_id = new_rankings[0].supplier_id if new_rankings else None
        new_l1_supplier_name = new_rankings[0].company_name if new_rankings else None

        # L1 changed if:
        # - Previously there was no L1 and now there is, OR
        # - The supplier holding the L1 position changed to a different supplier
        l1_changed = False
        if new_l1_supplier_id is not None:
            if old_l1_supplier_id is None:
                l1_changed = True
            elif old_l1_supplier_id != new_l1_supplier_id:
                l1_changed = True

        # Any rank changed:
        # Check if ranking positions of any supplier changed or if a new supplier was introduced
        old_rank_map = {item.supplier_id: item.rank for item in old_rankings}
        new_rank_map = {item.supplier_id: item.rank for item in new_rankings}

        any_rank_changed = False
        if len(old_rank_map) != len(new_rank_map):
            any_rank_changed = True
        else:
            for s_id, new_rank in new_rank_map.items():
                if s_id not in old_rank_map or old_rank_map[s_id] != new_rank:
                    any_rank_changed = True
                    break

        return any_rank_changed, l1_changed, old_l1_supplier_name, new_l1_supplier_name
