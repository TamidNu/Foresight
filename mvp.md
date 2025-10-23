# Getting on the same page about what we are building exactly

- this track session is going to be very much architecture focused, so I encourage you guys to take notes and ask questions when you have them!

What Foresight (MVP) actually does

- It’s a PMS plug-in layer that ingests multiple demand signals (historical bookings/occ/ADR, events, weather, flights, comp rates, direct traffic) and outputs dynamic price recommendations that update frequently (hourly-ish) with simple guardrails and explanations the manager trusts.

- For the pilot, we support one PMS (Guestline) and one hotel in Dublin.

- We score events (Impact Score) and refresh those ~4× per day; we reprice on schedule and when meaningful changes happen (pickup spikes, event impact changes).

- We keep it explainable, quick to infer, and easy to export/approve in the UI.

- No functional changes to the above—everything below is just how to implement it cleanly with your current stack.

```
tamidnu-foresight/
├── README.md
├── dev-setup.md
├── PRD.md                         # (keep, but update DB to Neon & remove Mongo mentions)
├── tech_README.md                 # (align to Neon + this DS/ML structure)
├── infra/
│   ├── render/
│   │   ├── web-backend.yaml       # Render FastAPI service (prod & staging)
│   │   ├── worker-train.yaml      # Render background worker for daily retrain
│   │   └── cron.json              # Render cron schedule (event score 4x/day; retrain 1x/day)
│   └── vercel/
│       └── vercel.json            # Next.js config (already OK)
├── backend/
│   ├── main.py
│   ├── requirements.txt           # + add: sqlalchemy, psycopg, pydantic[email], httpx
│   ├── .env.example               # add NEON_*, S3_*, GUESTLINE_* keys (see below)
│   └── app/
│       ├── controllers/
│       │   ├── hello_controller.py
│       │   ├── user_controller.py
│       │   ├── pricing_controller.py        # NEW: /api/pricing/* endpoints
│       │   ├── events_controller.py         # manager adds manual events
│       │   └── health_controller.py         # /api/health, /api/model/status
│       ├── models/
│       │   ├── dto.py                        # PricingRequest/Response etc. (see below)
│       │   └── orm.py                        # SQLAlchemy models for Neon tables
│       ├── repositories/
│       │   ├── database.py                   # Neon connection/session
│       │   ├── features_repo.py              # feature/materialized view access
│       │   ├── model_registry_repo.py        # get/set active model artifact uri
│       │   ├── predictions_repo.py           # log quotes/applied prices
│       │   ├── events_repo.py                # manual events CRUD
│       │   └── guestline_repo.py             # Guestline API adapter (read-only MVP1)
│       └── services/
│           ├── user_service.py
│           ├── feature_builder.py            # build runtime feature rows
│           ├── ml_service.py                 # load model, predict, explain
│           ├── pricing_service.py            # orchestrates price calc + guardrails
│           └── scheduler_service.py          # triggers for refresh (optional)
├── ml/                                      # rename ds-ml → ml
│   ├── requirements-ml.txt                   # scikit-learn, lightgbm or xgboost, shap, pandas, pyarrow
│   ├── notebooks/                            # EDA (outputs gitignored)
│   ├── data/                                 # gitignored (local only)
│   ├── features/
│   │   ├── make_features.py                  # builds features_daily & per-room-type views
│   │   ├── schema.py                         # Pydantic schemas for feature rows
│   │   └── event_impact.py                   # computes Impact Score (batch)
│   ├── training/
│   │   ├── train_pricing.py                  # trains per-room-type model or single multi-task model
│   │   └── eval_pricing.py                   # metrics, uplift checks, backtests
│   ├── inference/
│   │   ├── load_artifact.py                  # download + cache model from S3/R2
│   │   └── predict.py                        # pure predict(features) -> price, bounds, drivers
│   ├── pipelines/
│   │   ├── score_events.py                   # runs 4×/day → update events/impact_score
│   │   ├── hourly_refresh.py                 # recompute recs hourly (pilot cadence)
│   │   └── daily_retrain.py                  # 03:00 Europe/Dublin retrain if better
│   └── registry/
│       └── README.md                         # artifact naming & versioning scheme
├── frontend/
│   ├── ... (keep)
│   └── src/
│       ├── api/
│       │   ├── apiClient.ts                  # migrate utils/apiClient.tsx → here (already present)
│       │   └── pricing.ts                    # getQuote(), getCalendar(), exportCSV()
│       ├── app/(routes)/
│       │   ├── recommendations/page.tsx      # 14–30 day table with approve/export
│       │   └── events/page.tsx               # manual event inputs (impact guess)
│       ├── components/
│       │   ├── RecommendationTable.tsx
│       │   └── ExplainPopover.tsx
│       └── types/
│           ├── pricing.ts                    # DTOs mirror backend
│           └── events.ts
└── .github/
    └── workflows/
        ├── backend-ci.yml                    # lint, pytest
        └── frontend-ci.yml                   # typecheck, next build

```

## DS/ML stuff:

# Pilot MVP: Guestline Read‑Only + Per‑Room‑Type Pricing (updated)

## Scope alignment (confirmed)

- Guestline: read‑only ingestion (no write‑back), near real‑time via polling.
- Modeling: per‑room‑type recommendations for a single Dublin hotel.
- Add dual engines: Mock vs Actual for fast backend progress without PMS access.
- Incorporate external signals (events/news/social/flights/weather/comp rates) to react after‑hours (per shared screenshots) and emit block/max‑rate advisories.

## Data model (Neon/Postgres)

Add or keep these tables (extend `backend/app/models/schemas.sql`):

- `hotels(id, name, timezone)`
- `room_types(id, hotel_id, code, name, capacity)`
- `inventory_daily(date, hotel_id, room_type_id, rooms_total, rooms_out)`
- `bookings_daily(date, hotel_id, room_type_id, rooms_sold, adr, pickup_24h)`
- `rates_daily(date, hotel_id, room_type_id, published_rate)`
- `events_daily(date, hotel_id, impact_score, source_json)`
- `predictions(created_at, date, hotel_id, room_type_id, price_rec, price_min, price_max, drivers, input_json)`
- `model_registry(id serial, created_at, artifact_uri text, is_active boolean)`
- NEW `signals_raw(id, ts, source, payload_json)` and `signals_events(id, hotel_id, start_date, end_date, kind, score, source_ids jsonb, summary)`
- NEW `advisories(id, created_at, hotel_id, room_type_id, date, type, rationale, confidence, exported bool default false)`

## Dual pricing engines (dev vs prod)

- Define a common interface `PricingEngine` used by controllers.
- Engines:
  - `MockPricingEngine` (`backend/app/services/mock_pricing_engine.py`): deterministic seeded curves per `(room_type_code, date)` with realistic trends (DOW/seasonality), random noise; returns `PricingItem[]` + `model_version="mock:v1"`. No DB writes.
  - `ActualMLService` (current `ml_service.py`): loads trained artifact from `model_registry`, builds features from Neon, predicts with guardrails, logs batch to `predictions`.
- DI provider (in `ml_service.py` or `services/__init__.py`):
  - Env `PRICING_ENGINE_IMPL=mock|actual` controls which engine `get_pricing_engine()` returns.
  - Health endpoint shows active engine and artifact URI.

Sketch:

```python
class PricingEngine(Protocol):
    def quote(self, *, hotel_id: int, room_type_code: str, dates: list[str], as_of: str|None=None, persist: bool=True) -> tuple[list[PricingItem], str]: ...

def get_pricing_engine() -> PricingEngine:
    return MockPricingEngine() if os.getenv("PRICING_ENGINE_IMPL","mock")=="mock" else MLService()
```

## External Signals Service (beyond Guestline)

- Goal: detect demand shocks independent of PMS (e.g., Croke Park concert announced after hours) and convert to date‑window impact scores.
- `backend/app/services/signals_service.py` with plug‑in connectors (HTTP + light scraping where allowed):
  - News/events (RSS/Google News queries: Dublin, Croke Park, concerts, sports, conferences)
  - Social (X/Reddit/Facebook pages via APIs or RSS; rate‑limited)
  - Flights (flash sales/route volume proxies)
  - Weather (heatwave indices; med‑term forecasts)
  - Comp rates (small comp set public OTA pages; polite cadence and caching)
- Pipeline:

1. Fetch → store raw in `signals_raw`.

2. Normalize + dedupe → `signals_events(kind, start_date..end_date, score ∈ [0,1])`.

3. Nightly/hourly scorer writes `events_daily.impact_score` aggregates per date/hotel.

- Cadence: news/social 10–15 min; weather/flights hourly; comp rates 2–4×/day.

## Multi‑layer “Intelligent Pricing” pipeline

- Layer 0 — Data ingestion: Guestline (read), External Signals, Manual events (UI).
- Layer 1 — Demand model per room‑type (LightGBM/XGBoost): features = DOW/seasonality, lead_time buckets, occupancy & pickup deltas, event_impact, comp‑price delta, weather indices, price_yesterday, etc.
- Layer 2 — Optimizer/guardrails: price bands per room‑type; elasticity‑informed uplift/discount; pacing rules by lead‑time.
- Layer 3 — Shock handler: if `signals_events.score` high and pickup spikes after hours, apply immediate uplifts and emit advisories.
- Layer 4 — LLM assist (optional, feature‑flag): classify raw text into event types, estimate coarse uplift prior when history is absent, and generate human‑readable explanations. LLM never sets numeric price; it augments features/explanations.
- Output: recommendations + explanations + advisories.

## Advisory flow (read‑only PMS)

- Rules emit `advisories`:
  - High impact signal AND pickup spike → `type=max_rate` for affected dates/room‑types.
  - Occupancy > threshold with long lead time → `type=max_rate`.
  - Extreme shock (like instant sell‑out) → `type=suggest_stop_sell` (manager action). No automation to “invalidate cards”.
- Dashboard lists advisories with CSV export for quick action in PMS.

## Inference and scheduling

- `ml/pipelines/hourly_refresh.py`: hourly feature build → predictions per room‑type → upsert `predictions` and cache for API.
- `ml/pipelines/daily_retrain.py`: 03:00 Europe/Dublin retrain → if better, publish artifact and switch `model_registry.is_active`.
- `ml/pipelines/score_events.py`: 4×/day recompute `events_daily.impact_score` from `signals_events`.
- `backend/app/services/scheduler_service.py`: runs Guestline polling (15–60 min), signals connectors, and triggers recompute when thresholds exceeded.

## Backend API (FastAPI)

- `pricing_controller.py`
  - `POST /api/pricing/quote` (engine‑agnostic) body `{hotel_id, room_type_code, dates[]}` → items + `model_version`.
  - `GET /api/pricing/calendar?hotel_id&start&end` → aggregate predictions across room‑types.
  - `GET /api/pricing/export.csv`.
- `events_controller.py` — manual events CRUD → `events_daily`.
- `signals_controller.py` — recent signals & impacts; for debugging.
- `health_controller.py` — engine kind, artifact uri, last PMS/Signals sync, last model run.
- DTOs mirrored in `frontend/src/types/`.

## Frontend

- `src/api/pricing.ts` → `getQuote`, `getCalendar`, `exportCSV`.
- Pages: `recommendations` (table + per room‑type filters + explanations); `events` (manual add); lightweight `signals` panel.
- Status chips: “Last PMS sync”, “Last signals sync”, “Model vX” (engine aware).

## CSV bootstrap (for dev now)

- `ml/features/bootstrap_from_csv.py` to ingest `infra/foresight-data/2025 PMS.csv` and historic CSVs as hotel‑level backfill. We’ll request room‑type‑level export from Guestline; until then, allow an optional allocation mapping file to split to room‑types (pilot‑only fallback; clearly documented).

## Deployment & CI/CD

- Processes on Render:
  - API service (FastAPI) — env `PRICING_ENGINE_IMPL` controls Mock vs Actual.
  - Signals worker — connectors + scoring (APScheduler/Celery beat).
  - ML worker — hourly refresh + daily retrain + artifact publish to S3/R2.
- Neon for Postgres; S3/R2 for artifacts; Vercel for frontend.
- GitHub Actions: backend lint/pytest + frontend typecheck/build; separate staging/prod.
- Feature flags: `LLM_EXPLAINERS`, `ENABLE_SIGNALS`, `PRICING_ENGINE_IMPL`.

## Notes on the attached images

- They confirm after‑hours event announcements causing instant booking spikes and manager desire to temporarily max rate or suggest stop‑sell. The plan’s Signals Service + Advisories + Shock handler directly address this.
