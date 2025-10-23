<!-- bb5e3ef5-7d00-4dbf-ac78-2a0c6cadc54d 5046cc53-039d-432b-afc5-00a9cbdf5edb -->

# Pilot MVP: Guestline Read‑Only + Per‑Room‑Type Pricing

## Scope alignment (confirmed)

- Guestline: read‑only ingestion (no write‑back), near real‑time via polling.
- Modeling: per‑room‑type recommendations for a single Dublin hotel.
- Add dual engines: Mock vs Actual for fast backend progress without PMS access. (DEPENDENCY INJECTION)
- Incorporate external signals (events/news/social/flights/weather/comp rates) to react after‑hours (eg: bon Jovi announced Dublin tour, hotel booked out literally less than an hour later) and emit block/max‑rate advisories.

## Data model (Neon/Postgres)

Add or keep these tables (extend `backend/app/models/schemas.sql`): -- Aside: this file isint actually being ran

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

### Frontend pages and API calls (low‑level)

1. Dashboard `/dashboard`

   - UI: KPIs tiles (Occ 7d, ADR vs Rec ADR, Active Advisories), status chips, latest advisories list.
   - Initial data fetch (SSR or client):
     - `GET /api/health`
       - Response: `{ engine: "mock"|"actual", model_uri: string, last_pms_sync: ts, last_signals_sync: ts, last_model_run: ts }`
     - `GET /api/pricing/calendar?hotel_id={id}&start={today}&end={today+7}`
       - Response: `{ items: [{ date, room_type_code, price_rec, price_min, price_max }...] }`
     - `GET /api/advisories?hotel_id={id}&start={today}&end={today+30}` (when implemented)
       - Response: `{ advisories: [{ date, room_type_code, type, rationale, confidence }] }`
   - Polling: `/api/health` every 30–60s for status chips.

2. Recommendations `/recommendations`

   - UI: Date range picker (default 30 days), room‑type filter, table/grid view with Explain popover.
   - Data flow:
     - `GET /api/pricing/calendar?hotel_id={id}&start={s}&end={e}[&room_type_code=RT]`
       - Fast path from cache; used for rendering the table.
     - On manual refresh for selected rows (or if date range is unusual):
       - `POST /api/pricing/quote` with body:
         {"hotel_id": 1, "room_type_code": "DLX-QUEEN", "dates": ["2025-11-01","2025-11-02"]}
       - Response: {"items": [{"date":"2025-11-01","room_type_code":"DLX-QUEEN","price_rec":155.0,"price_min":135.0,"price_max":195.0,"drivers":["event","pace"]}], "model_version": "mock:v1"}
     - Export:
       - `GET /api/pricing/export.csv?hotel_id={id}&start={s}&end={e}[&room_type_code=RT][&ids=...]` → `text/csv`
   - Empty/error states: if `engine=mock`, display badge “demo data”. If `/calendar` stale (`last_model_run > 60m`), show warning.

3. Events `/events`

   - UI: calendar with badges, form: {label, date range, expected impact: low|med|high}.
   - API:
     - `GET /api/events?hotel_id={id}&start={s}&end={e}` → list existing manual events, and derived `impact_score` for context.
     - `POST /api/events` body `{hotel_id, start_date, end_date, label, impact_level}` → create/update.
     - `DELETE /api/events/{id}`
   - Side effects: creating/updating triggers recompute (feature flag/queued task) and may produce advisories.

4. Signals panel `/signals` (optional)

   - UI: list of recent signals with filters (kind: news/social/flights/weather/otas), link to the source.
   - API:
     - `GET /api/signals/recent?hotel_id={id}&limit=50` → from `signals_events` joined to `signals_raw` ids.
   - Purpose: transparency; helps trust the recommendations and advisories.

5. Global pieces
   - `src/api/pricing.ts` wraps `utils/apiClient.tsx` and exposes:
     - `getCalendar(hotelId, start, end, roomTypeCode?)`
     - `getQuote(hotelId, roomTypeCode, dates)`
     - `exportCSV(hotelId, start, end, roomTypeCode?, ids?)`
   - `src/api/system.ts` for `getHealth()` and later `getAdvisories()`.
   - Types mirrored under `src/types/` to match backend DTOs (`PricingItem`, `PricingResponse`, `Advisory`).

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

## End‑to‑end product flow (RM‑only pilot)

### Who can use it

- Single role: Revenue Manager (RM) for the pilot hotel. Authenticated users land in the app; others are blocked.

### What the RM sees (frontend)

- Dashboard (default)
  - Status chips: Last PMS sync, Last Signals sync, Model version/engine (mock or actual).
  - At‑a‑glance: next 7‑day occupancy trend, current ADR vs recommended ADR, count of active advisories.
  - Advisory feed: “Max rate suggested on 2026‑08‑30 (High event impact + pickup spike)” with link to details and CSV export.
- Recommendations page
  - Calendar/table for 14–60 days ahead filtered by room type.
  - Columns: Date, Room Type, Recommended Price, Min/Max band, Explanation (popover showing top drivers), Last updated.
  - Actions: Select rows → Export CSV (for PMS import). No write‑back in pilot.
- Events page
  - Add/edit manual events (date range, label, expected impact low/med/high) to nudge model/guardrails.
  - Shows computed Impact Score per day, merged with external signals.
- Signals panel (lite, optional for pilot)
  - Recent detected signals (news/social/flights/weather/OTAs) with source links and mapped date window.

### High‑level user flow

1. RM logs in → sees Dashboard with status and any new advisories.
2. RM opens Recommendations → reviews price curve for room types → exports selected dates as CSV to apply in PMS.
3. If RM knows a special event, they add it on Events page to pre‑empt demand.
4. During shocks (e.g., gig announced after hours), Advisories appear quickly (max‑rate/stop‑sell suggestion). RM exports and acts in PMS.

### Backend data flow (step‑by‑step)

1. PMS ingestion (read‑only): Guestline poller runs every 15–60 min.
   - Pulls reservations/availability/rates per room type for the next 60 days.
   - Normalizes into Neon: `inventory_daily`, `bookings_daily`, `rates_daily` and computes `pickup_24h` deltas.
   - Updates “Last PMS sync” status.
2. External Signals connectors (independent of PMS)
   - Poll news/RSS/Google News, social, flights, weather, and comp set OTAs on their cadences.
   - Raw payloads → `signals_raw`; dedup/normalize → `signals_events (kind, start_date..end_date, score)`.
   - Scorer updates `events_daily.impact_score` per date/hotel; updates “Last Signals sync”.
3. Feature build and caching (hourly and on triggers)
   - Joins daily tables + `events_daily` to create per‑room‑type feature rows for the next 60 days (lead‑time buckets, pickup deltas, seasonality, event impact, comp deltas, weather indices, price_yesterday, etc.).
   - Keeps a small cache for the Pricing API.
4. Pricing engine selection (DI)
   - Env `PRICING_ENGINE_IMPL=mock|actual`.
   - Mock: `MockPricingEngine` produces deterministic seeded curves for stable testing.
   - Actual: `MLService` loads the active model artifact from S3/R2 via `model_registry`, predicts, applies guardrails/explanations.
5. Recompute triggers
   - Scheduled hourly; or immediately when (a) pickup delta crosses threshold, (b) new high‑impact signal arrives, (c) RM adds a manual event.
   - Writes results to `predictions` and updates cache.
6. Advisory engine (read‑only guidance)
   - Rules examine `signals_events.score`, pickup spikes, occupancy/lead‑time, and recent predictions.
   - Emits `advisories` rows: `max_rate` or `suggest_stop_sell`, with rationale and confidence.
7. API layer (FastAPI)
   - `/api/pricing/quote` → engine‑agnostic on‑demand quote for a hotel/room‑type/dates.
   - `/api/pricing/calendar` → aggregates cached predictions for range.
   - `/api/pricing/export.csv` → CSV stream of selected dates.
   - `/api/events/*` → manual event CRUD; `/api/health` → engine kind, model uri, last PMS/Signals sync, last run.
8. Frontend consumption
   - Recommendations table/calendars read from `/calendar` (fast), fall back to `/quote` for ad‑hoc ranges.
   - CSV export calls `/export.csv` with selected row IDs/dates.
   - Dashboard polls `/api/health` for status chips.

### Detailed data flow internals

- Guestline ingestion worker

  - Reads: Guestline API.
  - Writes: staging temp tables (optional) → upserts to `inventory_daily`, `bookings_daily`, `rates_daily` (composite PK `date, hotel_id, room_type_id`).
  - Computes: `pickup_24h` by diffing rolling snapshots.
  - Indexes: `(hotel_id, room_type_id, date)` on all daily tables.

- Signals connectors

  - Reads: external sources (HTTP/RSS/APIs); each payload stored in `signals_raw` with source, ts, and hash for dedupe.
  - Normalizer scorer:
    - Groups by event; maps to `start_date..end_date`; assigns `kind` and a `score ∈ [0,1]`.
    - Writes to `signals_events`; aggregates per day into `events_daily.impact_score`.

- Feature builder

  - Query joins daily tables by `(hotel_id, room_type_id, date)` for horizon `[today, +60d]`.
  - Adds engineered columns: lead_time_bucket, pace indices, moving averages, event_impact, comp_delta, weather flags.
  - Materialization options: on‑the‑fly DataFrame vs temporary materialized view (pilot keeps it simple with on‑the‑fly build + cache).

- Pricing engines

  - Mock: computes deterministic `price_rec` with DOW/seasonality multipliers + noise; returns bands.
  - Actual: loads artifact once (hot‑reloaded if `model_registry.is_active` changes), predicts row‑by‑row; post‑process applies guardrails (min/max, uplift caps, pacing).

- Caching strategy

  - After each hourly refresh, latest predictions for `[today, +60d]` are cached in memory (process cache) keyed by `(hotel_id, room_type_code)`.
  - `/calendar` serves from cache; `/quote` bypasses cache for ad‑hoc dates.
  - Cache invalidated on successful recompute or model switch.

- Advisories
  - Rule engine scans fresh predictions and recent signals to detect shock conditions.
  - Writes human‑readable `rationale` and `confidence` to `advisories`.
  - Export endpoint filters by date/room‑type for RM action in PMS.

### After‑hours shock example (from screenshots)

1. News connector detects “Croke Park concert announced”, classifies as high‑impact; maps to date window; score escalates.
2. Signals scorer updates `events_daily.impact_score` for that date; trigger fires.
3. Pricing engine recomputes immediately; Advisory engine emits `max_rate` (and possibly `suggest_stop_sell`).
4. Dashboard shows new advisory within minutes; Recommendations reflect higher prices. RM exports CSV and applies in PMS.

### Deployment‑time flow

- ML worker: hourly refresh, daily 03:00 retrain → publish artifact to `model_registry` if improved.
- API service: serves requests with current engine; hot‑reloads to new artifact on next call.
- Signals worker: runs connectors/scorer on cadence.

### Failure/degeneration modes

- PMS unreachable: show stale badge; continue serving last predictions; keep Signals/advisories active.
- Signals API rate‑limited: degrade to manual events; keep base recommendations.
- Engine = mock: UI/flows remain identical; health shows `engine=mock` and no DB writes for predictions.

### Data model quick map

- Inputs: `inventory_daily`, `bookings_daily`, `rates_daily`, `events_daily`, `signals_events`.
- ML outputs: `predictions` (per date/room‑type price), `advisories` (human actions), cached responses for UI.
- Registry: `model_registry` controls active artifact.

### To-dos

- [ ] Add MockPricingEngine and DI switch PRICING_ENGINE_IMPL
- [ ] Implement signals connectors + scoring into events_daily
- [ ] Add advisories table and emit rules + UI export
- [ ] Optional LLM classifiers/explainers behind a flag
- [ ] Guestline read-only adapter + polling scheduler
- [ ] Bootstrap Neon from foresight-data CSVs
- [ ] Per-room-type feature build + training scripts
- [ ] Model loading + predict with guardrails
- [ ] Hourly refresh, daily retrain, 4× event scoring jobs
- [ ] Finish pricing/events/signals/health controllers + DTOs
- [ ] Recommendations/events pages and status chips
- [ ] Render/Vercel deploy and GitHub Actions
