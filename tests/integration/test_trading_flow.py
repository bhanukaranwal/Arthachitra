import pytest
import asyncio
from httpx import AsyncClient
from backend.main import app

@pytest.mark.asyncio
async def test_complete_trading_flow():
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Login
        login_response = await client.post("/auth/login", json={
            "username": "demo_user",
            "password": "demo_password"
        })
        assert login_response.status_code == 200
        token = login_response.json()["access_token"]
        
        headers = {"Authorization": f"Bearer {token}"}
        
        # Get portfolio
        portfolio_response = await client.get("/api/v1/portfolio", headers=headers)
        assert portfolio_response.status_code == 200
        
        # Place order
        order_response = await client.post("/api/v1/execution/orders", 
            json={
                "symbol": "RELIANCE",
                "side": "BUY",
                "quantity": 10,
                "order_type": "MARKET"
            },
            headers=headers
        )
        assert order_response.status_code == 200
        order_id = order_response.json()["order_id"]
        
        # Check order status
        order_status = await client.get(f"/api/v1/execution/orders/{order_id}", headers=headers)
        assert order_status.status_code == 200
