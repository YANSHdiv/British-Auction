from datetime import datetime, timedelta, timezone
import pytest
from httpx import AsyncClient
from app.models.user import User
from tests.conftest import get_auth_headers


@pytest.mark.asyncio
async def test_create_rfq_success(client: AsyncClient, buyer_user: User):
    now = datetime.now(timezone.utc)
    payload = {
        "name": "Test Interstate Freight",
        "reference_id": "RFQ-TEST-001",
        "pickup_service_date": (now + timedelta(days=5)).isoformat(),
        "bid_start_time": (now - timedelta(minutes=10)).isoformat(),
        "bid_close_time": (now + timedelta(minutes=30)).isoformat(),
        "forced_bid_close_time": (now + timedelta(minutes=60)).isoformat(),
        "auction_config": {
            "british_auction_enabled": True,
            "trigger_window_minutes": 10,
            "extension_duration_minutes": 5,
            "extension_trigger_type": "BID_RECEIVED"
        }
    }
    headers = get_auth_headers(buyer_user)
    res = await client.post("/api/rfqs", json=payload, headers=headers)
    assert res.status_code == 201
    data = res.json()
    assert data["reference_id"] == "RFQ-TEST-001"
    assert data["effective_status"] == "ACTIVE"
    assert data["auction_config"]["trigger_window_minutes"] == 10
    assert data["auction_config"]["extension_duration_minutes"] == 5


@pytest.mark.asyncio
async def test_rfq_validation_forced_close_must_be_greater(client: AsyncClient, buyer_user: User):
    now = datetime.now(timezone.utc)
    # Forced close is earlier than bid close -> Must fail validation!
    payload = {
        "name": "Invalid Date RFQ",
        "reference_id": "RFQ-FAIL-001",
        "pickup_service_date": (now + timedelta(days=5)).isoformat(),
        "bid_start_time": (now - timedelta(minutes=10)).isoformat(),
        "bid_close_time": (now + timedelta(minutes=30)).isoformat(),
        "forced_bid_close_time": (now + timedelta(minutes=20)).isoformat(),  # < bid_close_time
    }
    headers = get_auth_headers(buyer_user)
    res = await client.post("/api/rfqs", json=payload, headers=headers)
    assert res.status_code == 422
    assert "Forced Bid Close Time must be strictly later than Bid Close Time" in res.text


@pytest.mark.asyncio
async def test_rfq_validation_close_must_be_greater_than_start(client: AsyncClient, buyer_user: User):
    now = datetime.now(timezone.utc)
    payload = {
        "name": "Invalid Start Close RFQ",
        "reference_id": "RFQ-FAIL-002",
        "pickup_service_date": (now + timedelta(days=5)).isoformat(),
        "bid_start_time": (now + timedelta(minutes=30)).isoformat(),
        "bid_close_time": (now + timedelta(minutes=10)).isoformat(),  # < start
        "forced_bid_close_time": (now + timedelta(minutes=40)).isoformat(),
    }
    headers = get_auth_headers(buyer_user)
    res = await client.post("/api/rfqs", json=payload, headers=headers)
    assert res.status_code == 422
    assert "Bid Close Time must be strictly later than Bid Start Time" in res.text


@pytest.mark.asyncio
async def test_supplier_cannot_create_rfq(client: AsyncClient, supplier1: User):
    now = datetime.now(timezone.utc)
    payload = {
        "name": "Supplier Attempt",
        "reference_id": "RFQ-SUP-FAIL",
        "pickup_service_date": (now + timedelta(days=5)).isoformat(),
        "bid_start_time": now.isoformat(),
        "bid_close_time": (now + timedelta(minutes=30)).isoformat(),
        "forced_bid_close_time": (now + timedelta(minutes=60)).isoformat(),
    }
    headers = get_auth_headers(supplier1)
    res = await client.post("/api/rfqs", json=payload, headers=headers)
    assert res.status_code == 403
