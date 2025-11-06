from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Tuple
from datetime import datetime


SEASONALITY_MAP = {6: 10.0, 7: 15.0, 8: 10.0, 12: 5.0}


@dataclass
class PriceOutput:
    price_rec: float
    price_min: float
    price_max: float
    drivers: List[str]


def compute_price_for_date(
    *,
    date_str: str,
    room_type_code: str,
    published_rate: float | None = None,
    occupancy_pct: float | None = None,
    pickup_24h: int | None = None,
    event_impact: float | None = None,
) -> PriceOutput:
    """
    Deterministic, explainable heuristics for a single date.
    """
    d = datetime.fromisoformat(date_str).date()
    base = published_rate if published_rate and published_rate > 0 else 150.0
    drivers: List[str] = []

    dow = d.weekday()  # 0=Mon..6=Sun
    if dow in (4, 5):
        base += 20.0
        drivers.append("Weekend uplift")
    if dow in (1, 2):
        base -= 10.0
        drivers.append("Midweek softness")

    seasonality = SEASONALITY_MAP.get(d.month)
    if seasonality:
        base += seasonality
        drivers.append("Seasonality")

    if event_impact and event_impact > 0:
        delta = round(25.0 * min(1.0, max(0.0, event_impact)), 2)
        base += delta
        drivers.append("Event impact")

    if occupancy_pct and occupancy_pct > 0:
        base += min(15.0, occupancy_pct * 10.0)
        drivers.append("High occupancy")

    if pickup_24h and pickup_24h > 0:
        base += min(10.0, float(pickup_24h))
        drivers.append("High pickup")

    price_rec = round(base, 2)
    price_min = round(price_rec - 20.0, 2)
    price_max = round(price_rec + 20.0, 2)
    if price_min >= price_rec:
        price_min = round(price_rec - 10.0, 2)
    if price_max <= price_rec:
        price_max = round(price_rec + 10.0, 2)

    return PriceOutput(price_rec=price_rec, price_min=price_min, price_max=price_max, drivers=drivers)


