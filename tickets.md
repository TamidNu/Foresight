## Backend Ticket: Implement Mock Pricing API (MVP 0) and Wire It Up

### Summary

- Implement a mock pricing endpoint that returns deterministic-but-plausible price recommendations for a given date range and room type.
- Define request/response DTOs, finish the mock pricing engine, expose `POST /api/pricing/quote`, and register the router.
- Fix CORS origins and ensure DB tables are created at startup (or via migration) so user signup remains reliable.

### Why Now

- This unblocks the Dashboard to show an end-to-end recommendation flow for MVP 0 without waiting on the real model.

### Acceptance Criteria

- `POST /api/pricing/quote` returns JSON with fields: `items[]` (one per date) and `modelVersion`.
- Each pricing item includes: `date`, `room_type_code`, `price_rec`, `price_min`, `price_max`, `drivers[]`.
- Returns 200 for valid inputs; returns 422 for invalid payloads.
- CORS allows the frontend (`http://localhost:3000`) and staging/prod domains.
- Backend is reachable locally on `http://localhost:8000` and the route appears in `/docs`.

### API Contract

- Method: `POST /api/pricing/quote`
- Body:

```json
{
  "hotel_id": 1,
  "room_type_code": "DLX-QUEEN",
  "from": "2025-11-10",
  "to": "2025-12-10"
}
```

- Response (200):

```json
{
  "items": [
    {
      "date": "2025-11-10",
      "room_type_code": "DLX-QUEEN",
      "price_rec": 179.0,
      "price_min": 159.0,
      "price_max": 199.0,
      "drivers": ["Weekend uplift", "Seasonality"]
    }
  ],
  "modelVersion": "mock-v1"
}
```

### Files to Touch

- `backend/app/controllers/pricing_controller.py` (implement routes)
- `backend/app/services/mock_pricing_engine.py` (complete engine logic)
- `backend/app/models/dto.py` (add pricing request/response DTOs)
- `backend/main.py` (register pricing router, fix CORS)
- Optional: `backend/app/repositories/database.py` or `backend/main.py` startup hook to create tables, or add Alembic.
- `infra/docs/api-contracts.md` (document final contract)

### Detailed Implementation Plan

1. Define DTOs

   - Add to `backend/app/models/dto.py`:
     - `class PricingRequest(BaseModel): hotel_id: int; room_type_code: str; from: date; to: date`
     - `class PricingItem(BaseModel): date: str; room_type_code: str; price_rec: float; price_min: float; price_max: float; drivers: List[str] = []`
     - `class PricingResponse(BaseModel): items: List[PricingItem]; modelVersion: str`

   Example (Python):

```python
from datetime import date, timedelta
from typing import List
from pydantic import BaseModel

class PricingRequest(BaseModel):
    hotel_id: int
    room_type_code: str
    from_: date  # use from_ to avoid Python keyword
    to: date

class PricingItem(BaseModel):
    date: str
    room_type_code: str
    price_rec: float
    price_min: float
    price_max: float
    drivers: List[str] = []

class PricingResponse(BaseModel):
    items: List[PricingItem]
    modelVersion: str
```

2. Complete `MockPricingEngine`

   - Implement a simple deterministic function based on Day-of-Week and a small seasonality curve:
     - Base = 150
     - Weekend uplift (+20) for Friday/Saturday; midweek slight dip (-10) for Tuesday/Wednesday
     - Seasonal factor = `+5 * sin(month)` (or a simple monthly map)
     - `price_min = price_rec - 20`, `price_max = price_rec + 20`
     - `drivers` includes strings like `"Weekend uplift"`, `"Midweek softness"`, `"Seasonality"` when applicable
   - Version string: `mock-v1`.

   Example (Python):

```python
from datetime import datetime, timedelta
from typing import List

class MockPricingEngine:
    def __init__(self, version: str = "mock-v1"):
        self.version = version

    def quote(self, *, hotel_id: int, room_type_code: str, start_date: str, end_date: str) -> tuple[list[PricingItem], str]:
        start = datetime.fromisoformat(start_date)
        end = datetime.fromisoformat(end_date)
        items: List[PricingItem] = []
        cursor = start
        while cursor <= end:
            dow = cursor.weekday()  # 0=Mon..6=Sun
            month = cursor.month
            base = 150.0
            drivers: List[str] = []
            # weekend uplift
            if dow in (4, 5):
                base += 20.0
                drivers.append("Weekend uplift")
            # midweek softness
            if dow in (1, 2):
                base -= 10.0
                drivers.append("Midweek softness")
            # simple monthly seasonality map
            seasonality_map = {6: 10, 7: 15, 8: 10, 12: 5}
            if month in seasonality_map:
                base += seasonality_map[month]
                drivers.append("Seasonality")
            price_rec = round(base, 2)
            price_min = round(price_rec - 20, 2)
            price_max = round(price_rec + 20, 2)
            items.append(PricingItem(
                date=cursor.date().isoformat(),
                room_type_code=room_type_code,
                price_rec=price_rec,
                price_min=price_min,
                price_max=price_max,
                drivers=drivers,
            ))
            cursor += timedelta(days=1)
        return items, self.version
```

3. Implement Controller and Router

   - In `backend/app/controllers/pricing_controller.py`:
     - Create router: `router = APIRouter(prefix="/pricing", tags=["pricing"])`
     - Implement `@router.post("/quote", response_model=PricingResponse)`
     - Validate `from <= to` and max range (e.g., 90 days) → return 422 if invalid.
     - Call `MockPricingEngine().quote(...)` and map to DTO.

   Example (Python):

```python
from fastapi import APIRouter, HTTPException
from datetime import timedelta
from app.models.dto import PricingRequest, PricingResponse, PricingItem
from app.services.mock_pricing_engine import MockPricingEngine

router = APIRouter(prefix="/pricing", tags=["pricing"])

@router.post("/quote", response_model=PricingResponse)
def quote(req: PricingRequest) -> PricingResponse:
    if req.from_ > req.to:
        raise HTTPException(status_code=422, detail="from must be <= to")
    if (req.to - req.from_).days > 90:
        raise HTTPException(status_code=422, detail="Range too large; max 90 days")
    engine = MockPricingEngine()
    items, version = engine.quote(
        hotel_id=req.hotel_id,
        room_type_code=req.room_type_code,
        start_date=req.from_.isoformat(),
        end_date=req.to.isoformat(),
    )
    return PricingResponse(items=items, modelVersion=version)
```

4. Register Router and Fix CORS

   - In `backend/main.py`:
     - Change CORS origin to `allow_origins=["http://localhost:3000"]` (no trailing slash) and include staging/prod domains when ready.
     - Import and include pricing router under the existing `api` prefix: `api.include_router(pricing_router)`.

5. Ensure DB Tables Exist (Users)

   - Minimal: call `Base.metadata.create_all(bind=engine)` on startup so `Users` table exists locally.
   - Preferred: introduce Alembic migrations and document `alembic upgrade head`.

6. Update API Docs
   - Update `infra/docs/api-contracts.md` with request/response schema above and any constraints (max range 90 days, required fields).

### Local Run and Test

- Install deps: `pip install -r backend/requirements.txt`
- Start server:

```bash
cd backend
python -m uvicorn main:app --reload
```

- Health checks:

  - `GET http://localhost:8000/hello`
  - `GET http://localhost:8000/api/db-info`
  - Swagger: `http://localhost:8000/docs`

- Quote example:

```bash
curl -X POST \
  http://localhost:8000/api/pricing/quote \
  -H "Content-Type: application/json" \
  -d '{
    "hotel_id": 1,
    "room_type_code": "DLX-QUEEN",
    "from": "2025-11-10",
    "to": "2025-11-20"
  }'
```

### Out of Scope (for this ticket)

- Real ML model loading and feature stores.
- PMS integration.
- Authentication/authorization on pricing endpoints.

### Resources

- FastAPI Tutorial: [https://fastapi.tiangolo.com/tutorial/](https://fastapi.tiangolo.com/tutorial/)
- Pydantic Models: [https://docs.pydantic.dev/latest/](https://docs.pydantic.dev/latest/)
- SQLAlchemy ORM: [https://docs.sqlalchemy.org/en/20/orm/](https://docs.sqlalchemy.org/en/20/orm/)

### Definition of Done

- Endpoint implemented, validated, and appears in Swagger.
- Manual curl test returns a non-empty `items` list.
- CORS fixed; frontend can call the endpoint locally.
- API contracts doc updated.

---

## Frontend Ticket: Render Pricing Recommendations on Dashboard + CSV Export

### Summary

- Call the new mock pricing API from the dashboard and render a recommendations table.
- Add CSV export, types, and basic error handling. Move user signup network call into a service.

### Why Now

- Demonstrates MVP 0 end-to-end value: users can log in and immediately see pricing recommendations for the next 30 days.

### Acceptance Criteria

- On `/dashboard`, after user is authenticated, the page fetches `POST /api/pricing/quote` for a default room type and date range (today → +30 days).
- A table renders: Date, Recommended Price, Min, Max, Notes.
- “Export CSV” button downloads the current table data as a CSV.
- Errors show a non-intrusive inline alert; loading state is shown while fetching.
- User signup call is moved to a service function and handles 201/409 gracefully.

### Files to Touch

- `frontend/src/services/pricingService.ts` (new)
- `frontend/src/types/pricing.ts` (new)
- `frontend/src/app/(routes)/dashboard/page.tsx` (fetch + render table + export)
- `frontend/src/services/userService.tsx` (implement `signup`)
- Optional: `frontend/src/utils/apiClient.tsx` (use base URL from env, add simple error wrappers)

### Types and Service Layer

1. Types

```typescript
// src/types/pricing.ts
export type PricingItem = {
  date: string;
  room_type_code: string;
  price_rec: number;
  price_min: number;
  price_max: number;
  drivers: string[];
};

export type PricingResponse = {
  items: PricingItem[];
  modelVersion: string;
};
```

2. Pricing Service

```typescript
// src/services/pricingService.ts
import { request } from "../utils/apiClient";
import type { PricingResponse } from "../types/pricing";

type QuoteParams = {
  hotel_id: number;
  room_type_code: string;
  from: string; // YYYY-MM-DD
  to: string; // YYYY-MM-DD
};

export async function quote(params: QuoteParams): Promise<PricingResponse> {
  return request("/api/pricing/quote", {
    method: "POST",
    body: JSON.stringify(params),
  });
}
```

3. User Service

```typescript
// src/services/userService.tsx
type SignupPayload = {
  clerk_user_id: string;
  first_name: string;
  last_name: string;
  email: string;
};

export async function signup(payload: SignupPayload): Promise<Response> {
  return fetch("http://localhost:8000/api/users/signup", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
}
```

### Dashboard Integration

- In `dashboard/page.tsx`:
  - Compute `from = today`, `to = today + 30 days`.
  - Call `quote({ hotel_id: 1, room_type_code: "DLX-QUEEN", from, to })` on server side (preferred) or in a server action.
  - Render a table with columns: Date | Rec | Min | Max | Notes (drivers joined by `, `).
  - Add an “Export CSV” button that converts current rows to CSV and triggers a client-side download.

Example fetch usage (server component):

```typescript
import { quote } from "../../../services/pricingService";

const today = new Date();
const to = new Date();
to.setDate(today.getDate() + 30);
const fmt = (d: Date) => d.toISOString().slice(0, 10);

const data = await quote({
  hotel_id: 1,
  room_type_code: "DLX-QUEEN",
  from: fmt(today),
  to: fmt(to),
});
```

CSV export helper (client):

```typescript
export function downloadCsv(filename: string, rows: any[]) {
  const header = Object.keys(rows[0] ?? {}).join(",");
  const body = rows.map((r) => Object.values(r).join(",")).join("\n");
  const csv = `${header}\n${body}`;
  const blob = new Blob([csv], { type: "text/csv;charset=utf-8;" });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.setAttribute("download", filename);
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  URL.revokeObjectURL(url);
}
```

### Error Handling & States

- Loading: show a skeleton or spinner while the request is in-flight.
- Error: inline message (e.g., “Couldn’t load recommendations. Please try again.”) and log to console in dev.
- Empty state: show a brief message if `items.length === 0`.

### Environment & Config

- Use `NEXT_PUBLIC_API_BASE_URL` (default to `http://localhost:8000`) in `apiClient.tsx`. Example:

```typescript
const BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";
```

### Local Run and Test

- Start the backend first (ensure pricing endpoint is live).
- Start the frontend: `npm run dev`.
- Visit `/dashboard` while signed in via Clerk.
- Confirm the table renders 30 rows; “Export CSV” downloads a file containing the same rows.

### Out of Scope (for this ticket)

- Calendar visualization, filters, or pagination.
- Styling polish beyond basic readability.
- Persisting user-selected room types.

### Resources

- Next.js App Router Data Fetching: [https://nextjs.org/docs/app/building-your-application/data-fetching/fetching](https://nextjs.org/docs/app/building-your-application/data-fetching/fetching)
- Clerk for Next.js: [https://clerk.com/docs/quickstarts/nextjs](https://clerk.com/docs/quickstarts/nextjs)
- TypeScript Handbook: [https://www.typescriptlang.org/docs/](https://www.typescriptlang.org/docs/)

### Definition of Done

- Dashboard shows recommendations for the next 30 days.
- CSV export works and contains displayed rows.
- Network errors handled gracefully; no unhandled promise rejections in console.
- Code compiles with `npm run build`.

## AI/ML/DS Ticket: Baseline Pricing Engine v0 (Perplexity + LLM + Heuristics)

### Summary

- Build a minimal but real pricing engine that combines:
  - Simple, explainable heuristics on top of historical features (day-of-week, seasonality, optional occupancy/pickup proxies).
  - External signals via the Perplexity Search API to derive a daily event impact score.
  - An optional LLM summarizer to produce short human-readable reasons.
- Package it under `ml/` with clean function boundaries so the backend can later call it via `MLService` or a thin adapter.
- Must run locally without external keys (falls back to heuristics and templated reasons).

### Why Now

- Unblocks an initial “real” engine beyond a pure mock while keeping scope tractable. Establishes extensible interfaces for future model swaps (XGBoost/LightGBM), PMS-fed features, and richer signals.

### Acceptance Criteria

- `ml/` package exists and is importable from backend (local dev path is fine).
- `ml/inference/predict.py` exposes `predict_price(features: dict) -> { price_rec, price_min, price_max, drivers }`.
- A batch function `score_dates(hotel_id, room_type_code, dates)` returns a list of items with non-flat prices, weekend uplift, and reasonable bounds.
- Perplexity adapter can fetch events for a location and date range, map them into a per-day `impact_score` in [0, 1], and cache responses locally. If `PERPLEXITY_API_KEY` is missing, returns empty events gracefully.
- LLM summarizer produces a ≤ 160 char reason string from drivers if `OPENAI_API_KEY` is set; otherwise, returns a deterministic templated string.
- Unit tests cover: weekend uplift, month seasonality, bounding, and adapter fallbacks.

### Proposed Directory Structure

```
ml/
  requirements-ml.txt
  __init__.py
  features/
    __init__.py
    schema.py                # Pydantic schemas for feature rows
    make_features.py         # placeholder to compute features from raw (later)
  inference/
    __init__.py
    predict.py               # baseline heuristics + optional signals
  external/
    __init__.py
    perplexity_adapter.py    # search → normalized events per day + caching
    llm_reasoner.py          # optional OpenAI call; templated fallback
  utils/
    __init__.py
    dates.py                 # date helpers
    caching.py               # simple file cache
  cache/                     # gitignored JSON cache files
  artifacts/                 # future model files (gitignored)
```

### Detailed Implementation Plan

1. Create `ml/requirements-ml.txt`
   - Contents (pin reasonably):

```text
pandas>=2.1
numpy>=1.26
pydantic>=2.7
python-dotenv>=1.0
requests>=2.32
perplexityai>=0.17.0
openai>=1.0.0
```

2. Define feature schemas (`ml/features/schema.py`)

```python
from pydantic import BaseModel, Field

class FeatureRow(BaseModel):
    date: str                 # YYYY-MM-DD
    hotel_id: int
    room_type_code: str
    published_rate: float | None = None  # if provided (e.g., from PMS)
    occupancy_pct: float | None = None   # 0..1 if available
    pickup_24h: int | None = None        # new bookings in last 24h
    month: int | None = None
    dow: int | None = None               # 0=Mon..6=Sun
    event_impact: float | None = None    # 0..1 (filled by adapter)
```

3. Perplexity adapter (`ml/external/perplexity_adapter.py`)

- Responsibility: given `(location: str, from: str, to: str)`, return a dict mapping `date -> impact_score` and a list of raw sources.
- Strategy:
  - Query Perplexity with: `"events in {location} between {from} and {to} that impact hotel demand"`.
  - `max_results=5..10`, extract dates if present, otherwise heuristically map to nearest relevant days.
  - Score each result (e.g., concerts/sports: 0.6–0.9; conferences: 0.3–0.6) and clamp to [0, 1].
  - Cache JSON responses under `ml/cache/perplexity_{hash}.json` keyed by `(location, from, to)`.
  - If `PERPLEXITY_API_KEY` is missing or request fails, return empty mapping and empty sources.

Example shape:

```python
{
  "daily": {"2025-11-12": 0.7, "2025-11-13": 0.4},
  "sources": [{"title": "Taylor Swift @ Aviva Stadium", "url": "https://...", "date": "2025-11-12"}]
}
```

4. LLM reasoner (`ml/external/llm_reasoner.py`)

- Input: `drivers: list[str]`, `date`, optional extra context (event title snippets).
- Output: short reason (≤160 chars). If `OPENAI_API_KEY` missing, fallback to `", ".join(drivers)` with a prefix like `"Drivers: ..."`.

5. Baseline heuristics (`ml/inference/predict.py`)

- Rules:
  - Start with `base = published_rate if provided else 150.0`.
  - Weekend uplift: +20 for Fri/Sat (dow 4/5).
  - Midweek softness: -10 for Tue/Wed (dow 1/2).
  - Seasonality: monthly map `{6: +10, 7: +15, 8: +10, 12: +5}`.
  - Event impact: `base += round(25 * event_impact, 2)` if provided.
  - Occupancy/pickup (if available): `base += min(15, (occupancy_pct or 0)*10 + min(10, (pickup_24h or 0)))`.
  - Bounds: `price_min = base - 20`, `price_max = base + 20` (then round 2 decimals; ensure min < rec < max by adjusting if needed).
  - Drivers: collect labels for each adjustment applied (e.g., `"Weekend uplift"`, `"Seasonality"`, `"High pickup"`, `"Event impact"`).

API:

```python
from typing import Dict
from ml.features.schema import FeatureRow

def predict_price(model: object | None, row: Dict) -> Dict:
    # model is reserved for future use; ignored in v0
    f = FeatureRow(**row)
    # compute base using rules above → return dict with keys:
    # price_rec, price_min, price_max, drivers
```

6. Batch scoring helper

```python
from typing import List, Tuple
from datetime import date, timedelta

def score_dates(*, hotel_id: int, room_type_code: str, from_date: str, to_date: str, location: str | None = None) -> Tuple[list[dict], dict]:
    # Build feature rows for each date
    # If location provided and PERPLEXITY_API_KEY available → fetch daily impact
    # Call predict_price for each row
    # Return (items, metadata) where metadata contains sources and parameters
```

7. Caching utilities (`ml/utils/caching.py`)

- Minimal JSON read/write with file lock to avoid corruption.
- Hash key: `sha1(json.dumps(params, sort_keys=True))`.

8. Tests

- Add lightweight unit tests (pytest) for:
  - Weekend uplift on a known Friday vs Wednesday.
  - Seasonality bumps in July.
  - Bounds always 40 wide centered around rec ±20.
  - Perplexity adapter fallback without key.

### Optional (Stretch)

- Provide a thin adapter in `backend/app/services/ml_service.py` that, if `USE_ML_BASELINE=true`, proxies `quote()` to `ml.inference.predict.score_dates` for now. Keep it behind a flag; default continues to mock.

### Environment Variables

- `PERPLEXITY_API_KEY` — required to fetch events; otherwise adapter no-ops.
- `OPENAI_API_KEY` — required for LLM reasons; otherwise templated reasons.
- `USE_ML_BASELINE` — optional boolean to toggle backend to this engine later.

### Local Run and Manual Test

```bash
# 1) Install DS deps
pip install -r ml/requirements-ml.txt

# 2) Quick check (Python REPL)
from ml.inference.predict import score_dates
items, meta = score_dates(hotel_id=1, room_type_code="DLX-QUEEN", from_date="2025-11-10", to_date="2025-11-20", location="Dublin, Ireland")
len(items), items[0], list(meta.keys())
```

### Out of Scope (for this ticket)

- True model training, feature stores, or PMS ingestion.
- Persistence of predictions or integration into API routes (covered by separate backend ticket).
- Advanced explanations (SHAP, feature importances).

### Risks & Mitigations

- API rate limits or missing keys → design graceful fallbacks and caching.
- Event date extraction ambiguity → start with manual date fields from results; extend with light NLP later.
- Noisy heuristics → keep drivers explicit and explainable; will be replaced by a trained model.

### Resources

- Perplexity Python SDK: [Perplexity on PyPI](https://pypi.org/project/perplexityai/)
- Perplexity API overview: [Perplexity Docs](https://docs.perplexity.ai/)
- OpenAI API (for reasons): [OpenAI Docs](https://platform.openai.com/docs/)
- Pydantic v2: [Pydantic Docs](https://docs.pydantic.dev/latest/)

### Definition of Done

- `ml/` package created with modules listed above.
- `score_dates` returns valid items for a 10-day range with non-flat prices and sensible drivers.
- Perplexity and LLM integration works when keys set; otherwise code falls back without errors.
- Unit tests for heuristics and adapter fallback pass locally.
