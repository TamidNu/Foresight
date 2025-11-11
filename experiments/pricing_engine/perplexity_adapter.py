from __future__ import annotations

import os
import re
from datetime import date, datetime
from typing import Dict, List, Tuple

from perplexity import Perplexity  # requires PERPLEXITY_API_KEY in env

from .utils import cache_path, read_json, write_json, to_iso


WEEKEND_WORDS = ("concert", "festival", "match", "game", "marathon", "expo", "tournament", "cup", "show")
MONTH_NAMES = (
    "january", "february", "march", "april", "may", "june",
    "july", "august", "september", "october", "november", "december"
)
WEEKDAY_NAMES = ("monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday")


def _parse_indicators(text: str) -> Dict[str, bool]:
    t = text.lower()
    has_weekendish = any(w in t for w in WEEKEND_WORDS)
    has_month = any(m in t for m in MONTH_NAMES)
    has_weekday = any(wd in t for wd in WEEKDAY_NAMES)
    return {
        "weekendish": has_weekendish,
        "has_month": has_month,
        "has_weekday": has_weekday,
    }


def fetch_event_impacts(
    *, location: str, start: date, end: date, cache_dir: str
) -> Tuple[Dict[str, float], List[Dict[str, str]]]:
    """
    Query Perplexity for events likely to impact hotel demand, and map to a naive daily impact score in [0,1].
    Caching is applied by (location, start, end) key. Falls back gracefully to empty results if no API key.
    """
    key = {"location": location, "start": to_iso(start), "end": to_iso(end)}
    cpath = cache_path(cache_dir, key)
    cached = read_json(cpath)
    if cached:
        return cached.get("daily", {}), cached.get("sources", [])

    if not os.getenv("PERPLEXITY_API_KEY"):
        return {}, []

    client = Perplexity()
    query = f"major events in {location} between {to_iso(start)} and {to_iso(end)} that impact hotel demand"
    # Be conservative on max_results to avoid overuse; user has key in experiments/.env
    search = client.search.create(query=query, max_results=8)

    sources: List[Dict[str, str]] = []
    indicators: List[Dict[str, bool]] = []
    for r in search.results:
        # r likely has: title, url (SDK dependent). We keep what we can
        src = {"title": getattr(r, "title", "") or "", "url": getattr(r, "url", "") or ""}
        sources.append(src)
        indicators.append(_parse_indicators(src["title"]))

    # Naive mapping: if we found "weekendish" events → boost Fri/Sat/Sun slightly (0.3)
    # If month/weekday clues present → boost Fri/Sat more (0.5). Otherwise 0.
    daily: Dict[str, float] = {}
    found_weekendish = any(ind["weekendish"] for ind in indicators)
    found_rich_context = any(ind["has_month"] and ind["has_weekday"] for ind in indicators)
    current = start
    while current <= end:
        score = 0.0
        if current.weekday() in (4, 5, 6):  # Fri/Sat/Sun
            if found_rich_context:
                score = 0.5
            elif found_weekendish:
                score = 0.3
        daily[to_iso(current)] = round(score, 2)
        current = current.fromordinal(current.toordinal() + 1)

    write_json(cpath, {"daily": daily, "sources": sources})
    return daily, sources


