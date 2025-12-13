"""
WebSocket API endpoints for real-time monitor updates.
"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.database import AsyncSessionLocal
from app.websocket.manager import ws_manager
from app.api.metrics import get_dashboard_stats
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for real-time monitor stats updates.

    Clients connect to this endpoint and receive real-time updates
    whenever health checks complete.

    Message format:
    {
        "type": "stats_updated",
        "timestamp": "2024-01-01T00:00:00"
    }
    """
    # Accept the WebSocket connection
    await ws_manager.connect(websocket)

    try:
        # Send a welcome message
        await ws_manager.send_personal_message(
            {
                "type": "connected",
                "message": "WebSocket connected successfully"
            },
            websocket
        )
        logger.info("WebSocket client connected successfully")

        # Keep the connection alive and listen for client messages
        while True:
            # Wait for any message from client (ping/pong to keep alive)
            data = await websocket.receive_text()
            logger.debug(f"Received message from client: {data}")

            # Echo back a pong if client sends ping
            if data == "ping":
                await websocket.send_json({"type": "pong"})

    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)
        logger.info("WebSocket client disconnected normally")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        ws_manager.disconnect(websocket)
