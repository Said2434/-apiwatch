"""
WebSocket connection manager for real-time updates.
Handles client connections and broadcasts stats updates.
"""
from fastapi import WebSocket
from typing import List, Dict, Any
import logging
import json

logger = logging.getLogger(__name__)


class WebSocketManager:
    """
    Manages WebSocket connections and broadcasts updates to connected clients.
    """

    def __init__(self):
        # Store active WebSocket connections
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        """
        Accept and register a new WebSocket connection.

        Args:
            websocket: The WebSocket connection to register
        """
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"WebSocket connected. Total connections: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        """
        Remove a WebSocket connection from active connections.

        Args:
            websocket: The WebSocket connection to remove
        """
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            logger.info(f"WebSocket disconnected. Total connections: {len(self.active_connections)}")

    async def send_personal_message(self, message: Dict[Any, Any], websocket: WebSocket):
        """
        Send a message to a specific WebSocket connection.

        Args:
            message: The message data to send (will be converted to JSON)
            websocket: The target WebSocket connection
        """
        try:
            await websocket.send_json(message)
        except Exception as e:
            logger.error(f"Error sending personal message: {e}")
            self.disconnect(websocket)

    async def broadcast(self, message: Dict[Any, Any]):
        """
        Broadcast a message to all connected WebSocket clients.

        Args:
            message: The message data to broadcast (will be converted to JSON)
        """
        if not self.active_connections:
            return

        logger.info(f"Broadcasting to {len(self.active_connections)} connections")

        # Send to all connections and collect failed ones
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(f"Error broadcasting to connection: {e}")
                disconnected.append(connection)

        # Remove failed connections
        for connection in disconnected:
            self.disconnect(connection)


# Global WebSocket manager instance
ws_manager = WebSocketManager()
