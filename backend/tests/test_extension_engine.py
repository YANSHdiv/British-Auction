from datetime import datetime, timedelta, timezone
from decimal import Decimal
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User
from app.schemas.bid import BidCreate
from app.services.bid_service import BidService
from tests.conftest import get_auth_headers


@pytest.mark.asyncio
async def test_extension_trigger_bid_received(
    client: AsyncClient,
    db_session: AsyncSession,
    buyer_user: User,
    supplier1: User
):
    now = datetime.now(timezone.utc)
    # Bid close is 8 minutes away; Trigger window X = 10 minutes -> inside window!
    bid_close = now + timedelta(minutes=8)
    forced_close = now + timedelta(minutes=30)

    rfq_payload = {
        "name": "Extension Bid Received RFQ",
        "reference_id": "RFQ-EXT-001",
        "pickup_service_date": (now + timedelta(days=5)).isoformat(),
        "bid_start_time": (now - timedelta(minutes=10)).isoformat(),
        "bid_close_time": bid_close.isoformat(),
        "forced_bid_close_time": forced_close.isoformat(),
        "auction_config": {
            "british_auction_enabled": True,
            "trigger_window_minutes": 10,  # X = 10
            "extension_duration_minutes": 5,  # Y = 5
            "extension_trigger_type": "BID_RECEIVED"
        }
    }
    rfq_res = await client.post("/api/rfqs", json=rfq_payload, headers=get_auth_headers(buyer_user))
    assert rfq_res.status_code == 201
    rfq_id = rfq_res.json()["id"]

    # Submit bid inside trigger window
    bid_payload = {
        "carrier_name": "Swift Logistics",
        "freight_charges": "2000.00",
        "origin_charges": "200.00",
        "destination_charges": "200.00",
        "transit_time_days": 2,
        "validity_date": (now + timedelta(days=10)).isoformat()
    }
    bid_res = await client.post(f"/api/auctions/{rfq_id}/bids", json=bid_payload, headers=get_auth_headers(supplier1))
    assert bid_res.status_code == 201

    # Check that auction was extended by 5 minutes: 8m + 5m = 13m
    rfq_after = await client.get(f"/api/rfqs/{rfq_id}", headers=get_auth_headers(buyer_user))
    assert rfq_after.status_code == 200
    cfg = rfq_after.json()["auction_config"]
    assert cfg["extension_count"] == 1

    # Verify Activity log
    activity_res = await client.get(f"/api/auctions/{rfq_id}/activity", headers=get_auth_headers(buyer_user))
    assert activity_res.status_code == 200
    activities = activity_res.json()
    extended_event = next((a for a in activities if a["event_type"] == "AUCTION_EXTENDED"), None)
    assert extended_event is not None
    assert "Auction extended" in extended_event["extension_reason"]
    assert "trigger window" in extended_event["extension_reason"]


@pytest.mark.asyncio
async def test_no_extension_outside_trigger_window(
    client: AsyncClient,
    buyer_user: User,
    supplier1: User
):
    now = datetime.now(timezone.utc)
    # Bid close is 60 minutes away; Trigger window X = 10 minutes -> OUTSIDE trigger window!
    bid_close = now + timedelta(minutes=60)
    forced_close = now + timedelta(minutes=120)

    rfq_payload = {
        "name": "Outside Window RFQ",
        "reference_id": "RFQ-EXT-002",
        "pickup_service_date": (now + timedelta(days=5)).isoformat(),
        "bid_start_time": (now - timedelta(minutes=10)).isoformat(),
        "bid_close_time": bid_close.isoformat(),
        "forced_bid_close_time": forced_close.isoformat(),
        "auction_config": {
            "british_auction_enabled": True,
            "trigger_window_minutes": 10,
            "extension_duration_minutes": 5,
            "extension_trigger_type": "BID_RECEIVED"
        }
    }
    rfq_res = await client.post("/api/rfqs", json=rfq_payload, headers=get_auth_headers(buyer_user))
    rfq_id = rfq_res.json()["id"]

    bid_payload = {
        "carrier_name": "Swift Logistics",
        "freight_charges": "2000.00",
        "origin_charges": "200.00",
        "destination_charges": "200.00",
        "transit_time_days": 2,
        "validity_date": (now + timedelta(days=10)).isoformat()
    }
    bid_res = await client.post(f"/api/auctions/{rfq_id}/bids", json=bid_payload, headers=get_auth_headers(supplier1))
    assert bid_res.status_code == 201

    # Should NOT have extended
    rfq_after = await client.get(f"/api/rfqs/{rfq_id}", headers=get_auth_headers(buyer_user))
    cfg = rfq_after.json()["auction_config"]
    assert cfg["extension_count"] == 0

    # Activity log should have BID_SUBMITTED but NO AUCTION_EXTENDED
    act_res = await client.get(f"/api/auctions/{rfq_id}/activity", headers=get_auth_headers(buyer_user))
    has_extended = any(a["event_type"] == "AUCTION_EXTENDED" for a in act_res.json())
    assert not has_extended


@pytest.mark.asyncio
async def test_extension_trigger_l1_rank_change(
    client: AsyncClient,
    buyer_user: User,
    supplier1: User,
    supplier2: User
):
    now = datetime.now(timezone.utc)
    bid_close = now + timedelta(minutes=8)
    forced_close = now + timedelta(minutes=30)

    rfq_payload = {
        "name": "L1 Rank Change RFQ",
        "reference_id": "RFQ-EXT-L1",
        "pickup_service_date": (now + timedelta(days=5)).isoformat(),
        "bid_start_time": (now - timedelta(minutes=10)).isoformat(),
        "bid_close_time": bid_close.isoformat(),
        "forced_bid_close_time": forced_close.isoformat(),
        "auction_config": {
            "british_auction_enabled": True,
            "trigger_window_minutes": 20,
            "extension_duration_minutes": 5,
            "extension_trigger_type": "L1_RANK_CHANGE"
        }
    }
    rfq_res = await client.post("/api/rfqs", json=rfq_payload, headers=get_auth_headers(buyer_user))
    rfq_id = rfq_res.json()["id"]

    # 1. Supplier 1 submits first bid -> Establishes L1 -> Extends auction
    bid1 = {
        "carrier_name": "Carrier 1",
        "freight_charges": "3000.00",
        "origin_charges": "200.00",
        "destination_charges": "200.00",
        "transit_time_days": 2,
        "validity_date": (now + timedelta(days=10)).isoformat()
    }
    res1 = await client.post(f"/api/auctions/{rfq_id}/bids", json=bid1, headers=get_auth_headers(supplier1))
    assert res1.status_code == 201

    rfq_1 = await client.get(f"/api/rfqs/{rfq_id}", headers=get_auth_headers(buyer_user))
    assert rfq_1.json()["auction_config"]["extension_count"] == 1

    # 2. Supplier 1 submits an even lower bid ($3,200) -> Still L1! Lowest-priced supplier did NOT change!
    bid1_lower = {
        "carrier_name": "Carrier 1",
        "freight_charges": "2800.00",
        "origin_charges": "200.00",
        "destination_charges": "200.00",
        "transit_time_days": 2,
        "validity_date": (now + timedelta(days=10)).isoformat()
    }
    res1_lower = await client.post(f"/api/auctions/{rfq_id}/bids", json=bid1_lower, headers=get_auth_headers(supplier1))
    assert res1_lower.status_code == 201

    # Extension count must remain 1 because L1 supplier did NOT change
    rfq_1b = await client.get(f"/api/rfqs/{rfq_id}", headers=get_auth_headers(buyer_user))
    assert rfq_1b.json()["auction_config"]["extension_count"] == 1

    # 3. Supplier 2 submits lower bid ($3,000) -> Supplier 2 takes over L1 from Supplier 1 -> Extends!
    bid2 = {
        "carrier_name": "Carrier 2",
        "freight_charges": "2600.00",
        "origin_charges": "200.00",
        "destination_charges": "200.00",
        "transit_time_days": 2,
        "validity_date": (now + timedelta(days=10)).isoformat()
    }
    res2 = await client.post(f"/api/auctions/{rfq_id}/bids", json=bid2, headers=get_auth_headers(supplier2))
    assert res2.status_code == 201

    # Extension count must be 2 now
    rfq_2 = await client.get(f"/api/rfqs/{rfq_id}", headers=get_auth_headers(buyer_user))
    assert rfq_2.json()["auction_config"]["extension_count"] == 2


@pytest.mark.asyncio
async def test_extension_capped_at_forced_close(
    client: AsyncClient,
    buyer_user: User,
    supplier1: User
):
    now = datetime.now(timezone.utc)
    # Only 2 minutes remain between bid close and forced close!
    # But Y = 5 minutes extension duration!
    bid_close = now + timedelta(minutes=4)
    forced_close = now + timedelta(minutes=6)

    rfq_payload = {
        "name": "Capped Extension RFQ",
        "reference_id": "RFQ-EXT-CAP",
        "pickup_service_date": (now + timedelta(days=5)).isoformat(),
        "bid_start_time": (now - timedelta(minutes=10)).isoformat(),
        "bid_close_time": bid_close.isoformat(),
        "forced_bid_close_time": forced_close.isoformat(),
        "auction_config": {
            "british_auction_enabled": True,
            "trigger_window_minutes": 10,
            "extension_duration_minutes": 5,  # Y = 5 > 2 remaining minutes
            "extension_trigger_type": "BID_RECEIVED"
        }
    }
    rfq_res = await client.post("/api/rfqs", json=rfq_payload, headers=get_auth_headers(buyer_user))
    rfq_id = rfq_res.json()["id"]

    bid = {
        "carrier_name": "Carrier",
        "freight_charges": "1000.00",
        "origin_charges": "100.00",
        "destination_charges": "100.00",
        "transit_time_days": 1,
        "validity_date": (now + timedelta(days=10)).isoformat()
    }
    res = await client.post(f"/api/auctions/{rfq_id}/bids", json=bid, headers=get_auth_headers(supplier1))
    assert res.status_code == 201

    # Check that current_close_time is capped EXACTLY at forced_bid_close_time!
    rfq_after = await client.get(f"/api/rfqs/{rfq_id}", headers=get_auth_headers(buyer_user))
    data = rfq_after.json()
    new_close = data["current_close_time"]
    forced = data["forced_bid_close_time"]
    assert new_close == forced

    # Check reason notes capping
    act_res = await client.get(f"/api/auctions/{rfq_id}/activity", headers=get_auth_headers(buyer_user))
    extended_event = next(a for a in act_res.json() if a["event_type"] == "AUCTION_EXTENDED")
    assert "Extension capped at Forced Bid Close Time" in extended_event["extension_reason"]


@pytest.mark.asyncio
async def test_extension_trigger_any_rank_change(
    client: AsyncClient,
    buyer_user: User,
    supplier1: User,
    supplier2: User,
    supplier3: User
):
    now = datetime.now(timezone.utc)
    bid_close = now + timedelta(minutes=8)
    forced_close = now + timedelta(minutes=30)

    rfq_payload = {
        "name": "Any Rank Change RFQ",
        "reference_id": "RFQ-EXT-ANY-RANK",
        "pickup_service_date": (now + timedelta(days=5)).isoformat(),
        "bid_start_time": (now - timedelta(minutes=10)).isoformat(),
        "bid_close_time": bid_close.isoformat(),
        "forced_bid_close_time": forced_close.isoformat(),
        "auction_config": {
            "british_auction_enabled": True,
            "trigger_window_minutes": 20,
            "extension_duration_minutes": 5,
            "extension_trigger_type": "ANY_RANK_CHANGE"
        }
    }
    rfq_res = await client.post("/api/rfqs", json=rfq_payload, headers=get_auth_headers(buyer_user))
    rfq_id = rfq_res.json()["id"]

    # 1. Supplier 1 places bid $3000 (L1) -> First bid establishes ranks -> triggers ANY_RANK_CHANGE
    bid1 = {
        "carrier_name": "Carrier 1",
        "freight_charges": "2600.00",
        "origin_charges": "200.00",
        "destination_charges": "200.00",
        "transit_time_days": 2,
        "validity_date": (now + timedelta(days=10)).isoformat()
    }
    res1 = await client.post(f"/api/auctions/{rfq_id}/bids", json=bid1, headers=get_auth_headers(supplier1))
    assert res1.status_code == 201

    rfq_1 = await client.get(f"/api/rfqs/{rfq_id}", headers=get_auth_headers(buyer_user))
    assert rfq_1.json()["auction_config"]["extension_count"] == 1

    # 2. Supplier 3 places bid $4000 (L2) -> New supplier enters rank -> triggers ANY_RANK_CHANGE
    bid3 = {
        "carrier_name": "Carrier 3",
        "freight_charges": "3600.00",
        "origin_charges": "200.00",
        "destination_charges": "200.00",
        "transit_time_days": 2,
        "validity_date": (now + timedelta(days=10)).isoformat()
    }
    res3 = await client.post(f"/api/auctions/{rfq_id}/bids", json=bid3, headers=get_auth_headers(supplier3))
    assert res3.status_code == 201

    rfq_2 = await client.get(f"/api/rfqs/{rfq_id}", headers=get_auth_headers(buyer_user))
    assert rfq_2.json()["auction_config"]["extension_count"] == 2

    # 3. Supplier 2 places bid $3500 -> Takes L2 from Supplier 3 (Supplier 3 pushed to L3)
    # Note: L1 (Supplier 1 @ $3000) DID NOT CHANGE, but rank of Supplier 3 changed from 2 to 3!
    bid2 = {
        "carrier_name": "Carrier 2",
        "freight_charges": "3100.00",
        "origin_charges": "200.00",
        "destination_charges": "200.00",
        "transit_time_days": 2,
        "validity_date": (now + timedelta(days=10)).isoformat()
    }
    res2 = await client.post(f"/api/auctions/{rfq_id}/bids", json=bid2, headers=get_auth_headers(supplier2))
    assert res2.status_code == 201

    rfq_3 = await client.get(f"/api/rfqs/{rfq_id}", headers=get_auth_headers(buyer_user))
    assert rfq_3.json()["auction_config"]["extension_count"] == 3

    # Verify Activity Log contains proper ANY_RANK_CHANGE extension reason
    act_res = await client.get(f"/api/auctions/{rfq_id}/activity", headers=get_auth_headers(buyer_user))
    assert any("Supplier ranking changed" in a["extension_reason"] for a in act_res.json() if a["extension_reason"])
