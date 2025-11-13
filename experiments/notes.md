## Experimental Pricing Engine — Step-by-Step Notes

# Commands:

train model:
`python run_pricing_engine.py --train-model --data-dir infra/foresight-data --cache-dir experiments/cache --from 2025-11-10 --to 2025-11-25`#

score with ML enabled:

```python
python run_pricing_engine.py \
  --from 2025-11-10 --to 2025-11-25 \
  --location "Dublin, Ireland" \
  --ml-weight 0.6 --smoothing-window 3
```

This document explains exactly what happens when you run the experimental pricing engine in the `experiments/` directory: how environment variables are loaded, how the engine reads optional baseline rates from `infra/foresight-data`, how it calls the Perplexity Search API for event signals, how heuristics compute recommendations, where results are cached/written, and how to run and troubleshoot.

### 1) Where the code lives

- Engine entrypoint (CLI): `experiments/run_pricing_engine.py`
- Core modules:
  - `experiments/pricing_engine/engine.py` — orchestrates the full scoring pipeline
  - `experiments/pricing_engine/perplexity_adapter.py` — pulls event signals from Perplexity
  - `experiments/pricing_engine/heuristics.py` — deterministic, explainable pricing rules
  - `experiments/pricing_engine/utils.py` — env loading, dates, simple JSON caching
- Outputs:
  - CSV: `experiments/output/pricing_<timestamp>.csv`
  - Cache: JSON files under `experiments/cache/` (can be pruned safely)

### 2) One-time setup

1. Install Python deps for experiments (keep separate from backend env if you prefer):

```bash
pip install -r experiments/requirements-experiments.txt
```

2. Put your Perplexity API key in `experiments/.env`:

```bash
PERPLEXITY_API_KEY=sk-...your-key...
```

No Perplexity key? The engine still runs; it just skips the external event impact and uses heuristics only.

### 3) Running the engine (CLI)

From the repository root (recommended to avoid nested paths):

```bash
python experiments/run_pricing_engine.py \
  --hotel-id 1 \
  --room-type "DLX-QUEEN" \
  --from 2025-11-10 \
  --to 2025-11-25 \
  --location "Dublin, Ireland" \
  --max-perplexity-results 8 \
  --disable-perplexity    # optional flag; omit to enable
```

Useful flags:

- `--data-dir` (default: `<repo>/infra/foresight-data`) — where baseline rate/ADR files may exist
- `--cache-dir` (default: `<repo>/experiments/cache`)
- `--out-dir` (default: `<repo>/experiments/output`)
- `--disable-perplexity` — disable external Perplexity calls (uses cache/fallback only)
- `--max-perplexity-results` — cap Perplexity results fetched
- `--force-refresh-perplexity` — ignore cache and refresh Perplexity results
- `--train-model` — train ML model from `--data-dir` and save to cache
- `--disable-ml` — run without ML (heuristics only)
- `--ml-weight` — ensemble weight for ML prediction in [0..1] (default 0.6)
- `--smoothing-window` — rolling median window for smoothing (default 3)

Tip: If you run the script from inside `experiments/` as your working directory, the default `--cache-dir` will become `experiments/experiments/cache`. Pass an absolute `--cache-dir` (or run from repo root) to keep paths clean.

### 4) Step-by-step flow

1. Load environment

- `utils.load_env()` looks for `experiments/.env` (next to this code) and loads it if present.
- If `PERPLEXITY_API_KEY` is set, the Perplexity adapter will call the API; otherwise it returns empty signals.

2. Parse CLI args

- The CLI expects: `--hotel-id`, `--room-type`, `--from`, `--to`. Optional: `--location`, `--data-dir`, `--cache-dir`, `--out-dir`.

3. Orchestration — `engine.score_dates(...)`

- Validates the date range and converts to Python `date` objects.
- Loads baseline rates (optional) from `--data-dir` using `_try_load_baseline_rates()`:
  - Scans `.csv` and `.xlsx` files under the directory.
  - Tries to find a date column: one of `date`, `day`, or `dt` (case-insensitive).
  - Tries to find a rate column: one of `published_rate`, `adr`, `rate`, or `price`.
  - Builds a dictionary: `YYYY-MM-DD → baseline rate (float)`.
- Loads operational metrics (optional) using `_try_load_operational_metrics()`:
  - Looks for `occupancy_pct`/`occupancy`/`occ` and `pickup_24h`/`pickup` columns alongside a date column.
  - Normalizes occupancy values like `85` to `0.85`; builds `YYYY-MM-DD → {occupancy_pct, pickup_24h}`.
- Fetches external event impact using `perplexity_adapter.fetch_event_impacts()`:
  - Builds a cache key from `(location, from, to)` and checks `--cache-dir` for a JSON cache file.
  - If cached: returns the cached daily scores and sources.
  - If not cached and `PERPLEXITY_API_KEY` is set (and not `--disable-perplexity`):
    - Calls Perplexity Search with a query like “major events in {city} between {from} and {to} that impact hotel demand”.
    - Extracts explicit date spans from result titles when possible (e.g., “Nov 12–14”), assigning stronger signals to those exact days (stackable, capped).
    - Falls back to weekend boosts if no explicit spans are found.
    - Saves `{ daily: {date: score}, sources: [{title,url}, ...] }` to cache.
  - If not cached and no key: returns empty signals.

4. Heuristics per day — `heuristics.compute_price_for_date(...)`

- Inputs: `date`, `room_type_code`, optional `published_rate` (from baseline), `event_impact` (from Perplexity), `occupancy_pct` and `pickup_24h` (not provided yet, reserved for future PMS integration).
- Rules (all additive adjustments on top of `base`):
  - Base = `published_rate` if available and > 0 else 150.0
  - Weekend uplift: +20 for Friday/Saturday
  - Midweek softness: -10 for Tuesday/Wednesday
  - Seasonality: +10 (Jun), +15 (Jul), +10 (Aug), +5 (Dec)
  - Event impact: + up to 25 × `event_impact` (0..1)
  - Occupancy uplift for high occupancy (≥0.8), and softening when ≤0.3
  - Non-linear, capped pickup contribution
  - Bounds: `price_min = rec - 20`, `price_max = rec + 20`
- Returns:
  - `price_rec`, `price_min`, `price_max`
  - `drivers`: an array of human-readable strings that explain which factors applied (Weekend uplift, Seasonality, Event impact, etc.)

5. ML model — `pricing_engine.model.MLPriceModel`

- Train: `python experiments/run_pricing_engine.py --train-model --data-dir infra/foresight-data`
- Data ingestion:
  - Flexible detection of columns for `date`, target (`published_rate`/`adr`/`rate`/`price`), optional `occupancy` and `pickup`.
  - Uses GradientBoostingRegressor with scaling; saves to `experiments/cache/pricing_model.pkl`.
- Inference:
  - If a model exists and not `--disable-ml`, the engine ensembles ML and heuristics (`--ml-weight`).
  - Guardrails clamp outputs to a slightly expanded heuristic band.
  - Rolling-median smoothing ensures calendar consistency (`--smoothing-window`).

5. Build results and metadata

- Results list contains one item per date:
  - `{date, room_type_code, price_rec, price_min, price_max, drivers[]}`
- Metadata includes the parameters, number of items, how many baseline days were found, and up to the first few Perplexity source entries.
  - Also includes `metrics_days`, `disable_perplexity`, and `max_perplexity_results`.
  - Also includes `ml_loaded`, `ml_weight`, and `smoothing_window`.

6. Output

- Console preview: prints the first 5 scored rows and a summary of Perplexity sources.
- CSV: writes to `--out-dir` (default `experiments/output/`) with name `pricing_<timestamp>.csv`.
  - Headers: `date, room_type_code, price_rec, price_min, price_max, drivers`
  - Drivers are pipe-delimited in the CSV (e.g., `Weekend uplift|Seasonality`).

### 5) Example output snippet

```
[engine] scored 16 days (hotel_id=1 room_type=DLX-QUEEN location=Dublin, Ireland)
  2025-11-10  rec=150.00  min=130.00  max=170.00  drivers=
  2025-11-11  rec=140.00  min=120.00  max=160.00  drivers=Midweek softness
  2025-11-14  rec=170.00  min=150.00  max=190.00  drivers=Weekend uplift
  ...
[engine] wrote CSV → experiments/output/pricing_20251106-181148.csv
[engine] perplexity sources (3):
  - Taylor Swift at Aviva Stadium :: https://...
  - Dublin Marathon 2025 :: https://...
  - ...
```

### 6) Troubleshooting

- “No module named perplexity”: `pip install -r experiments/requirements-experiments.txt`.
- Perplexity key not found: create `experiments/.env` with `PERPLEXITY_API_KEY=...`. Without it, the run still completes (no event boost).
- No CSV generated: ensure `--out-dir` is writable; script creates it if missing.
- Paths look like `experiments/experiments/cache`: you likely ran the script from inside `experiments/`. Either run from repo root or pass an absolute `--cache-dir`/`--out-dir`.
- Baseline rates not detected: check your data files have a date column named `date`/`day`/`dt` and a rate column named `published_rate`/`adr`/`rate`/`price`. If not, the engine falls back to base=150.

### 7) How to extend next

- Better event mapping: parse dates from event titles and map to specific days instead of generic weekend boosts.
- Add PMS features: `occupancy_pct`, `pickup_24h`, `published_rate` per room type from live sources.
- Replace heuristics with a trained model, keeping the same `predict_price(row)->{price_rec,min,max,drivers}` interface.
- Add an LLM “reasoner” to compress drivers and key signals into a short reason string for the UI.

### 8) Quick reference: core functions

- CLI → `experiments/run_pricing_engine.py` (argument parsing, printing, CSV writing)
- Orchestration → `pricing_engine.engine.score_dates(...)`
- External signals → `pricing_engine.perplexity_adapter.fetch_event_impacts(...)`
- Price computation → `pricing_engine.heuristics.compute_price_for_date(...)`
- Helpers → `pricing_engine.utils.*` (env load, caching, dates)
