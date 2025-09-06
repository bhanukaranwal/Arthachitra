from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from fastapi.security import HTTPAuthorizationCredentials
import json
import asyncio
import logging
from typing import Dict, Any
from uuid import uuid4

from ..core.websocket_manager import websocket_manager
from ..core.auth.jwt_handler import jwt_handler, security

logger = logging.getLogger(__name__)

websocket_router = APIRouter()

@websocket_router.websocket("/market/{symbol}")
async def market_data_websocket(websocket: WebSocket, symbol: str):
    """WebSocket endpoint for real-time market data."""
    connection_id = str(uuid4())
    
    try:
        # Accept WebSocket connection
        success = await websocket_manager.connect(websocket, connection_id)
        if not success:
            await websocket.close(code=1011, reason="Connection failed")
            return
        
        # Subscribe to market data channel
        channel = f"market_data:{symbol}"
        await websocket_manager.subscribe(connection_id, channel)
        
        logger.info(f"WebSocket connected for market data: {symbol}")
        
        # Keep connection alive and handle messages
        while True:
            try:
                # Wait for client messages
                data = await websocket.receive_text()
                message = json.loads(data)
                
                # Handle different message types
                if message.get("type") == "subscribe":
                    new_symbol = message.get("symbol")
                    if new_symbol:
                        new_channel = f"market_data:{new_symbol}"
                        await websocket_manager.subscribe(connection_id, new_channel)
                
                elif message.get("type") == "unsubscribe":
                    old_symbol = message.get("symbol")
                    if old_symbol:
                        old_channel = f"market_data:{old_symbol}"
                        await websocket_manager.unsubscribe(connection_id, old_channel)
                
                elif message.get("type") == "ping":
                    # Respond to ping with pong
                    await websocket.send_text(json.dumps({"type": "pong"}))
                
            except WebSocketDisconnect:
                break
            except Exception as e:
                logger.error(f"Error in market data WebSocket: {e}")
                break
    
    except Exception as e:
        logger.error(f"WebSocket connection error: {e}")
    
    finally:
        await websocket_manager.disconnect(connection_id)

@websocket_router.websocket("/orderbook/{symbol}")
async def orderbook_websocket(websocket: WebSocket, symbol: str):
    """WebSocket endpoint for real-time order book data."""
    connection_id = str(uuid4())
    
    try:
        success = await websocket_manager.connect(websocket, connection_id)
        if not success:
            await websocket.close(code=1011, reason="Connection failed")
            return
        
        # Subscribe to order book channel
        channel = f"orderbook:{symbol}"
        await websocket_manager.subscribe(connection_id, channel)
        
        logger.info(f"WebSocket connected for order book: {symbol}")
        
        while True:
            try:
                data = await websocket.receive_text()
                message = json.loads(data)
                
                # Handle order book specific messages
                if message.get("type") == "depth_level":
                    depth = message.get("depth", 10)
                    # Request specific depth level
                    await websocket_manager.broadcast_to_channel(
                        channel, 
                        {"type": "depth_request", "depth": depth}
                    )
                
            except WebSocketDisconnect:
                break
            except Exception as e:
                logger.error(f"Error in order book WebSocket: {e}")
                break
    
    finally:
        await websocket_manager.disconnect(connection_id)

@websocket_router.websocket("/user")
async def user_websocket(websocket: WebSocket, token: str):
    """WebSocket endpoint for user-specific updates (orders, positions, etc.)."""
    connection_id = str(uuid4())
    
    try:
        # Authenticate user
        try:
            payload = jwt_handler.decode_token(token)
            user_id = payload.get("sub")
            if not user_id:
                await websocket.close(code=1008, reason="Invalid token")
                return
        except Exception:
            await websocket.close(code=1008, reason="Authentication failed")
            return
        
        # Connect with user context
        success = await websocket_manager.connect(websocket, connection_id, user_id)
        if not success:
            await websocket.close(code=1011, reason="Connection failed")
            return
        
        # Subscribe to user channels
        user_channels = [
            f"orders:{user_id}",
            f"positions:{user_id}",
            f"portfolio:{user_id}",
            f"alerts:{user_id}"
        ]
        
        for channel in user_channels:
            await websocket_manager.subscribe(connection_id, channel)
        
        logger.info(f"User WebSocket connected: {user_id}")
        
        while True:
            try:
                data = await websocket.receive_text()
                message = json.loads(data)
                
                # Handle user-specific messages
                if message.get("type") == "heartbeat":
                    await websocket.send_text(json.dumps({
                        "type": "heartbeat_ack",
                        "timestamp": message.get("timestamp")
                    }))
                
            except WebSocketDisconnect:
                break
            except Exception as e:
                logger.error(f"Error in user WebSocket: {e}")
                break
    
    finally:
        await websocket_manager.disconnect(connection_id)
