from __future__ import annotations

import os
from dataclasses import asdict, dataclass
from datetime import date, datetime
from typing import Dict, List, Tuple

import pandas as pd  # for optional baseline rate ingestion

from .heuristics import PriceOutput, compute_price_for_date
from .perplexity_adapter import fetch_event_impacts
from .model import MLPriceModel, build_features_for_date
from .utils import daterange, ensure_dir, to_iso


@dataclass
class PricingItem:
    date: str
    room_type_code: str
    price_rec: float
    price_min: float
    price_max: float
    drivers: List[str]


def _try_load_baseline_rates(data_dir: str) -> Dict[str, float]:
    """
    Try to load published rates / ADR from provided data files to serve as baseline per-date rates.
    Accepts CSV/XLSX where columns may include: date, published_rate, adr, rate.
    Returns a mapping: YYYY-MM-DD -> float
    """
    mapping: Dict[str, float] = {}
    if not os.path.exists(data_dir):
        return mapping

    # search for candidate files
    candidates: List[str] = []
    for fname in os.listdir(data_dir):
        if fname.lower().endswith(".csv") or fname.lower().endswith(".xlsx"):
            candidates.append(os.path.join(data_dir, fname))

    def normalize_df(df: pd.DataFrame) -> Dict[str, float]:
        col_date = None
        for c in df.columns:
            if str(c).strip().lower() in ("date", "day", "dt"):
                col_date = c
                break
        if col_date is None:
            return {}
        col_rate = None
        for c in df.columns:
            lc = str(c).strip().lower()
            if lc in ("published_rate", "adr", "rate", "price"):
                col_rate = c
                break
        if col_rate is None:
            return {}
        out: Dict[str, float] = {}
        for _, row in df.iterrows():
            try:
                d = pd.to_datetime(row[col_date]).date()
                r = float(row[col_rate])
                if r > 0:
                    out[to_iso(d)] = r
            except Exception:
                continue
        return out

    for path in candidates:
        try:
            if path.lower().endswith(".csv"):
                df = pd.read_csv(path)
            else:
                df = pd.read_excel(path)
            mapping.update(normalize_df(df))
        except Exception:
            continue

    return mapping


def _try_load_operational_metrics(data_dir: str) -> Dict[str, Dict[str, float]]:
    """
    Optionally load operational metrics like occupancy_pct and pickup_24h from CSV/XLSX files.
    We scan for columns:
      - date column: one of {date, day, dt}
      - occupancy column: one of {occupancy_pct, occupancy, occ}
      - pickup column: one of {pickup_24h, pickup, new_bookings_24h}
    Returns mapping: YYYY-MM-DD -> { 'occupancy_pct': float|None, 'pickup_24h': float|None }
    """
    metrics: Dict[str, Dict[str, float]] = {}
    if not os.path.exists(data_dir):
        return metrics

    candidates: List[str] = []
    for fname in os.listdir(data_dir):
        if fname.lower().endswith(".csv") or fname.lower().endswith(".xlsx"):
            candidates.append(os.path.join(data_dir, fname))

    def normalize_df(df: pd.DataFrame) -> None:
        date_col = None
        for c in df.columns:
            if str(c).strip().lower() in ("date", "day", "dt"):
                date_col = c
                break
        if date_col is None:
            return
        occ_col = None
        pickup_col = None
        for c in df.columns:
            lc = str(c).strip().lower()
            if occ_col is None and lc in ("occupancy_pct", "occupancy", "occ"):
                occ_col = c
            if pickup_col is None and lc in ("pickup_24h", "pickup", "new_bookings_24h"):
                pickup_col = c
        if not occ_col and not pickup_col:
            return
        for _, row in df.iterrows():
            try:
                dts = pd.to_datetime(row[date_col], dayfirst=True, errors="coerce")
                if pd.isna(dts):
                    dts = pd.to_datetime(row[date_col], errors="coerce")
                if pd.isna(dts):
                    continue
                d = dts.date()
            except Exception:
                continue
            key = to_iso(d)
            occ_val = None
            pick_val = None
            try:
                if occ_col:
                    v = float(row[occ_col])
                    # Normalize occupancy: if given like 85 instead of 0.85, convert
                    occ_val = v / 100.0 if v > 1.5 else v
            except Exception:
                pass
            try:
                if pickup_col:
                    pick_val = float(row[pickup_col])
            except Exception:
                pass
            if occ_val is None and pick_val is None:
                continue
            cur = metrics.get(key, {})
            if occ_val is not None:
                cur["occupancy_pct"] = occ_val
            if pick_val is not None:
                cur["pickup_24h"] = pick_val
            metrics[key] = cur

    for path in candidates:
        try:
            if path.lower().endswith(".csv"):
                df = pd.read_csv(path)
            else:
                df = pd.read_excel(path)
            normalize_df(df)
        except Exception:
            continue

    return metrics


def score_dates(
    *,
    hotel_id: int,
    room_type_code: str,
    from_date: str,
    to_date: str,
    location: str | None,
    data_dir: str,
    cache_dir: str,
    disable_perplexity: bool = False,
    max_perplexity_results: int = 8,
    force_refresh_perplexity: bool = False,
    disable_ml: bool = False,
    ml_weight: float = 0.6,
    smoothing_window: int = 3,
) -> Tuple[List[PricingItem], Dict]:
    """
    Score a date range using baseline rates (if any), Perplexity-derived event impact (if any), and heuristics.
    Returns (items, metadata).
    """
    start = datetime.fromisoformat(from_date).date()
    end = datetime.fromisoformat(to_date).date()

    # Load baseline rates (ADR/published) if present
    baseline = _try_load_baseline_rates(data_dir) if data_dir else {}
    # Load optional operational metrics (occupancy & pickup)
    metrics = _try_load_operational_metrics(data_dir) if data_dir else {}

    # Fetch external event impact
    impacts: Dict[str, float] = {}
    sources: List[Dict[str, str]] = []
    if location:
        impacts, sources = fetch_event_impacts(
            location=location,
            start=start,
            end=end,
            cache_dir=cache_dir,
            max_results=max_perplexity_results,
            disable_external=disable_perplexity,
            force_refresh=force_refresh_perplexity,
        )

    # Load ML model if enabled
    ml_model: MLPriceModel | None = None
    if not disable_ml:
        ml_model = MLPriceModel.load(cache_dir)

    items: List[PricingItem] = []
    recs_for_smoothing: List[float] = []
    for d in daterange(start, end):
        iso = to_iso(d)
        published_rate = baseline.get(iso)
        event_impact = impacts.get(iso, 0.0)
        occ = None
        pick = None
        if iso in metrics:
            occ = metrics[iso].get("occupancy_pct")
            pick = metrics[iso].get("pickup_24h")
        heur_out: PriceOutput = compute_price_for_date(
            date_str=iso,
            room_type_code=room_type_code,
            published_rate=published_rate,
            occupancy_pct=occ,
            pickup_24h=pick,
            event_impact=event_impact,
        )
        price_rec = heur_out.price_rec
        drivers = list(heur_out.drivers)

        # ML inference and ensemble
        if ml_model is not None:
            feats = build_features_for_date(
                d=d,
                published_rate=published_rate if published_rate else heur_out.price_rec,
                occupancy_pct=occ,
                pickup_24h=pick,
                event_impact=event_impact,
            )
            try:
                ml_price = ml_model.predict_price(feats)
                price_rec = round(float(ml_weight) * ml_price + (1.0 - float(ml_weight)) * heur_out.price_rec, 2)
                drivers.append("ML model")
            except Exception:
                pass

        # Guardrails based on heuristic band (slightly expanded)
        guard_min = max(0.0, heur_out.price_min * 0.9)
        guard_max = heur_out.price_max * 1.1
        if price_rec < guard_min:
            price_rec = round(guard_min, 2)
            drivers.append("Guardrail min")
        elif price_rec > guard_max:
            price_rec = round(guard_max, 2)
            drivers.append("Guardrail max")

        price_min = round(max(0.0, price_rec - 20.0), 2)
        price_max = round(price_rec + 20.0, 2)

        items.append(PricingItem(
            date=iso,
            room_type_code=room_type_code,
            price_rec=price_rec,
            price_min=price_min,
            price_max=price_max,
            drivers=drivers,
        ))
        recs_for_smoothing.append(price_rec)

    # Rolling-median smoothing
    if smoothing_window and smoothing_window > 1 and len(items) >= smoothing_window:
        k = int(smoothing_window)
        half = k // 2
        for i in range(len(items)):
            lo = max(0, i - half)
            hi = min(len(items), i + half + 1)
            window_vals = [r.price_rec for r in items[lo:hi]]
            window_vals.sort()
            med = window_vals[len(window_vals) // 2]
            blended = round(0.5 * items[i].price_rec + 0.5 * float(med), 2)
            if abs(blended - items[i].price_rec) >= 0.01:
                items[i].price_rec = blended
                items[i].price_min = round(max(0.0, blended - 20.0), 2)
                items[i].price_max = round(blended + 20.0, 2)
                items[i].drivers.append("Smoothing")

    meta = {
        "hotel_id": hotel_id,
        "room_type_code": room_type_code,
        "from": from_date,
        "to": to_date,
        "location": location,
        "num_items": len(items),
        "baseline_days": len(baseline),
        "metrics_days": len(metrics),
        "sources": sources,
        "disable_perplexity": disable_perplexity,
        "max_perplexity_results": max_perplexity_results,
        "ml_loaded": bool(ml_model is not None),
        "ml_weight": ml_weight,
        "smoothing_window": smoothing_window,
    }
    return items, meta


