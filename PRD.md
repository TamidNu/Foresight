# Foresight — Business PRD

> **Scope:** Web app for a single hotel (initially), with real‑time AI pricing recommendations and one manager user role. Tech: **Next.js** (frontend) + **FastAPI** (backend) + **MongoDB** (potential data store).

## 1) Vision & Problem

Hotels routinely leave 10–20% revenue on the table due to static or manual pricing. Revenue managers juggle spreadsheets, instincts, and delayed signals (events, pace, seasonality). Foresight delivers **revenue intelligence**: timely, transparent, and trustworthy AI price recommendations that are easy to act on.

**Primary outcome:** Increase RevPAR by surfacing the **right price at the right time** with minimal effort from the manager.

## 2) Target User & Roles

- **Hotel Manager (single role)** — Reviews/adjusts prices, inputs special dates/events, applies recommendations to PMS or exports.

## 3) Core Value Proposition

- **MVP 0**: Prove the end‑to‑end loop from historical data → AI model → daily recommendations in a clean UI.
- **MVP 1**: Make it **live**: integrate one major PMS, keep recommendations fresh, and add lightweight event/seasonality awareness.

## 4) Success Metrics (north‑star & supporting)

- **NSM:** Increase in **expected RevPAR** vs. baseline for the next 30 days (simulation/what‑if analysis).
- **Adoption:** % days with recommendations viewed; time‑to-first-recommendation (< 10 minutes from login).
- **Quality:** Manager‑rated usefulness of recs (≥ 4/5); % recs accepted/applied.
- **Reliability:** Data freshness (e.g., last sync < 60 min in MVP 1), uptime ≥ 99%.

---

## 5) MVP 0 — Requirements (3–4 months)

**Goal:** Demonstrate value with the simplest path to recommendations.

### In‑Scope Features

1. **Historical data ingestion**

   - Manager uploads CSV/XLSX following a simple template (dates, available rooms, ADR, occupancy, bookings, room type optional).
   - Basic validation and schema hints.

2. **AI price recommendations (batch)**

   - Train a lightweight model on historical data (day‑of‑week, seasonality, pace proxies).
   - Output daily **recommended rate** for the next 30–60 days (per hotel; per room type optional if data allows).
   - Show confidence/strength signal (e.g., low/med/high) and a simple reason snippet where possible.

3. **Manager UI (minimal)**

   - Secure login (single user).
   - Upload page, "Generate Recommendations" action.
   - Results: table (Date | Recommended Price | Notes). CSV export.

4. **Ops & guardrails**

   - Error handling for malformed files.
   - Basic audit log (upload time, model run time, result set ID).

### Out‑of‑Scope (MVP 0)

- Real‑time sync, automatic PMS write‑back, competitor scraping, multi‑property, multi‑user, rich analytics.

### Acceptance Criteria

- Given valid historical data, the system returns a **non‑flat** recommended price curve for the next 30+ days.
- End‑to‑end time (upload → results) under \~2 minutes on sample data.
- Exportable recommendations; UI understandable by a non‑technical manager.

---

## 6) MVP 1 — Requirements (follow‑on \~4–5 months)

**Goal:** "Always‑fresh" recommendations with one PMS integration and light event awareness.

### In‑Scope Features

1. **PMS integration (one provider)**

   - Read reservations/availability/rates via provider API (polling or webhook) on a schedule (e.g., every 15–60 min).
   - Normalize into our datastore; surface last‑sync status in UI.

2. **Real‑time(ish) recommendations**

   - Automatic recompute cadence (e.g., hourly) and/or trigger on significant pickup deltas.
   - Optional one‑click **export** (CSV) or **push** back to PMS for selected dates (push may be a stretch goal; export is in‑scope).

3. **Event & seasonality awareness (lightweight)**

   - Manager can add special events/blackout periods with expected impact (low/med/high).
   - Model or post‑processing applies uplift/guardrails for those dates.

4. **Manager UI (usable daily)**

   - Dashboard (today’s occ %, current vs. recommended ADR, 7‑day view).
   - Calendar view of recommendations; event badges; quick filters.
   - Simple explanations (e.g., "High weekend demand" / "Low midweek pickup").

5. **Ops & reliability**

   - Status page: last model run, last PMS sync, data health.
   - Basic alerting if sync fails or recommendations are stale.

### Out‑of‑Scope (MVP 1)

- Multi‑property tenants; competitor rates; channel manager/CRS; native mobile apps; advanced RL pricing.

### Acceptance Criteria

- PMS data ingests on schedule; UI shows fresh timestamp.
- Recommendations change in response to synthetic booking shocks (QA scenario).
- Manager can add an event and see uplift reflected on those dates.
- "npm run build" (frontend) and test suite (backend) pass in CI for release.

---

## 7) Constraints & Assumptions

- **Single hotel** and **single role** until post‑MVP 1.
- One major PMS integration only (depth over breadth).
- Data science remains explainable; no opaque black‑box requirements.
- Hosting on reliable cloud (separate staging/prod). Secrets managed securely.

## 8) Risks & Mitigations

- **PMS API access delays** → start integration early; use mock/test data; keep export workflow as fallback.
- **Data sparsity/quality** → include validators and templates; allow manual event input to improve signal.
- **Model trust** → ship simple explanations + guardrails (min/max rate bands), and CSV export for human review.

## 9) Go‑to‑Market for Pilot

- Target one committed pilot hotel (the dataset we have). Weekly check‑ins; gather acceptance signals (recs applied %, qualitative feedback). Create simple ROI case studies for fundraising and future sales.

---

## 10) Release Plan (indicative)

- **Month 1–2:** Data model, upload/validation, baseline model, MVP 0 UI.
- **Month 3–4:** MVP 0 polish, export, basic logging/metrics; pilot demo.
- **Month 5–6:** PMS integration scaffolding, data adapter, scheduler, dashboard/calendar.
- **Month 7–8:** Event inputs, explanations, auto refresh, reliability/alerts, pilot hardening.

---

## 11) Non‑Functional Requirements

- Security: HTTPS, least‑privilege credentials, audit of data imports/exports.
- Performance: Recommendation generation < 2s per date range after model is warm; sync jobs complete reliably within cadence.
- Observability: Logs, request IDs, job status, basic dashboards.
- Documentation: Runbooks for onboarding, model retrain, and integration keys.
