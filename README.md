# Цифровой двойник локомотива ВЛ80

Real-time locomotive telemetry dashboard for the Almaty–Taraz route. Visualizes live sensor data, calculates a Health Index, and provides interactive charts, alerts, and an interactive route map.

## Stack

| Layer | Technology |
|---|---|
| Frontend | Vue 3 + Vite + Pinia |
| Charts | Apache ECharts |
| Map | Leaflet.js + CartoDB |
| Backend | Python 3.12 + FastAPI (async) |
| Database | PostgreSQL 16 + SQLAlchemy 2 + Alembic |
| Auth | JWT (python-jose) + bcrypt |
| Export | ReportLab (PDF), CSV |
| Infra | Docker Compose + nginx |

---

## Quick Start

### Prerequisites
- [Docker Desktop](https://www.docker.com/products/docker-desktop/) running

### Run

```bash
git clone <repo-url>
cd railways-solution
docker-compose up --build
```

Open **http://localhost** in your browser.

Login with:
```
Username: admin
Password: admin
```

| Service | URL |
|---|---|
| Frontend | http://localhost |
| Backend API | http://localhost:8000/api |
| Swagger docs | http://localhost:8000/docs |
| ReDoc | http://localhost:8000/redoc |
| PostgreSQL | localhost:**5433** |

---

## Local Development (without Docker)

### Backend

```bash
cd backend

# Create virtual environment
python -m venv .venv
source .venv/bin/activate       # Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set environment variables (or create .env file)
export DATABASE_URL="postgresql+asyncpg://postgres:postgres@localhost:5432/railways"
export DATABASE_URL_SYNC="postgresql://postgres:postgres@localhost:5432/railways"
export SECRET_KEY="your-secret-key"

# Run database migrations
alembic upgrade head

# Start server
uvicorn main:app --reload --port 8000
```

### Frontend

```bash
cd frontend

# Install dependencies
npm install

# Create .env.local
echo "VITE_WS_URL=ws://localhost:8000/api/ws/telemetry" > .env.local
echo "VITE_API_URL=http://localhost:8000/api" >> .env.local

# Start dev server
npm run dev
```

---

## Project Structure

```
railways-solution/
├── docker-compose.yml
├── backend/
│   ├── main.py                  # FastAPI app entry point
│   ├── health_config.yaml       # Health Index thresholds & weights (hot-reload)
│   ├── config.py                # Settings via environment variables
│   ├── routers/
│   │   ├── ws.py                # WebSocket endpoint + heartbeat
│   │   ├── telemetry.py         # REST: history query
│   │   ├── alerts.py            # REST: alerts history
│   │   ├── auth.py              # JWT login / me
│   │   ├── config.py            # Threshold config CRUD
│   │   └── export.py            # CSV + PDF export
│   ├── services/
│   │   ├── simulator.py         # Locomotive telemetry simulator
│   │   ├── health_index.py      # Health Index calculation engine
│   │   ├── alert_engine.py      # Threshold checks with debounce
│   │   ├── telemetry_buffer.py  # EMA ring buffer + deduplication
│   │   ├── event_bus.py         # asyncio pub/sub bus
│   │   └── retention.py         # DB cleanup job
│   ├── models/                  # SQLAlchemy ORM models
│   ├── schemas/                 # Pydantic request/response schemas
│   ├── middleware/              # JWT auth middleware
│   ├── database/                # Engine, session factory, init
│   ├── alembic/                 # Database migrations
│   └── tests/                   # pytest unit tests
└── frontend/
    ├── src/
    │   ├── views/
    │   │   ├── DashboardView.vue   # Cabin — main telemetry screen
    │   │   ├── TrendsView.vue      # ECharts live trend charts
    │   │   ├── AlertsView.vue      # Sticky live alerts + DB history
    │   │   ├── RouteView.vue       # Full Leaflet map
    │   │   ├── SettingsView.vue    # Config, export, connection info
    │   │   └── LoginView.vue       # JWT login
    │   ├── components/cabin/       # Dashboard panel components
    │   ├── stores/                 # Pinia stores (telemetry, auth, ui)
    │   └── services/
    │       └── telemetryService.js # WebSocket client with reconnect
    ├── Dockerfile                  # Multi-stage: node build → nginx
    └── nginx.conf                  # SPA routing + /api proxy
```

---

## Configuration

### Health Index (`backend/health_config.yaml`)

Thresholds and weights are configured in YAML — **no restart required**. Reload via API:

```bash
curl -X POST http://localhost:8000/api/config/reload \
  -H "Authorization: Bearer <admin-token>"
```

Default parameters and weights:

| Parameter | Weight | Normal | Warning | Critical |
|---|---|---|---|---|
| speed | 0.25 | 0–120 km/h | 120–140 | 140–200 |
| fuel_level | 0.25 | 30–100% | 15–30% | 0–15% |
| pressure | 0.25 | 3.0–6.0 bar | 2.0–3.0 | 0.5–2.0 |
| temperature | 0.25 | 60–95°C | 95–105 | 105–130 |

**Health Index formula:**
```
Score_i  = 100 (normal) → 50 (warning) → 0 (critical)  [linear]
RawIndex = Σ(Score_i × weight_i) / Σ(weight_i)
FinalIndex = max(0, RawIndex − 5×warnings − 15×criticals)
```

Categories: **A** (85–100) · **B** (70–85) · **C** (50–70) · **D** (25–50) · **E** (0–25)

### Environment Variables

| Variable | Default | Description |
|---|---|---|
| `DATABASE_URL` | postgresql+asyncpg://... | Async DB connection |
| `SECRET_KEY` | `super-secret-change-me` | JWT signing secret |
| `SIMULATOR_ENABLED` | `true` | Enable telemetry simulator |
| `SIMULATOR_INTERVAL_MS` | `1000` | Tick interval (1000 = 1 Hz) |
| `CORS_ORIGINS` | `[...]` | Allowed frontend origins (JSON array) |
| `DEFAULT_ADMIN_USERNAME` | `admin` | Seeded admin username |
| `DEFAULT_ADMIN_PASSWORD` | `admin` | Seeded admin password |

---

## API Reference

Full interactive docs at **http://localhost:8000/docs**

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| `POST` | `/api/auth/login` | — | Get JWT token |
| `GET` | `/api/auth/me` | user | Current user info |
| `WS` | `/api/ws/telemetry` | — | Live telemetry stream |
| `GET` | `/api/telemetry/latest` | — | Latest frame |
| `GET` | `/api/telemetry/history` | — | DB history (`?minutes=30&limit=200`) |
| `GET` | `/api/alerts` | — | Alerts from DB (`?minutes=30&severity=critical`) |
| `GET` | `/api/config/thresholds` | — | Current Health Index config |
| `GET` | `/api/config/health-formula` | — | Formula with all weights |
| `PUT` | `/api/config/thresholds` | admin | Update parameter thresholds |
| `PUT` | `/api/config/weights` | admin | Update parameter weights |
| `POST` | `/api/config/reload` | admin | Hot-reload config from YAML |
| `GET` | `/api/export/csv` | — | Export telemetry CSV (`?minutes=15`) |
| `GET` | `/api/export/pdf` | — | Diagnostic PDF report (`?minutes=15`) |
| `POST` | `/api/simulator/highload` | — | Toggle ×10 load (`?enabled=true`) |
| `GET` | `/api/healthcheck` | — | Service health check |

### WebSocket Frame

```json
{
  "type": "telemetry",
  "timestamp": "2024-01-01T12:00:00.000Z",
  "locomotive_id": "LOC-001",
  "data": {
    "speed": 87.5,
    "fuel_level": 68.2,
    "pressure": 5.01,
    "temperature": 81.3,
    "position": { "lat": 50.432, "lng": 76.512, "km_marker": 42.3 }
  },
  "health": {
    "index": 82.5,
    "category": "B",
    "label": "Attention",
    "top_factors": [
      { "parameter": "speed", "score": 78.0, "weight": 0.25, "impact": -5.5, "status": "warning" }
    ]
  },
  "alerts": [
    {
      "severity": "warning",
      "code": "SPEED_WARNING",
      "message": "Speed is above warning threshold: 121.3 km/h (limit: 120.0)",
      "recommendation": "Reduce speed to within operational limits",
      "parameter": "speed",
      "value": 121.3,
      "threshold": 120.0,
      "timestamp": "2024-01-01T12:00:00.000Z"
    }
  ]
}
```

---

## Features

- **Live telemetry** via WebSocket at 1 Hz (highload mode: 10 Hz)
- **Health Index** — weighted formula across 4 parameters, alert penalties, A–E categories, top-5 factor breakdown
- **Cabin dashboard** — SVG speedometer, fuel gauge, pressure/temp panel, health ring gauge, mini route progress, live alerts
- **Trend charts** — ECharts with zoom, tooltip, time window selector (1–15 min), CSV/PDF export
- **Interactive map** — Leaflet + CartoDB tiles, real Almaty–Taraz waypoints, live train marker, station markers
- **Alerts** — sticky live panel (120s persistence) + historical view with severity filter
- **Fault injection** — simulator randomly injects temperature spikes and pressure drops (1% per tick)
- **Reconnect** — exponential backoff 2s→30s, missed-frame replay via `?last_timestamp`
- **EMA smoothing** — α=0.3 on all numeric fields, deduplication by timestamp
- **Export** — CSV (raw telemetry) and PDF (summary stats + alerts table) via ReportLab
- **Auth** — JWT tokens, 8h expiry, session persisted in localStorage, admin role for config changes
- **Theme** — dark/light toggle, CSS custom properties throughout

---

## Running Tests

```bash
cd backend
pytest tests/ -v
pytest tests/ --cov=. --cov-report=term-missing
```

---

## Docker Services

| Container | Image | Port |
|---|---|---|
| `railways_db` | postgres:16-alpine | 5433 → 5432 |
| `railways_backend` | ./backend Dockerfile | 8000 → 8000 |
| `railways_frontend` | ./frontend Dockerfile | 80 → 80 |

nginx proxies `/api/*` and `/api/ws/*` to the backend container, so the frontend only needs to connect to port 80.
