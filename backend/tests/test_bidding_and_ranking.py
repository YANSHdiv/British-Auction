from datetime import datetime, timedelta, timezone
from decimal import Decimal
import pytest
from httpx import AsyncClient
from app.models.user import User
from tests.conftest import get_auth_headers


@pytest.mark.asyncio
async def test_bidding_rules_and_ranking(
    client: AsyncClient,
    buyer_user: User,
    supplier1: User,
    supplier2: User,
    supplier3: User
):
    now = datetime.now(timezone.utc)
    # 1. Create an active RFQ
    rfq_payload = {
        "name": "Ranking Test RFQ",
        "reference_id": "RFQ-RANK-001",
        "pickup_service_date": (now + timedelta(days=5)).isoformat(),
        "bid_start_time": (now - timedelta(minutes=10)).isoformat(),
        "bid_close_time": (now + timedelta(hours=2)).isoformat(),  # Not in trigger window
        "forced_bid_close_time": (now + timedelta(hours=4)).isoformat(),
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

    # 2. Supplier 1 submits initial bid: $5,000 (Freight 4000 + Origin 500 + Dest 500)
    bid1_payload = {
        "carrier_name": "Alpha Carrier Express",
        "freight_charges": "4000.00",
        "origin_charges": "500.00",
        "destination_charges": "500.00",
        "transit_time_days": 3,
        "validity_date": (now + timedelta(days=10)).isoformat()
    }
    res1 = await client.post(f"/api/auctions/{rfq_id}/bids", json=bid1_payload, headers=get_auth_headers(supplier1))
    assert res1.status_code == 201
    b1_data = res1.json()
    assert b1_data["total_amount"] == "5000.00"
    assert b1_data["rank_label"] == "L1"

    # 3. Supplier 2 submits lower bid: $4,500 -> Becomes new L1
    bid2_payload = {
        "carrier_name": "Beta Quick Freight",
        "freight_charges": "3500.00",
        "origin_charges": "500.00",
        "destination_charges": "500.00",
        "transit_time_days": 2,
        "validity_date": (now + timedelta(days=10)).isoformat()
    }
    res2 = await client.post(f"/api/auctions/{rfq_id}/bids", json=bid2_payload, headers=get_auth_headers(supplier2))
    assert res2.status_code == 201
    b2_data = res2.json()
    assert b2_data["total_amount"] == "4500.00"
    assert b2_data["rank_label"] == "L1"

    # 4. Check rankings endpoint: Supplier 2 is L1, Supplier 1 is L2
    res_ranks = await client.get(f"/api/auctions/{rfq_id}/ranking", headers=get_auth_headers(supplier1))
    assert res_ranks.status_code == 200
    ranks_data = res_ranks.json()["rankings"]
    assert len(ranks_data) == 2
    assert ranks_data[0]["rank_label"] == "L1"
    assert ranks_data[0]["supplier_name"] == "Supplier Two"
    assert ranks_data[0]["total_amount"] == "4500.00"
    assert ranks_data[1]["rank_label"] == "L2"
    assert ranks_data[1]["supplier_name"] == "Supplier One"
    assert ranks_data[1]["total_amount"] == "5000.00"

    # 5. British Auction Rule Test: Supplier 1 tries to submit HIGHER bid ($5,200) -> Must be rejected!
    bid1_higher = {
        "carrier_name": "Alpha Carrier Express",
        "freight_charges": "4200.00",
        "origin_charges": "500.00",
        "destination_charges": "500.00",
        "transit_time_days": 3,
        "validity_date": (now + timedelta(days=10)).isoformat()
    }
    res_fail_high = await client.post(f"/api/auctions/{rfq_id}/bids", json=bid1_higher, headers=get_auth_headers(supplier1))
    assert res_fail_high.status_code == 400
    assert "must be strictly lower than your previous best bid" in res_fail_high.text

    # 6. Supplier 1 tries to submit EQUAL bid ($5,000) -> Must be rejected!
    res_fail_equal = await client.post(f"/api/auctions/{rfq_id}/bids", json=bid1_payload, headers=get_auth_headers(supplier1))
    assert res_fail_equal.status_code == 400
    assert "must be strictly lower than your previous best bid" in res_fail_equal.text

    # 7. Supplier 1 submits lower bid: $4,200 -> Becomes new L1!
    bid1_lower = {
        "carrier_name": "Alpha Carrier Express",
        "freight_charges": "3200.00",
        "origin_charges": "500.00",
        "destination_charges": "500.00",
        "transit_time_days": 3,
        "validity_date": (now + timedelta(days=10)).isoformat()
    }
    res_success_lower = await client.post(f"/api/auctions/{rfq_id}/bids", json=bid1_lower, headers=get_auth_headers(supplier1))
    assert res_success_lower.status_code == 201
    assert res_success_lower.json()["total_amount"] == "4200.00"
    assert res_success_lower.json()["rank_label"] == "L1"

    # 8. Check my-bid endpoint for Supplier 1
    res_my_bid = await client.get(f"/api/auctions/{rfq_id}/my-bid", headers=get_auth_headers(supplier1))
    assert res_my_bid.status_code == 200
    my_bid = res_my_bid.json()
    assert my_bid["rank_label"] == "L1"
    assert my_bid["total_amount"] == "4200.00"


@pytest.mark.asyncio
async def test_tie_breaking_deterministic(
    client: AsyncClient,
    buyer_user: User,
    supplier1: User,
    supplier2: User
):
    now = datetime.now(timezone.utc)
    rfq_payload = {
        "name": "Tie Breaker RFQ",
        "reference_id": "RFQ-TIE-001",
        "pickup_service_date": (now + timedelta(days=5)).isoformat(),
        "bid_start_time": (now - timedelta(minutes=10)).isoformat(),
        "bid_close_time": (now + timedelta(hours=2)).isoformat(),
        "forced_bid_close_time": (now + timedelta(hours=4)).isoformat(),
    }
    rfq_res = await client.post("/api/rfqs", json=rfq_payload, headers=get_auth_headers(buyer_user))
    rfq_id = rfq_res.json()["id"]

    # Both suppliers submit exactly $4,000
    bid_payload = {
        "carrier_name": "Fleet",
        "freight_charges": "3000.00",
        "origin_charges": "500.00",
        "destination_charges": "500.00",
        "transit_time_days": 2,
        "validity_date": (now + timedelta(days=10)).isoformat()
    }
    # Supplier 1 submits first
    res1 = await client.post(f"/api/auctions/{rfq_id}/bids", json=bid_payload, headers=get_auth_headers(supplier1))
    assert res1.status_code == 201
    assert res1.json()["rank_label"] == "L1"

    # Supplier 2 submits second with same amount
    res2 = await client.post(f"/api/auctions/{rfq_id}/bids", json=bid_payload, headers=get_auth_headers(supplier2))
    assert res2.status_code == 201
    assert res2.json()["rank_label"] == "L2"  # Earlier submission takes priority!
