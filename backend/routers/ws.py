"""
WebSocket endpoint for real-time telemetry streaming.

Features:
- Heartbeat / ping-pong
- Backpressure handling (skip frames if client is slow)
- Reconnect support (client sends last timestamp, server replays from buffer)
- Connection count broadcasting
"""

from __future__ import annotations

import asyncio
import json
import logging
from datetime import datetime, timezone

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query

from services.telemetry_buffer import get_buffer

router = APIRouter(prefix="/api/ws", tags=["websocket"])
logger = logging.getLogger(__name__)

# Track active connections
_connections: set[WebSocket] = set()


def get_connection_count() -> int:
    return len(_connections)


@router.websocket("/telemetry")
async def telemetry_ws(
    websocket: WebSocket,
    last_timestamp: str | None = Query(None, description="ISO timestamp of last received frame for replay"),
):
    """
    Stream live telemetry frames to the client.

    Query params:
        last_timestamp: If provided, replay all buffered frames since this time
    """
    await websocket.accept()
    _connections.add(websocket)
    logger.info(
        "WebSocket connected. Active: %d", len(_connections)
    )

    buffer = get_buffer()

    try:
        # If client sent last_timestamp, replay missed frames
        if last_timestamp:
            try:
                since = datetime.fromisoformat(last_timestamp)
                missed = await buffer.get_since(since)
                for frame in missed:
                    await websocket.send_text(
                        frame.model_dump_json()
                    )
                logger.info("Replayed %d missed frames", len(missed))
            except (ValueError, TypeError):
                logger.warning("Invalid last_timestamp: %s", last_timestamp)

        # Main streaming loop
        last_frame_count = buffer.frame_count

        while True:
            # Wait for new data (with timeout for heartbeat)
            got_new = await buffer.wait_for_new(timeout=5.0)

            if got_new:
                current_count = buffer.frame_count

                # Backpressure: if we missed many frames, just send the latest
                frames_missed = current_count - last_frame_count
                if frames_missed > 10:
                    # Client is slow — send only the latest frame
                    latest = await buffer.get_latest(1)
                    if latest:
                        await websocket.send_text(
                            latest[0].model_dump_json()
                        )
                else:
                    # Send all new frames
                    latest = await buffer.get_latest(max(1, frames_missed))
                    for frame in latest:
                        try:
                            await websocket.send_text(
                                frame.model_dump_json()
                            )
                        except Exception:
                            break

                last_frame_count = current_count
            else:
                # Timeout — send heartbeat
                try:
                    await websocket.send_json({
                        "type": "heartbeat",
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                        "connections": len(_connections),
                        "buffer_size": buffer.size,
                    })
                except Exception:
                    break

            # Check for client messages (non-blocking)
            try:
                data = await asyncio.wait_for(
                    websocket.receive_text(), timeout=0.01
                )
                # Handle client commands
                try:
                    msg = json.loads(data)
                    if msg.get("type") == "ping":
                        await websocket.send_json({
                            "type": "pong",
                            "timestamp": datetime.now(timezone.utc).isoformat(),
                        })
                except json.JSONDecodeError:
                    pass
            except asyncio.TimeoutError:
                pass

    except WebSocketDisconnect:
        logger.info("WebSocket disconnected normally")
    except Exception:
        logger.exception("WebSocket error")
    finally:
        _connections.discard(websocket)
        logger.info("WebSocket removed. Active: %d", len(_connections))
