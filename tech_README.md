# Foresight — Engineering Guide (MVP 0 & MVP 1)

> **Stack:** **Next.js** (frontend) + **FastAPI** (backend) + **MongoDB** (potential, via Motor) + **Python ML**.
> Tone: beginner‑friendly, pragmatic, and shippable.

---

## Section A — For **All Devs**

### A1. Git/GitHub Flow

- **Main branches:** `main` (deployable), `dev` (integration). Feature work on short‑lived branches: `feat/<scope>`, `fix/<scope>`, `chore/<scope>`.
- **Flow:** create branch → commit early/often → open **draft PR** → get review → squash‑merge. Keep PRs small (< \~300 lines where possible for backend, more is acceptable for frontend since code tends to be more verbose. ). Link issues.
- **support systems**: Reach out to Naman, Adit, Jeff or Rishi without hesitating if you get stuck on anything.
- **Commit messages:** descriptive messages, scope tag: `feat(pricing): <description of feature you worked on>`.
- **Reviews:** At least **1 approval** to merge for bigger changes. Address comments or open follow‑ups. CHeck the tc-f2025-github-bot slack chanel often, since it contains good info (comments on PRs, or if any new issues are assigned to you)
- **CI basics:** PR must pass tests/linters; frontend `npm run build` should succeed locally **before** pushing. This is to avoid any deployment failures, and to ensure smooth sailing!

**Pull Requests & Projects**

- Use PR templates (checklist: tests, docs, screenshots).
- Track work in our GitHub Project board: **[https://github.com/orgs/TamidNu/projects/1](https://github.com/orgs/TamidNu/projects/1)** (link issues/PRs to items; keep status updated).

### A2. Issues & Project Hygiene

- Use milestones for MVP 0 / MVP 1. Convert comments to tasks (`- [ ]`) to create a clear checklist. And make sure to check it off. It is always a good idea to reply to an issue you are assigned on github with your action plan to complete it.

### A3. Tooling & Resources

- **Prettier (VSCode/Cursor):** install the "Prettier – Code formatter" extension, enable **Format on Save**, and add a project `.prettierrc`.

  - VSCode Marketplace → search **Prettier – Code formatter** (publisher: `esbenp`) and click **Install**.

- **Cursor (AI editor):** Students at Northeastern often have **free Cursor Pro** — go to **cursor.com/students**, sign in with your `.edu` email, and claim access. Use it for AI‑assisted refactors and test generation.
- **Postman:** Desktop app for crafting, saving, and sharing API requests & collections. Great for exploring FastAPI endpoints, env vars, and mocks. Create a shared **Foresight** workspace/collection for endpoints.
- **Docs to keep open:** Next.js docs, FastAPI docs, MongoDB/Motor, scikit‑learn/pandas. (Links in Resources per section.)

---

## Section B — Frontend (Next.js)

- whever you have a chance pls generate a cool logo using chatgpt or an online logo generator.

### B1. Expectations

- **Build must pass**: run `npm run build` **before pushing / opening a PR**. Fix type errors and lint issues locally.
- Prefer **Server Components**/**server routes** for data fetching, and keep client components lean.
- **No direct API calls** inside random `useEffect`s. Centralize calls in **services** to keep components declarative/testable.

### B2. Suggested Folder Structure

```
frontend        # Next.js app
  src/app/                 # App Router (recommended)
    (routes)/          # Route groups by feature
      dashboard/
        page.tsx
      recommendations/
        page.tsx
      events/
        page.tsx
    api/               # Route handlers (server only)
  components/          # Reusable UI components
    charts/
    tables/
    forms/
  services/            # API client wrappers (fetch/axios)
    http.ts            # base client (fetch with interceptors)
    pricing.service.ts # functions: getRecommendations(), exportCSV()
    events.service.ts
  lib/                 # utils (date, currency, guards)
  hooks/               # custom hooks (UI state only)
  styles/              # global styles
  types/               # shared TypeScript types
  test/                # component tests
```

DO MORE RESEARCH ON FRONTEND ARCHITECTURE FOR YOURSELF. Great way to learn!

**Notes:**

- `services/*` should be the **only** place that knows backend URLs and request shapes.
- Components stay "dumb" (props in, events out). Keep business logic out of UI.
- Add loading & error boundaries around pages.

### B3. Patterns

- Use **Zod** for client‑side schema validation when needed.
- Prefer **async server actions** / route handlers for operations that shouldn’t run on the client.

### B4. Resources

- Next.js App Router & data fetching (SSR/SSG/ISR), routing/linking.
- Testing: Playwright (e2e) or React Testing Library for components.

---

## Section C — Data Science / AI

### C1. Scope for MVPs

- consult with jeff for a more detailed analysis of resources and what we need to do.
- **MVP 0:** Train a lightweight model on historical data to output next 30–60 days’ recommended ADR. Focus on day‑of‑week patterns, seasonality proxies, and simple pickup features (if present in the upload).
- **MVP 1:** Add near real‑time refresh (scheduled), PMS‑fed on‑the‑books data, and **event uplift** (manager inputs). Keep models explainable and fast to infer.

### C2. Working Environment

```
services/ml/
  notebooks/           # EDA, feature trials (kept out of prod image)
  models/              # saved artifacts (.pkl, metadata.json)
  src/
    features/          # transforms (calendar, lag features)
    models/            # train.py, predict.py, baselines
    eval/              # backtests, KPI calculators
    utils/             # IO, logging, config
  jobs/
    retrain.py         # scheduled job (cron/celery)
```

- this is just proposed by Naman, who does not know much about data science. Please consult JEFF!

### C3. Recommended Stack

- **Data wrangling:** pandas, numpy.
- **Modeling:** scikit‑learn (linear models/GBMs), XGBoost/LightGBM as needed.
- **Time‑series:** lightweight Prophet/ETS for occupancy/ADR baselines (optional); simple calendar features often suffice early.
- **Explainability:** feature importances, SHAP (optional), and **human‑readable reasons** (weekend uplift, event uplift, pacing).
- **Pipelines:** keep pure‑Python functions with typed signatures; save model + version. Inference must be **idempotent** & quick (< 200ms/date).
- **Scheduling:** cron or Celery worker (backed by Redis) to run retrains/refreshes.

### C4. External Signals (MVP 1)

- **Events:** Start manual inputs; apply uplift factors. Consider simple public calendars later.
- **Seasonality:** calendar features (month, DOW, holidays).

### C5. Hosting & Ops

- Package inference as a **module** imported by FastAPI (hot‑loaded at startup).
- Store artifacts under `models/` with metadata (`model_version`, `trained_at`, `schema_hash`).
- Add a health endpoint returning model status and last refresh.

### C6. DS Resources

- Pandas & scikit‑learn tutorials; time‑series primers; lightweight web scraping (Requests/BeautifulSoup/Playwright) for future enrichment; sentiment (VADER/HF Transformers) if we later explore event buzz.

---

## Section D — Backend (FastAPI + MongoDB)

### D1. Architecture (Suggested. Madhav update this documentation when you know eactly what you want to go with. this is just a suggestion i generated with chat. )

- **Pattern:** Resource‑oriented services with clear layers. Keep **business logic** out of route handlers.

```
services/api/
  app/
    main.py            # FastAPI init, routers include
    deps.py            # DI helpers (db, auth)
    config.py          # settings (Pydantic BaseSettings)
    api/
      routes/
        pricing.py     # GET /pricing, POST /recompute
        events.py      # CRUD events
        health.py      # liveness/readiness
      schemas/
        pricing.py     # Pydantic models (Request/Response)
        events.py
      services/
        pricing_service.py  # orchestrates inference
        events_service.py
      repositories/
        pricing_repo.py # Mongo/SQL adapters
        events_repo.py
    core/
      logger.py        # struct logging
      scheduler.py     # APScheduler/Celery trigger jobs
    models/            # ODM/ORM models if needed
    tests/             # pytest
```

### D2. Data Layer

- **MongoDB** (optional for MVPs): use **Motor** (async) client or look into Atlas. NOT SURE now. TODO actionable plan for DB strategy. ; collections: `bookings`, `calendar`, `events`, `recommendations`, `runs`.
- Alternatively, start with a simple Postgres/SQLite if team prefers SQL; keep repositories swappable.

### D3. API Contracts (suggested)

- `GET /pricing?from=YYYY-MM-DD&to=YYYY-MM-DD` → array of `{date, recRate, reason, conf}`.
- `POST /pricing/recompute` → triggers refresh (async job ID).
- `POST /events` / `GET /events` → manager‑added events.
- `GET /status` → last sync time, last model run, model version.

### D4. Infra & DevEx

- **Run:** `uvicorn app.main:app --reload`. For prod: `gunicorn -k uvicorn.workers.UvicornWorker`.
- **Config:** `.env` with `MONGO_URI`, `PMS_API_KEY`, etc.; never commit secrets. Use `BaseSettings` to load.
- **Testing:** pytest + httpx test client. Seed small fixtures.
- **Docs:** FastAPI auto‑docs at `/docs` and `/redoc`.

### D5. Backend Resources

- FastAPI docs & tutorials; Motor/Mongo docs; Postman for API exploration; patterns for background tasks (Celery/Redis or APScheduler).

---

## Team Rituals & Quality Bar

- **Standups:** async in Slack/GitHub issues.
- **Weekly demo:** show something clickable or an API returning real data.
- **Definition of Done:** tests pass, `npm run build` passes, docs updated, PR reviewed/merged, issue closed.
- **Ship mindset:** Thin slices, frequent releases, always leave the branch greener.

## Onboarding Checklist

- Clone repos, install Node, Python, and MongoDB (if used).
- Install Prettier & enable Format on Save.
- Get Postman and join the shared workspace.
- Access the GitHub Project board and pick a **good‑first‑issue**.
- Run the example: start FastAPI locally, hit it from Next.js via a service, and render dummy recommendations.

> Let’s build revenue intelligence that feels **obvious** to use and **impossible** to ignore. (this is a good line for the landing page btw)
