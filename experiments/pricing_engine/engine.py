from __future__ import annotations

import os
from dataclasses import asdict, dataclass
from datetime import date, datetime
from typing import Dict, List, Tuple

import pandas as pd  # for optional baseline rate ingestion

from .heuristics import PriceOutput, compute_price_for_date
from .perplexity_adapter import fetch_event_impacts
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


def score_dates(
    *,
    hotel_id: int,
    room_type_code: str,
    from_date: str,
    to_date: str,
    location: str | None,
    data_dir: str,
    cache_dir: str,
) -> Tuple[List[PricingItem], Dict]:
    """
    Score a date range using baseline rates (if any), Perplexity-derived event impact (if any), and heuristics.
    Returns (items, metadata).
    """
    start = datetime.fromisoformat(from_date).date()
    end = datetime.fromisoformat(to_date).date()

    # Load baseline rates (ADR/published) if present
    baseline = _try_load_baseline_rates(data_dir) if data_dir else {}

    # Fetch external event impact
    impacts: Dict[str, float] = {}
    sources: List[Dict[str, str]] = []
    if location:
        impacts, sources = fetch_event_impacts(location=location, start=start, end=end, cache_dir=cache_dir)

    items: List[PricingItem] = []
    for d in daterange(start, end):
        iso = to_iso(d)
        published_rate = baseline.get(iso)
        event_impact = impacts.get(iso, 0.0)
        out: PriceOutput = compute_price_for_date(
            date_str=iso,
            room_type_code=room_type_code,
            published_rate=published_rate,
            occupancy_pct=None,
            pickup_24h=None,
            event_impact=event_impact,
        )
        items.append(
            PricingItem(
                date=iso,
                room_type_code=room_type_code,
                price_rec=out.price_rec,
                price_min=out.price_min,
                price_max=out.price_max,
                drivers=out.drivers,
            )
        )

    meta = {
        "hotel_id": hotel_id,
        "room_type_code": room_type_code,
        "from": from_date,
        "to": to_date,
        "location": location,
        "num_items": len(items),
        "baseline_days": len(baseline),
        "sources": sources,
    }
    return items, meta


