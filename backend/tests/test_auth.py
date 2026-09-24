import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_register_and_login(client: AsyncClient):
    # 1. Register
    reg_payload = {
        "email": "newuser@example.com",
        "password": "strongpassword123",
        "full_name": "New User",
        "company_name": "New Logistics Co",
        "role": "SUPPLIER"
    }
    res = await client.post("/api/auth/register", json=reg_payload)
    assert res.status_code == 201
    data = res.json()
    assert data["email"] == "newuser@example.com"
    assert data["role"] == "SUPPLIER"

    # 2. Duplicate registration rejected
    res_dup = await client.post("/api/auth/register", json=reg_payload)
    assert res_dup.status_code == 400

    # 3. Login
    login_payload = {
        "email": "newuser@example.com",
        "password": "strongpassword123"
    }
    res_login = await client.post("/api/auth/login", json=login_payload)
    assert res_login.status_code == 200
    token_data = res_login.json()
    assert "access_token" in token_data
    token = token_data["access_token"]

    # 4. Access /me
    res_me = await client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert res_me.status_code == 200
    assert res_me.json()["email"] == "newuser@example.com"


@pytest.mark.asyncio
async def test_invalid_login(client: AsyncClient):
    login_payload = {
        "email": "nonexistent@example.com",
        "password": "wrongpassword"
    }
    res = await client.post("/api/auth/login", json=login_payload)
    assert res.status_code == 401
