from __future__ import annotations

import os
import re
from datetime import date, datetime, timedelta
from typing import Dict, List, Tuple, Iterable

try:
    # requires PERPLEXITY_API_KEY in env
    from perplexity import Perplexity
except Exception:  # pragma: no cover - optional at runtime
    Perplexity = None  # type: ignore

from .utils import cache_path, read_json, write_json, to_iso


WEEKEND_WORDS = ("concert", "festival", "match", "game", "marathon", "expo", "tournament", "cup", "show", "conference")
MONTH_NAMES = (
    "january", "february", "march", "april", "may", "june",
    "july", "august", "september", "october", "november", "december"
)
WEEKDAY_NAMES = ("monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday")

# Regexes for simple date extraction from titles like:
# - "November 12-14, 2025"
# - "Nov 12, 2025"
# - "12-14 November 2025"
_MONTH_RE = r"(jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|apr(?:il)?|may|jun(?:e)?|jul(?:y)?|aug(?:ust)?|sep(?:t(?:ember)?)?|oct(?:ober)?|nov(?:ember)?|dec(?:ember)?)"
_RANGE_SEP = r"(?:-|–|—|to)"
_PATTERNS: List[re.Pattern] = [
    re.compile(rf"(?i){_MONTH_RE}\s+(\d{{1,2}})\s*,?\s*(\d{{4}})?"),  # "Nov 12, 2025" or "Nov 12"
    re.compile(rf"(?i){_MONTH_RE}\s+(\d{{1,2}})\s*{_RANGE_SEP}\s*(\d{{1,2}})\s*,?\s*(\d{{4}})?"),  # "Nov 12-14, 2025"
    re.compile(rf"(?i)(\d{{1,2}})\s*{_RANGE_SEP}\s*(\d{{1,2}})\s+{_MONTH_RE}\s*(\d{{4}})?"),  # "12-14 Nov 2025"
    re.compile(rf"(?i)(\d{{1,2}})\s+{_MONTH_RE}\s*(\d{{4}})?"),  # "12 Nov 2025" or "12 Nov"
]

_MONTH_TO_NUM = {
    "jan": 1, "january": 1,
    "feb": 2, "february": 2,
    "mar": 3, "march": 3,
    "apr": 4, "april": 4,
    "may": 5,
    "jun": 6, "june": 6,
    "jul": 7, "july": 7,
    "aug": 8, "august": 8,
    "sep": 9, "sept": 9, "september": 9,
    "oct": 10, "october": 10,
    "nov": 11, "november": 11,
    "dec": 12, "december": 12,
}


def _normalize_month(token: str) -> int | None:
    return _MONTH_TO_NUM.get(token.strip().lower())


def _clamp(d: date, start: date, end: date) -> date | None:
    if d < start or d > end:
        return None
    return d


def _iter_dates(start: date, end: date) -> Iterable[date]:
    current = start
    while current <= end:
        yield current
        current = current + timedelta(days=1)


def _extract_date_spans(text: str, default_year: int, window_start: date, window_end: date) -> List[Tuple[date, date]]:
    """
    Extract likely date spans from a text using simple regex patterns.
    Returned spans are clamped to [window_start, window_end] and filtered.
    """
    spans: List[Tuple[date, date]] = []
    t = text.strip()
    if not t:
        return spans

    for p in _PATTERNS:
        for m in p.finditer(t):
            try:
                # Pattern-dependent group interpretation
                g = [g for g in m.groups() if g is not None]
                # Try to map the match to (start_date, end_date)
                if p is _PATTERNS[0]:
                    # "<Mon> <d> [, <yyyy>]"
                    mon_raw, day_str, year_str = m.groups()
                    mon = _normalize_month(mon_raw)
                    day = int(day_str)
                    year = int(year_str) if year_str else default_year
                    d = date(year, mon or 1, day)
                    d = _clamp(d, window_start, window_end)
                    if d:
                        spans.append((d, d))
                elif p is _PATTERNS[1]:
                    # "<Mon> <d1>-<d2> [, <yyyy>]"
                    mon_raw, d1_str, d2_str, year_str = m.groups()
                    mon = _normalize_month(mon_raw)
                    d1 = int(d1_str)
                    d2 = int(d2_str)
                    year = int(year_str) if year_str else default_year
                    start_d = date(year, mon or 1, min(d1, d2))
                    end_d = date(year, mon or 1, max(d1, d2))
                    start_d = _clamp(start_d, window_start, window_end)
                    end_d = _clamp(end_d, window_start, window_end)
                    if start_d and end_d:
                        spans.append((start_d, end_d))
                elif p is _PATTERNS[2]:
                    # "<d1>-<d2> <Mon> [<yyyy>]"
                    d1_str, d2_str, mon_raw, year_str = m.groups()
                    mon = _normalize_month(mon_raw)
                    d1 = int(d1_str)
                    d2 = int(d2_str)
                    year = int(year_str) if year_str else default_year
                    start_d = date(year, mon or 1, min(d1, d2))
                    end_d = date(year, mon or 1, max(d1, d2))
                    start_d = _clamp(start_d, window_start, window_end)
                    end_d = _clamp(end_d, window_start, window_end)
                    if start_d and end_d:
                        spans.append((start_d, end_d))
                else:
                    # "<d> <Mon> [<yyyy>]"
                    day_str, mon_raw, year_str = m.groups()
                    mon = _normalize_month(mon_raw)
                    day = int(day_str)
                    year = int(year_str) if year_str else default_year
                    d = date(year, mon or 1, day)
                    d = _clamp(d, window_start, window_end)
                    if d:
                        spans.append((d, d))
            except Exception:
                # Ignore parsing errors for any particular match
                continue

    # Merge overlapping/adjacent spans
    if not spans:
        return spans
    spans.sort(key=lambda s: (s[0], s[1]))
    merged: List[Tuple[date, date]] = []
    cur_s, cur_e = spans[0]
    for s, e in spans[1:]:
        if s <= (cur_e + timedelta(days=1)):
            cur_e = max(cur_e, e)
        else:
            merged.append((cur_s, cur_e))
            cur_s, cur_e = s, e
    merged.append((cur_s, cur_e))
    return merged


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
    *,
    location: str,
    start: date,
    end: date,
    cache_dir: str,
    max_results: int = 8,
    disable_external: bool = False,
    force_refresh: bool = False,
) -> Tuple[Dict[str, float], List[Dict[str, str]]]:
    """
    Query Perplexity for events likely to impact hotel demand, and map to a daily impact score in [0,1].
    Improvements over previous version:
      - Safe import and graceful fallback if SDK or API key is missing
      - Basic extraction of explicit date spans from result titles
      - Prefer explicit dates (score≈0.6–0.8) over generic weekend boosts (0.3–0.5)
      - Caching keyed by (location, start, end, max_results)
    """
    key = {
        "location": location,
        "start": to_iso(start),
        "end": to_iso(end),
        "max_results": max_results,
    }
    cpath = cache_path(cache_dir, key)
    if not force_refresh:
        cached = read_json(cpath)
        if cached:
            return cached.get("daily", {}), cached.get("sources", [])

    if disable_external or (Perplexity is None) or (not os.getenv("PERPLEXITY_API_KEY")):
        return {}, []

    sources: List[Dict[str, str]] = []
    try:
        client = Perplexity()
        query = f"major public events in {location} between {to_iso(start)} and {to_iso(end)} that could increase hotel demand"
        search = client.search.create(query=query, max_results=max_results)
        for r in getattr(search, "results", []) or []:
            title = getattr(r, "title", "") or ""
            url = getattr(r, "url", "") or ""
            sources.append({"title": title, "url": url})
    except Exception:
        # On any API or SDK error, fall back to empty signals
        return {}, []

    # Build impacts with preference for explicit date spans in titles
    daily: Dict[str, float] = {to_iso(d): 0.0 for d in _iter_dates(start, end)}

    # 1) Explicit spans → stronger signals (0.6–0.8)
    for src in sources:
        spans = _extract_date_spans(src.get("title", ""), default_year=start.year, window_start=start, window_end=end)
        for s, e in spans:
            for d in _iter_dates(s, e):
                # stack multiple events but clamp to 0.9
                key_iso = to_iso(d)
                daily[key_iso] = min(0.9, round(daily[key_iso] + 0.3, 2))

    # 2) If no explicit spans found at all, fall back to weekend-ish signals
    if all(v == 0.0 for v in daily.values()):
        indicators = [_parse_indicators(src.get("title", "")) for src in sources]
        found_weekendish = any(ind["weekendish"] for ind in indicators)
        found_rich_context = any(ind["has_month"] and ind["has_weekday"] for ind in indicators)
        for d in _iter_dates(start, end):
            iso = to_iso(d)
            if d.weekday() in (4, 5, 6):  # Fri/Sat/Sun
                if found_rich_context:
                    daily[iso] = 0.5
                elif found_weekendish:
                    daily[iso] = 0.3

    daily = {k: round(v, 2) for k, v in daily.items()}
    write_json(cpath, {"daily": daily, "sources": sources})
    return daily, sources


