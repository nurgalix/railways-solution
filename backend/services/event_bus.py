"""
In-memory event bus for telemetry routing.

Implements a simple publish/subscribe pattern as an analogue
of Kafka/RabbitMQ for the demo. The simulator publishes frames,
and multiple consumers (WebSocket broadcaster, DB writer, alert
processor) subscribe to receive them.
"""

from __future__ import annotations

import asyncio
import logging
from collections import defaultdict
from typing import Any, Callable, Awaitable

logger = logging.getLogger(__name__)

# Event types
EVENT_TELEMETRY = "telemetry"
EVENT_ALERT = "alert"
EVENT_HEALTH = "health_update"
EVENT_SYSTEM = "system"


class EventBus:
    """
    Lightweight async publish/subscribe event bus.

    Replaces external message brokers (Kafka, RabbitMQ) for demo purposes.
    Supports multiple named channels with multiple subscribers per channel.
    """

    def __init__(self) -> None:
        self._subscribers: dict[str, list[Callable[..., Awaitable[None]]]] = defaultdict(list)
        self._event_count: dict[str, int] = defaultdict(int)
        self._lock = asyncio.Lock()

    def subscribe(self, channel: str, handler: Callable[..., Awaitable[None]]) -> None:
        """Subscribe a handler to a channel."""
        self._subscribers[channel].append(handler)
        logger.info(
            "Subscribed handler %s to channel '%s' (total: %d)",
            handler.__name__, channel, len(self._subscribers[channel]),
        )

    def unsubscribe(self, channel: str, handler: Callable[..., Awaitable[None]]) -> None:
        """Unsubscribe a handler from a channel."""
        if handler in self._subscribers[channel]:
            self._subscribers[channel].remove(handler)

    async def publish(self, channel: str, data: Any) -> int:
        """
        Publish an event to a channel. All subscribed handlers are called
        concurrently. Returns the number of handlers that received the event.
        """
        handlers = self._subscribers.get(channel, [])
        if not handlers:
            return 0

        self._event_count[channel] += 1

        # Fire all handlers concurrently, catching individual errors
        results = await asyncio.gather(
            *(self._safe_call(h, data) for h in handlers),
            return_exceptions=True,
        )

        errors = [r for r in results if isinstance(r, Exception)]
        if errors:
            logger.warning(
                "Channel '%s': %d/%d handlers failed",
                channel, len(errors), len(handlers),
            )

        return len(handlers) - len(errors)

    async def _safe_call(self, handler: Callable, data: Any) -> None:
        """Call handler with error isolation."""
        try:
            await handler(data)
        except Exception:
            logger.exception("Event handler %s failed", handler.__name__)
            raise

    def get_stats(self) -> dict:
        """Return event bus statistics."""
        return {
            "channels": {
                ch: {
                    "subscribers": len(handlers),
                    "events_published": self._event_count.get(ch, 0),
                }
                for ch, handlers in self._subscribers.items()
            },
            "total_events": sum(self._event_count.values()),
        }


# ── Singleton ─────────────────────────────────────────────────

_bus_instance: EventBus | None = None


def get_event_bus() -> EventBus:
    global _bus_instance
    if _bus_instance is None:
        _bus_instance = EventBus()
    return _bus_instance
