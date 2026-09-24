from datetime import datetime, timedelta, timezone
from typing import Tuple, Optional
from decimal import Decimal
from app.models.auction import AuctionConfiguration, ExtensionTriggerType
from app.models.rfq import RFQ
from app.models.user import User


class ExtensionEngine:
    @staticmethod
    def evaluate_extension(
        rfq: RFQ,
        auction_config: AuctionConfiguration,
        bid_timestamp: datetime,
        bid_amount: Decimal,
        supplier: User,
        any_rank_changed: bool,
        l1_changed: bool,
        old_l1_name: Optional[str],
        new_l1_name: Optional[str],
    ) -> Tuple[bool, Optional[datetime], Optional[str]]:
        """
        Evaluates whether an incoming bid triggers an auction extension.
        Returns:
            should_extend (bool)
            new_close_time (Optional[datetime])
            extension_reason (Optional[str])
        """
        if not auction_config.british_auction_enabled:
            return False, None, None

        current_close = auction_config.current_close_time
        forced_close = rfq.forced_bid_close_time
        x_minutes = auction_config.trigger_window_minutes
        y_minutes = auction_config.extension_duration_minutes
        trigger_type = auction_config.extension_trigger_type

        # If already at or past forced close, no extension is possible
        if current_close >= forced_close:
            return False, None, None

        # Calculate trigger window: [current_close - X minutes, current_close]
        trigger_window_start = current_close - timedelta(minutes=x_minutes)

        # Ensure timezone compatibility
        if bid_timestamp.tzinfo is None:
            bid_timestamp = bid_timestamp.replace(tzinfo=timezone.utc)
        if current_close.tzinfo is None:
            current_close = current_close.replace(tzinfo=timezone.utc)
        if trigger_window_start.tzinfo is None:
            trigger_window_start = trigger_window_start.replace(tzinfo=timezone.utc)
        if forced_close.tzinfo is None:
            forced_close = forced_close.replace(tzinfo=timezone.utc)

        # Check if the bid timestamp falls within the trigger window
        if bid_timestamp < trigger_window_start or bid_timestamp > current_close:
            return False, None, None

        # Check if condition is met based on trigger type
        condition_met = False
        reason_detail = ""

        if trigger_type == ExtensionTriggerType.BID_RECEIVED:
            condition_met = True
            reason_detail = f"Bid of ${bid_amount:,.2f} received from {supplier.company_name or supplier.full_name} during the last {x_minutes}-minute trigger window."

        elif trigger_type == ExtensionTriggerType.ANY_RANK_CHANGE:
            if any_rank_changed:
                condition_met = True
                reason_detail = f"Supplier ranking changed in the last {x_minutes}-minute trigger window due to bid from {supplier.company_name or supplier.full_name}."

        elif trigger_type == ExtensionTriggerType.L1_RANK_CHANGE:
            if l1_changed:
                condition_met = True
                prev_text = old_l1_name if old_l1_name else "None"
                curr_text = new_l1_name if new_l1_name else "None"
                reason_detail = f"Lowest bidder (L1) changed from {prev_text} to {curr_text} during the last {x_minutes}-minute trigger window."

        if not condition_met:
            return False, None, None

        # Calculate new close time: min(current_close + Y minutes, forced_close)
        candidate_close = current_close + timedelta(minutes=y_minutes)
        new_close = min(candidate_close, forced_close)

        # If new_close does not push the close time forward, do not extend
        if new_close <= current_close:
            return False, None, None

        # Build comprehensive reason string
        actual_extension_minutes = (new_close - current_close).total_seconds() / 60.0
        capped_note = ""
        if candidate_close > forced_close:
            capped_note = f" (Extension capped at Forced Bid Close Time, added {actual_extension_minutes:.1f} min instead of {y_minutes} min)"

        extension_reason = (
            f"Auction extended from {current_close.strftime('%Y-%m-%d %H:%M:%S UTC')} to "
            f"{new_close.strftime('%Y-%m-%d %H:%M:%S UTC')} ({actual_extension_minutes:.0f}m added). "
            f"Reason: {reason_detail}{capped_note}"
        )

        return True, new_close, extension_reason
