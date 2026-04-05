"""
Mock telemetry simulator that generates realistic locomotive data.

Simulates a journey: station → acceleration → cruise → deceleration → station.
Periodically injects faults (temperature spikes, pressure drops, voltage sags).
Supports highload mode (×10 frequency) for stress testing.
"""

from __future__ import annotations

import asyncio
import logging
import random
from datetime import datetime, timezone
from typing import Any

from config import get_settings
from schemas.telemetry import (
    AlertData,
    HealthIndexResponse,
    PositionData,
    TelemetryData,
    TelemetryFrame,
)
from services.alert_engine import get_alert_engine
from services.health_index import calculate_health_index
from services.telemetry_buffer import get_buffer

logger = logging.getLogger(__name__)

# ── Simple linear track (0–100 km) ───────────────────────────
# Start/end coordinates for linear interpolation
_TRACK_START = (50.0, 30.0)   # lat, lng at km 0
_TRACK_END   = (51.0, 31.0)   # lat, lng at km 100
_TRACK_LENGTH_KM = 100.0


class LocomotiveSimulator:
    """Generates realistic telemetry for a single locomotive."""

    def __init__(self, locomotive_id: str = "LOC-001"):
        self.locomotive_id = locomotive_id
        self._running = False
        self._task: asyncio.Task | None = None
        self._highload = False
        self._tick = 0

        # Journey state
        self._phase = "accelerating"  # accelerating / cruising / decelerating / stopped
        self._phase_ticks = 0
        self._phase_duration = random.randint(30, 60)

        # Current values (initialised to nominal)
        self._speed = 0.0
        self._target_speed = random.uniform(80, 120)
        self._fuel_level = random.uniform(75, 95)
        self._km = 0.0

        # Fault injection
        self._fault_active: dict[str, int] = {}  # param → remaining ticks

    # ── Lifecycle ─────────────────────────────────────────────

    async def start(self) -> None:
        if self._running:
            return
        self._running = True
        self._task = asyncio.create_task(self._run_loop())
        logger.info("Simulator started for %s", self.locomotive_id)

    async def stop(self) -> None:
        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        logger.info("Simulator stopped for %s", self.locomotive_id)

    def set_highload(self, enabled: bool) -> None:
        """Toggle ×10 highload mode."""
        self._highload = enabled
        logger.info("Highload mode: %s", enabled)

    # ── Main loop ─────────────────────────────────────────────

    async def _run_loop(self) -> None:
        settings = get_settings()
        buffer = get_buffer()
        alert_engine = get_alert_engine()

        from services.event_bus import get_event_bus, EVENT_TELEMETRY, EVENT_ALERT
        bus = get_event_bus()

        while self._running:
            interval = settings.SIMULATOR_INTERVAL_MS / 1000.0
            if self._highload:
                interval /= 10  # ×10 frequency

            try:
                frame = self._generate_frame(alert_engine)
                await buffer.push(frame)

                # Publish to event bus (consumers: WS broadcaster, DB writer, etc.)
                await bus.publish(EVENT_TELEMETRY, frame)

                # Persist to DB every 5th tick (reduce DB load)
                if self._tick % 5 == 0:
                    await self._persist_frame(frame)

                # Persist and publish alerts
                if frame.alerts:
                    await self._persist_alerts(frame.alerts)
                    await bus.publish(EVENT_ALERT, frame.alerts)

            except Exception:
                logger.exception("Simulator tick error")

            await asyncio.sleep(interval)

    # ── Frame generation ──────────────────────────────────────

    def _generate_frame(self, alert_engine: Any) -> TelemetryFrame:
        self._tick += 1
        self._advance_journey()
        self._process_faults()

        now = datetime.now(timezone.utc)
        position = self._get_position()

        # Build telemetry values (more stable - reduced noise)
        noise = lambda scale=1.0: random.gauss(0, scale * 0.5)  # Halved noise

        speed = max(0.0, self._speed + noise(0.3))
        fuel_consumption = max(0.0, speed * 0.12 + noise(0.2)) if speed > 0 else 0.3

        self._fuel_level = max(0, self._fuel_level - fuel_consumption * 0.0008)

        # More stable pressure and temperature (stay well within normal ranges)
        pressure = 4.5 + noise(0.05) - (speed / 400)  # Less speed impact
        temperature = 72 + speed * 0.12 + noise(0.3)  # Lower base, less speed impact

        # Apply faults (reduced severity)
        if "temperature" in self._fault_active:
            temperature += random.uniform(12, 22)  # Less extreme (was 15-30)
        if "pressure" in self._fault_active:
            pressure -= random.uniform(1.0, 1.8)  # Less extreme (was 1.5-2.5)
            pressure = max(1.0, pressure)

        telemetry_dict = {
            "speed": round(speed, 1),
            "fuel_level": round(self._fuel_level, 1),
            "pressure": round(pressure, 2),
            "temperature": round(temperature, 1),
        }

        # Calculate health index
        health = calculate_health_index(telemetry_dict)

        # Check for alerts
        raw_alerts = alert_engine.check(
            telemetry_dict,
            locomotive_id=self.locomotive_id,
        )
        alert_datas = [
            AlertData(
                severity=a["severity"],
                code=a["code"],
                message=a["message"],
                parameter=a.get("parameter"),
                value=a.get("value"),
                threshold=a.get("threshold"),
                recommendation=a.get("recommendation"),
                timestamp=a.get("timestamp"),
            )
            for a in raw_alerts
        ]

        # Recalculate health with alerts factored in
        if raw_alerts:
            health = calculate_health_index(
                telemetry_dict, active_alerts=raw_alerts
            )

        data = TelemetryData(
            **telemetry_dict,
            position=PositionData(
                lat=position[0],
                lng=position[1],
                km_marker=position[2],
            ),
        )

        return TelemetryFrame(
            type="telemetry",
            timestamp=now,
            locomotive_id=self.locomotive_id,
            data=data,
            health=health,
            alerts=alert_datas,
        )

    # ── Journey phases ────────────────────────────────────────

    def _advance_journey(self) -> None:
        self._phase_ticks += 1

        if self._phase == "stopped":
            if self._phase_ticks >= self._phase_duration:
                self._phase = "accelerating"
                self._phase_ticks = 0
                self._phase_duration = random.randint(20, 40)
                self._target_speed = random.uniform(80, 130)

        elif self._phase == "accelerating":
            accel = random.uniform(0.5, 1.5)
            self._speed = min(self._speed + accel, self._target_speed)
            if self._speed >= self._target_speed:
                self._phase = "cruising"
                self._phase_ticks = 0
                self._phase_duration = random.randint(120, 300)

        elif self._phase == "cruising":
            self._speed += random.gauss(0, 0.3)
            self._speed = max(0, min(self._speed, self._target_speed + 10))
            if self._phase_ticks >= self._phase_duration:
                self._phase = "decelerating"
                self._phase_ticks = 0
                self._phase_duration = random.randint(20, 40)

        elif self._phase == "decelerating":
            decel = random.uniform(0.5, 2.0)
            self._speed = max(0, self._speed - decel)
            if self._speed <= 0:
                self._speed = 0
                self._phase = "stopped"
                self._phase_ticks = 0
                self._phase_duration = random.randint(30, 90)

        # Advance km marker
        self._km += self._speed / 3600  # km per second at current speed
        if self._km > _TRACK_LENGTH_KM:
            self._km = 0  # loop back

    def _get_position(self) -> tuple[float, float, float]:
        """Linear interpolation along the simple track."""
        ratio = self._km / max(_TRACK_LENGTH_KM, 1e-9)
        ratio = min(ratio, 1.0)
        lat = _TRACK_START[0] + (_TRACK_END[0] - _TRACK_START[0]) * ratio
        lng = _TRACK_START[1] + (_TRACK_END[1] - _TRACK_START[1]) * ratio
        return (round(lat, 6), round(lng, 6), round(self._km, 1))

    # ── Fault injection ───────────────────────────────────────

    def _process_faults(self) -> None:
        """Randomly inject and expire faults."""
        # Expire active faults
        expired = [p for p, t in self._fault_active.items() if t <= 0]
        for p in expired:
            del self._fault_active[p]
            logger.info("Fault expired: %s", p)

        # Decrement counters
        for p in list(self._fault_active):
            self._fault_active[p] -= 1

        # Random injection (0.2% chance per tick - much rarer than before)
        # Only inject faults if none are currently active (avoid stacking)
        if not self._fault_active:
            fault_candidates = ["temperature", "pressure"]
            for fc in fault_candidates:
                if random.random() < 0.002:  # 0.2% chance (was 1%)
                    duration = random.randint(8, 20)  # shorter duration (was 10-60)
                    self._fault_active[fc] = duration
                    logger.info("Fault injected: %s for %d ticks", fc, duration)
                    break  # Only inject one fault at a time

    # ── Persistence ───────────────────────────────────────────

    async def _persist_frame(self, frame: TelemetryFrame) -> None:
        """Persist telemetry frame to database."""
        try:
            from database.engine import async_session_factory
            from models.telemetry import TelemetryReading

            async with async_session_factory() as session:
                reading = TelemetryReading(
                    timestamp=frame.timestamp,
                    locomotive_id=frame.locomotive_id,
                    speed=frame.data.speed,
                    fuel_level=frame.data.fuel_level,
                    pressure=frame.data.pressure,
                    temperature=frame.data.temperature,
                    latitude=frame.data.position.lat,
                    longitude=frame.data.position.lng,
                    km_marker=frame.data.position.km_marker,
                    health_index=frame.health.index,
                    health_category=frame.health.category,
                    raw_json=frame.model_dump(mode="json"),
                )
                session.add(reading)
                await session.commit()
        except Exception:
            logger.exception("Failed to persist telemetry frame")

    async def _persist_alerts(self, alerts: list[AlertData]) -> None:
        """Persist alert events to database."""
        try:
            from database.engine import async_session_factory
            from models.telemetry import AlertEvent

            async with async_session_factory() as session:
                for a in alerts:
                    event = AlertEvent(
                        timestamp=a.timestamp or datetime.now(timezone.utc),
                        locomotive_id=self.locomotive_id,
                        severity=a.severity,
                        code=a.code,
                        message=a.message,
                        parameter=a.parameter,
                        value=a.value,
                        threshold=a.threshold,
                        recommendation=a.recommendation,
                        acknowledged=False,
                    )
                    session.add(event)
                await session.commit()
        except Exception:
            logger.exception("Failed to persist alerts")


# ── Singleton ─────────────────────────────────────────────────

_simulator: LocomotiveSimulator | None = None


def get_simulator() -> LocomotiveSimulator:
    global _simulator
    if _simulator is None:
        settings = get_settings()
        _simulator = LocomotiveSimulator(
            locomotive_id=settings.SIMULATOR_LOCOMOTIVE_ID,
        )
    return _simulator
