import asyncio
from datetime import datetime, timedelta, timezone
import pytest
from httpx import AsyncClient
from app.models.user import User
from tests.conftest import get_auth_headers


@pytest.mark.asyncio
async def test_concurrent_bids_submission(
    client: AsyncClient,
    buyer_user: User,
    supplier1: User,
    supplier2: User,
    supplier3: User
):
    now = datetime.now(timezone.utc)
    # Create active RFQ
    rfq_payload = {
        "name": "Concurrent Bidding Test RFQ",
        "reference_id": "RFQ-CONCURRENCY-001",
        "pickup_service_date": (now + timedelta(days=5)).isoformat(),
        "bid_start_time": (now - timedelta(minutes=10)).isoformat(),
        "bid_close_time": (now + timedelta(minutes=30)).isoformat(),
        "forced_bid_close_time": (now + timedelta(minutes=90)).isoformat(),
        "auction_config": {
            "british_auction_enabled": True,
            "trigger_window_minutes": 10,
            "extension_duration_minutes": 5,
            "extension_trigger_type": "BID_RECEIVED"
        }
    }
    rfq_res = await client.post("/api/rfqs", json=rfq_payload, headers=get_auth_headers(buyer_user))
    assert rfq_res.status_code == 201
    rfq_id = rfq_res.json()["id"]

    # Prepare concurrent bid payloads from 3 different suppliers
    bids = [
        (supplier1, {
            "carrier_name": "Supplier 1 Freight",
            "freight_charges": "3000.00",
            "origin_charges": "200.00",
            "destination_charges": "200.00",
            "transit_time_days": 2,
            "validity_date": (now + timedelta(days=10)).isoformat()
        }),
        (supplier2, {
            "carrier_name": "Supplier 2 Express",
            "freight_charges": "2800.00",
            "origin_charges": "200.00",
            "destination_charges": "200.00",
            "transit_time_days": 2,
            "validity_date": (now + timedelta(days=10)).isoformat()
        }),
        (supplier3, {
            "carrier_name": "Supplier 3 Transit",
            "freight_charges": "2600.00",
            "origin_charges": "200.00",
            "destination_charges": "200.00",
            "transit_time_days": 1,
            "validity_date": (now + timedelta(days=10)).isoformat()
        }),
    ]

    async def post_bid(sup, payload):
        return await client.post(
            f"/api/auctions/{rfq_id}/bids",
            json=payload,
            headers=get_auth_headers(sup)
        )

    # Launch all 3 bids simultaneously
    responses = await asyncio.gather(*(post_bid(s, p) for s, p in bids))

    # All 3 bids should succeed with 201 Created
    for res in responses:
        assert res.status_code == 201, f"Failed with {res.status_code}: {res.text}"

    # Verify rankings consistency
    rank_res = await client.get(f"/api/auctions/{rfq_id}/ranking", headers=get_auth_headers(buyer_user))
    assert rank_res.status_code == 200
    rankings = rank_res.json()["rankings"]
    assert len(rankings) == 3

    # Lowest price ($3000 total from Supplier 3) must be L1
    assert rankings[0]["rank_label"] == "L1"
    assert rankings[0]["total_amount"] == "3000.00"
    assert rankings[0]["supplier_name"] == "Supplier Three"

    # Supplier 2 ($3200 total) must be L2
    assert rankings[1]["rank_label"] == "L2"
    assert rankings[1]["total_amount"] == "3200.00"

    # Supplier 1 ($3400 total) must be L3
    assert rankings[2]["rank_label"] == "L3"
    assert rankings[2]["total_amount"] == "3400.00"
