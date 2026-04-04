"""
Locomotive Digital Twin — FastAPI Backend

Main application entry point with lifespan management,
CORS middleware, and all route registrations.
"""

import logging
from contextlib import asynccontextmanager
from datetime import datetime, timezone

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import get_settings

# ── Logging ───────────────────────────────────────────────────

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-7s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


# ── Lifespan ──────────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown hooks."""
    settings = get_settings()
    logger.info("Starting Locomotive Digital Twin backend…")

    # 1. Initialise database tables & seed admin
    from database.init_db import init_db
    await init_db()
    logger.info("Database initialised")

    # 2. Load health config
    from services.health_index import load_config
    load_config(settings.HEALTH_CONFIG_PATH)
    logger.info("Health config loaded")

    # 3. Start telemetry simulator
    if settings.SIMULATOR_ENABLED:
        from services.simulator import get_simulator
        simulator = get_simulator()
        await simulator.start()
        logger.info("Telemetry simulator started (interval=%dms)", settings.SIMULATOR_INTERVAL_MS)

    logger.info("Backend ready ✓")
    yield

    # Shutdown
    logger.info("Shutting down…")
    if settings.SIMULATOR_ENABLED:
        from services.simulator import get_simulator
        simulator = get_simulator()
        await simulator.stop()
    logger.info("Shutdown complete.")


# ── App ───────────────────────────────────────────────────────

settings = get_settings()

app = FastAPI(
    title="Locomotive Digital Twin API",
    description=(
        "Real-time telemetry streaming, Health Index calculation, "
        "alert management, and diagnostic reporting for locomotive monitoring."
    ),
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# ── CORS ──────────────────────────────────────────────────────

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ───────────────────────────────────────────────────

from routers.ws import router as ws_router
from routers.telemetry import router as telemetry_router
from routers.health import router as health_router
from routers.alerts import router as alerts_router
from routers.config import router as config_router
from routers.export import router as export_router
from routers.auth import router as auth_router

app.include_router(ws_router)
app.include_router(telemetry_router)
app.include_router(health_router)
app.include_router(alerts_router)
app.include_router(config_router)
app.include_router(export_router)
app.include_router(auth_router)


# ── Health Check & Root ───────────────────────────────────────

@app.get("/", tags=["root"])
async def root():
    return {
        "service": "Locomotive Digital Twin API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
    }


@app.get("/api/healthcheck", tags=["monitoring"])
async def healthcheck():
    """Service health check endpoint."""
    from services.telemetry_buffer import get_buffer
    from routers.ws import get_connection_count

    buffer = get_buffer()
    return {
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "buffer_frames": buffer.size,
        "total_processed": buffer.frame_count,
        "ws_connections": get_connection_count(),
        "simulator_enabled": settings.SIMULATOR_ENABLED,
    }


@app.get("/api/metrics", tags=["monitoring"])
async def metrics():
    """Basic service metrics."""
    from services.telemetry_buffer import get_buffer
    from routers.ws import get_connection_count

    buffer = get_buffer()
    return {
        "telemetry_buffer_size": buffer.size,
        "telemetry_frames_total": buffer.frame_count,
        "websocket_connections_active": get_connection_count(),
    }


# ── Simulator control ────────────────────────────────────────

@app.post("/api/simulator/highload", tags=["simulator"])
async def toggle_highload(enabled: bool = True):
    """Toggle highload mode (×10 telemetry frequency) for stress testing."""
    from services.simulator import get_simulator
    simulator = get_simulator()
    simulator.set_highload(enabled)
    return {"highload": enabled, "frequency_hz": 10 if enabled else 1}


@app.post("/api/simulator/toggle", tags=["simulator"])
async def toggle_simulator(enabled: bool = True):
    """Start or stop the telemetry simulator."""
    from services.simulator import get_simulator
    simulator = get_simulator()
    if enabled:
        await simulator.start()
    else:
        await simulator.stop()
    return {"simulator_running": enabled}
