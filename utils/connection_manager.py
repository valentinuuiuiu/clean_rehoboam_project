"""WebSocket connection manager with advanced error handling."""
from typing import Dict, Set, Optional, Callable, Awaitable, Any, List
from fastapi import WebSocket
import asyncio
import json
import logging
from datetime import datetime
from dataclasses import dataclass, asdict
from collections import defaultdict

logger = logging.getLogger(__name__)

@dataclass
class ConnectionMetrics:
    """Track connection metrics for monitoring."""
    connected_at: datetime
    message_count: int = 0
    error_count: int = 0
    last_activity: datetime = None
    latency_ms: float = 0.0

class ConnectionManager:
    """Manage WebSocket connections with error handling and metrics."""
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.subscriptions: Dict[str, Set[str]] = defaultdict(set)
        self.metrics: Dict[str, ConnectionMetrics] = {}
        self.handlers: Dict[str, Callable[[str, Any], Awaitable[None]]] = {}
        self._cleanup_task: Optional[asyncio.Task] = None
        
    async def start(self):
        """Start connection manager and cleanup task."""
        self._cleanup_task = asyncio.create_task(self._periodic_cleanup())
        logger.info("Connection manager started")
        
    async def stop(self):
        """Stop connection manager and cleanup."""
        if self._cleanup_task:
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass
        
        # Close all connections
        for client_id in list(self.active_connections.keys()):
            await self.disconnect(client_id)
        logger.info("Connection manager stopped")
        
    async def connect(self, client_id: str, websocket: WebSocket) -> bool:
        """Handle new connection with error handling."""
        try:
            await websocket.accept()
            self.active_connections[client_id] = websocket
            self.metrics[client_id] = ConnectionMetrics(
                connected_at=datetime.now()
            )
            logger.info(f"Client {client_id} connected")
            return True
        except Exception as e:
            logger.error(f"Error accepting connection from {client_id}: {str(e)}")
            return False

    async def disconnect(self, client_id: str):
        """Handle client disconnection."""
        if client_id in self.active_connections:
            try:
                await self.active_connections[client_id].close()
            except Exception as e:
                logger.error(f"Error closing connection for {client_id}: {str(e)}")
            finally:
                self._cleanup_client(client_id)

    def _cleanup_client(self, client_id: str):
        """Clean up client data."""
        self.active_connections.pop(client_id, None)
        self.metrics.pop(client_id, None)
        for channel in list(self.subscriptions.keys()):
            self.subscriptions[channel].discard(client_id)

    async def broadcast(self, message: Any, channel: Optional[str] = None):
        """Broadcast message to all clients or specific channel."""
        if not self.active_connections:
            return

        encoded_message = (
            message if isinstance(message, str)
            else json.dumps(message)
        )

        send_tasks = []
        for client_id, websocket in self.active_connections.items():
            # If no channel specified, send to all clients
            # Otherwise only send to clients subscribed to the specified channel
            if channel is None or (channel in self.subscriptions and client_id in self.subscriptions[channel]):
                send_tasks.append(self._safe_send(client_id, encoded_message))

        if send_tasks:
            results = await asyncio.gather(*send_tasks, return_exceptions=True)
            failed = sum(1 for r in results if isinstance(r, Exception))
            if failed:
                logger.warning(f"{failed} message(s) failed to send")

    async def send_to_client(self, client_id: str, message: Any) -> bool:
        """Send message to a specific client."""
        if not client_id or client_id not in self.active_connections:
            logger.warning(f"Attempted to send to non-existent client: {client_id}")
            return False
            
        encoded_message = (
            message if isinstance(message, str)
            else json.dumps(message)
        )
        
        return await self._safe_send(client_id, encoded_message)
    
    async def _safe_send(self, client_id: str, message: str) -> bool:
        """Send message with error handling."""
        try:
            start_time = datetime.now()
            websocket = self.active_connections[client_id]
            await websocket.send_text(message)
            
            # Update metrics
            metrics = self.metrics[client_id]
            metrics.message_count += 1
            metrics.last_activity = datetime.now()
            metrics.latency_ms = (metrics.last_activity - start_time).total_seconds() * 1000
            
            return True
        except Exception as e:
            logger.error(f"Error sending to {client_id}: {str(e)}")
            metrics = self.metrics[client_id]
            metrics.error_count += 1
            if metrics.error_count >= 3:
                await self.disconnect(client_id)
            return False

    async def subscribe(self, client_id: str, channel: str) -> bool:
        """Subscribe client to channel."""
        if client_id in self.active_connections:
            self.subscriptions[channel].add(client_id)
            return True
        return False

    async def unsubscribe(self, client_id: str, channel: str):
        """Unsubscribe client from channel."""
        self.subscriptions[channel].discard(client_id)

    async def _periodic_cleanup(self):
        """Periodically clean up stale connections."""
        while True:
            try:
                await asyncio.sleep(60)  # Run every minute
                now = datetime.now()
                
                for client_id in list(self.active_connections.keys()):
                    metrics = self.metrics[client_id]
                    
                    # Check for stale connections
                    if metrics.last_activity:
                        idle_time = (now - metrics.last_activity).total_seconds()
                        if idle_time > 300:  # 5 minutes
                            logger.info(f"Disconnecting stale client {client_id}")
                            await self.disconnect(client_id)
                    
                    # Check error rates
                    if metrics.error_count > 5:
                        logger.warning(f"Disconnecting error-prone client {client_id}")
                        await self.disconnect(client_id)
                        
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in cleanup task: {str(e)}")
                await asyncio.sleep(5)  # Back off on error

    def get_connection_stats(self) -> Dict[str, Any]:
        """Get connection statistics."""
        return {
            'total_connections': len(self.active_connections),
            'total_subscriptions': sum(len(subs) for subs in self.subscriptions.values()),
            'channels': {
                channel: len(subs)
                for channel, subs in self.subscriptions.items()
            },
            'clients': {
                client_id: asdict(metrics)
                for client_id, metrics in self.metrics.items()
                if client_id is not None  # Ensure we don't include None keys
            }
        }

    async def register_handler(self, channel: str, handler: Callable[[str, Any], Awaitable[None]]):
        """Register message handler for channel."""
        self.handlers[channel] = handler
        
    async def handle_message(self, client_id: str, message: Dict[str, Any]):
        """Handle incoming message."""
        try:
            channel = message.get('channel')
            if channel in self.handlers:
                await self.handlers[channel](client_id, message)
            else:
                logger.warning(f"No handler for channel: {channel}")
        except Exception as e:
            logger.error(f"Error handling message: {str(e)}")
            metrics = self.metrics.get(client_id)
            if metrics:
                metrics.error_count += 1