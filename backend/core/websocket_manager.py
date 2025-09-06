import asyncio
import json
import logging
from typing import Dict, List, Set, Optional, Any
from fastapi import WebSocket, WebSocketDisconnect
from datetime import datetime
import redis.asyncio as redis
from dataclasses import dataclass, asdict

logger = logging.getLogger(__name__)

@dataclass
class ConnectionInfo:
    websocket: WebSocket
    user_id: Optional[str] = None
    subscriptions: Set[str] = None
    last_ping: datetime = None
    
    def __post_init__(self):
        if self.subscriptions is None:
            self.subscriptions = set()
        if self.last_ping is None:
            self.last_ping = datetime.now()

class WebSocketManager:
    """
    Centralized WebSocket connection manager for Arthachitra.
    Handles market data, order updates, and real-time notifications.
    """
    
    def __init__(self, redis_url: str = "redis://localhost:6379"):
        self.connections: Dict[str, ConnectionInfo] = {}
        self.channel_subscribers: Dict[str, Set[str]] = {}
        self.redis_client: Optional[redis.Redis] = None
        self.pubsub_task: Optional[asyncio.Task] = None
        self.ping_task: Optional[asyncio.Task] = None
        self.redis_url = redis_url
        
    async def start(self):
        """Initialize Redis connection and start background tasks."""
        try:
            self.redis_client = redis.from_url(self.redis_url)
            await self.redis_client.ping()
            logger.info("WebSocket manager connected to Redis")
            
            # Start background tasks
            self.pubsub_task = asyncio.create_task(self._redis_subscriber())
            self.ping_task = asyncio.create_task(self._ping_connections())
            
        except Exception as e:
            logger.error(f"Failed to start WebSocket manager: {e}")
            raise
    
    async def stop(self):
        """Clean up connections and background tasks."""
        if self.pubsub_task:
            self.pubsub_task.cancel()
        if self.ping_task:
            self.ping_task.cancel()
        
        # Close all WebSocket connections
        for connection_id in list(self.connections.keys()):
            await self._disconnect(connection_id, code=1001, reason="Server shutdown")
        
        if self.redis_client:
            await self.redis_client.aclose()
        
        logger.info("WebSocket manager stopped")
    
    async def connect(self, websocket: WebSocket, connection_id: str, user_id: str = None) -> bool:
        """Accept new WebSocket connection."""
        try:
            await websocket.accept()
            
            self.connections[connection_id] = ConnectionInfo(
                websocket=websocket,
                user_id=user_id,
                subscriptions=set(),
                last_ping=datetime.now()
            )
            
            logger.info(f"WebSocket connection established: {connection_id}")
            
            # Send welcome message
            await self._send_to_connection(connection_id, {
                "type": "connection_established",
                "connection_id": connection_id,
                "timestamp": datetime.now().isoformat()
            })
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to establish WebSocket connection {connection_id}: {e}")
            return False
    
    async def disconnect(self, connection_id: str):
        """Handle WebSocket disconnection."""
        await self._disconnect(connection_id)
    
    async def _disconnect(self, connection_id: str, code: int = 1000, reason: str = "Normal closure"):
        """Internal disconnect handler."""
        if connection_id not in self.connections:
            return
        
        connection_info = self.connections[connection_id]
        
        # Unsubscribe from all channels
        for channel in list(connection_info.subscriptions):
            await self._unsubscribe_from_channel(connection_id, channel)
        
        # Close WebSocket connection
        try:
            await connection_info.websocket.close(code=code, reason=reason)
        except Exception as e:
            logger.warning(f"Error closing WebSocket {connection_id}: {e}")
        
        # Remove from connections
        del self.connections[connection_id]
        logger.info(f"WebSocket connection closed: {connection_id}")
    
    async def subscribe(self, connection_id: str, channel: str) -> bool:
        """Subscribe connection to a channel."""
        if connection_id not in self.connections:
            logger.warning(f"Cannot subscribe unknown connection {connection_id} to {channel}")
            return False
        
        connection_info = self.connections[connection_id]
        connection_info.subscriptions.add(channel)
        
        # Add to channel subscribers
        if channel not in self.channel_subscribers:
            self.channel_subscribers[channel] = set()
        self.channel_subscribers[channel].add(connection_id)
        
        logger.info(f"Connection {connection_id} subscribed to {channel}")
        
        # Send confirmation
        await self._send_to_connection(connection_id, {
            "type": "subscription_confirmed",
            "channel": channel,
            "timestamp": datetime.now().isoformat()
        })
        
        return True
    
    async def unsubscribe(self, connection_id: str, channel: str) -> bool:
        """Unsubscribe connection from a channel."""
        return await self._unsubscribe_from_channel(connection_id, channel)
    
    async def _unsubscribe_from_channel(self, connection_id: str, channel: str) -> bool:
        """Internal unsubscribe handler."""
        if connection_id not in self.connections:
            return False
        
        connection_info = self.connections[connection_id]
        connection_info.subscriptions.discard(channel)
        
        # Remove from channel subscribers
        if channel in self.channel_subscribers:
            self.channel_subscribers[channel].discard(connection_id)
            if not self.channel_subscribers[channel]:
                del self.channel_subscribers[channel]
        
        logger.info(f"Connection {connection_id} unsubscribed from {channel}")
        
        # Send confirmation
        await self._send_to_connection(connection_id, {
            "type": "unsubscription_confirmed",
            "channel": channel,
            "timestamp": datetime.now().isoformat()
        })
        
        return True
    
    async def broadcast_to_channel(self, channel: str, message: Dict[str, Any]):
        """Broadcast message to all subscribers of a channel."""
        if channel not in self.channel_subscribers:
            return
        
        subscribers = list(self.channel_subscribers[channel])
        message["channel"] = channel
        message["timestamp"] = datetime.now().isoformat()
        
        # Send to all subscribers
        tasks = []
        for connection_id in subscribers:
            tasks.append(self._send_to_connection(connection_id, message))
        
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
    
    async def send_to_user(self, user_id: str, message: Dict[str, Any]):
        """Send message to all connections of a specific user."""
        user_connections = [
            conn_id for conn_id, info in self.connections.items()
            if info.user_id == user_id
        ]
        
        if not user_connections:
            return
        
        message["timestamp"] = datetime.now().isoformat()
        
        tasks = []
        for connection_id in user_connections:
            tasks.append(self._send_to_connection(connection_id, message))
        
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
    
    async def _send_to_connection(self, connection_id: str, message: Dict[str, Any]):
        """Send message to a specific connection."""
        if connection_id not in self.connections:
            return
        
        connection_info = self.connections[connection_id]
        
        try:
            await connection_info.websocket.send_text(json.dumps(message))
        except Exception as e:
            logger.warning(f"Failed to send message to {connection_id}: {e}")
            # Connection is likely dead, remove it
            await self._disconnect(connection_id, code=1011, reason="Send failed")
    
    async def _redis_subscriber(self):
        """Background task to subscribe to Redis pub/sub channels."""
        if not self.redis_client:
            return
        
        try:
            pubsub = self.redis_client.pubsub()
            
            # Subscribe to various channels
            await pubsub.subscribe(
                "market_data:*",
                "order_updates:*",
                "news:*",
                "system_alerts"
            )
            
            async for message in pubsub.listen():
                if message["type"] == "message":
                    await self._handle_redis_message(message)
                    
        except asyncio.CancelledError:
            logger.info("Redis subscriber task cancelled")
        except Exception as e:
            logger.error(f"Redis subscriber error: {e}")
    
    async def _handle_redis_message(self, message):
        """Handle messages from Redis pub/sub."""
        try:
            channel = message["channel"].decode("utf-8")
            data = json.loads(message["data"].decode("utf-8"))
            
            # Route message to appropriate WebSocket subscribers
            await self.broadcast_to_channel(channel, data)
            
        except Exception as e:
            logger.error(f"Failed to handle Redis message: {e}")
    
    async def _ping_connections(self):
        """Background task to ping connections and remove dead ones."""
        while True:
            try:
                await asyncio.sleep(30)  # Ping every 30 seconds
                
                current_time = datetime.now()
                dead_connections = []
                
                for connection_id, info in self.connections.items():
                    try:
                        await info.websocket.ping()
                        info.last_ping = current_time
                    except Exception:
                        dead_connections.append(connection_id)
                
                # Remove dead connections
                for connection_id in dead_connections:
                    await self._disconnect(connection_id, code=1011, reason="Ping failed")
                
                if dead_connections:
                    logger.info(f"Removed {len(dead_connections)} dead connections")
                
            except asyncio.CancelledError:
                logger.info("Ping task cancelled")
                break
            except Exception as e:
                logger.error(f"Ping task error: {e}")
                await asyncio.sleep(5)
    
    def get_connection_stats(self) -> Dict[str, Any]:
        """Get statistics about current connections."""
        channel_stats = {
            channel: len(subscribers) 
            for channel, subscribers in self.channel_subscribers.items()
        }
        
        user_connections = {}
        for info in self.connections.values():
            if info.user_id:
                user_connections[info.user_id] = user_connections.get(info.user_id, 0) + 1
        
        return {
            "total_connections": len(self.connections),
            "authenticated_users": len([info for info in self.connections.values() if info.user_id]),
            "channel_subscriptions": channel_stats,
            "user_connections": user_connections
        }
    
    def is_healthy(self) -> bool:
        """Check if the WebSocket manager is healthy."""
        return (
            self.redis_client is not None and
            self.pubsub_task is not None and
            not self.pubsub_task.done() and
            self.ping_task is not None and
            not self.ping_task.done()
        )

# Global WebSocket manager instance
websocket_manager = WebSocketManager()
