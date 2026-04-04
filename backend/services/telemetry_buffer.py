"""
In-memory ring buffer for telemetry frames with EMA smoothing.

Acts as the "event bus": the simulator writes frames, WebSocket readers
consume them via an asyncio.Event notification mechanism.
"""

from __future__ import annotations

import asyncio
import logging
from collections import deque
from datetime import datetime, timezone

from schemas.telemetry import TelemetryFrame

logger = logging.getLogger(__name__)

# Smoothable numeric fields
_SMOOTHABLE = [
    "speed", "fuel_level", "fuel_consumption",
    "oil_pressure", "brake_pressure",
    "coolant_temp", "exhaust_temp", "bearing_temp",
    "voltage", "current", "power",
]


class TelemetryBuffer:
    """Thread-safe ring buffer with EMA smoothing and async notification."""

    def __init__(self, capacity: int = 1000, ema_alpha: float = 0.3):
        self._capacity = capacity
        self._alpha = ema_alpha
        self._buffer: deque[TelemetryFrame] = deque(maxlen=capacity)
        self._ema_state: dict[str, float] = {}
        self._seen_timestamps: deque[str] = deque(maxlen=capacity)
        self._event = asyncio.Event()  # notifies waiters on new data
        self._lock = asyncio.Lock()
        self._frame_count = 0

    @property
    def size(self) -> int:
        return len(self._buffer)

    @property
    def frame_count(self) -> int:
        return self._frame_count

    def _ema_smooth(self, param: str, raw_value: float) -> float:
        """Apply Exponential Moving Average smoothing."""
        prev = self._ema_state.get(param)
        if prev is None:
            self._ema_state[param] = raw_value
            return raw_value
        smoothed = self._alpha * raw_value + (1 - self._alpha) * prev
        self._ema_state[param] = smoothed
        return smoothed

    def _validate(self, frame: TelemetryFrame) -> bool:
        """Basic validation: reject NaN, dedup by timestamp."""
        ts_key = f"{frame.locomotive_id}_{frame.timestamp.isoformat()}"
        if ts_key in self._seen_timestamps:
            logger.debug("Duplicate frame rejected: %s", ts_key)
            return False

        # Check for NaN values
        data_dict = frame.data.model_dump()
        for key in _SMOOTHABLE:
            val = data_dict.get(key)
            if val is not None and val != val:  # NaN check
                logger.warning("NaN value in %s, rejecting frame", key)
                return False

        self._seen_timestamps.append(ts_key)
        return True

    async def push(self, frame: TelemetryFrame) -> bool:
        """
        Push a new frame into the buffer.
        Applies validation, smoothing, and notifies waiters.
        Returns False if frame was rejected.
        """
        async with self._lock:
            if not self._validate(frame):
                return False

            # Apply EMA smoothing to data fields
            data_dict = frame.data.model_dump()
            smoothed = {}
            for key in _SMOOTHABLE:
                raw_val = data_dict.get(key, 0.0)
                smoothed[key] = round(self._ema_smooth(key, raw_val), 2)

            # Create smoothed frame
            from schemas.telemetry import TelemetryData, PositionData
            smoothed_data = TelemetryData(
                **smoothed,
                position=frame.data.position,
            )
            smoothed_frame = frame.model_copy(update={"data": smoothed_data})

            self._buffer.append(smoothed_frame)
            self._frame_count += 1

        # Notify all waiters
        self._event.set()
        self._event.clear()
        return True

    async def get_latest(self, n: int = 1) -> list[TelemetryFrame]:
        """Get the latest N frames."""
        async with self._lock:
            if n >= len(self._buffer):
                return list(self._buffer)
            return list(self._buffer)[-n:]

    async def get_since(self, since: datetime) -> list[TelemetryFrame]:
        """Get all frames since a given timestamp."""
        async with self._lock:
            return [f for f in self._buffer if f.timestamp >= since]

    async def get_range(self, start: datetime, end: datetime) -> list[TelemetryFrame]:
        """Get frames within a time range."""
        async with self._lock:
            return [
                f for f in self._buffer
                if start <= f.timestamp <= end
            ]

    async def wait_for_new(self, timeout: float = 5.0) -> bool:
        """Wait for a new frame to be pushed. Returns False on timeout."""
        try:
            await asyncio.wait_for(self._event.wait(), timeout=timeout)
            return True
        except asyncio.TimeoutError:
            return False

    async def clear(self) -> None:
        async with self._lock:
            self._buffer.clear()
            self._ema_state.clear()
            self._seen_timestamps.clear()
            self._frame_count = 0


# ── Singleton ─────────────────────────────────────────────────

_buffer_instance: TelemetryBuffer | None = None


def get_buffer() -> TelemetryBuffer:
    global _buffer_instance
    if _buffer_instance is None:
        from config import get_settings
        settings = get_settings()
        _buffer_instance = TelemetryBuffer(
            capacity=settings.BUFFER_SIZE,
            ema_alpha=settings.EMA_ALPHA,
        )
    return _buffer_instance
