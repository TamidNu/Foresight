from __future__ import annotations

import json
import os
from dataclasses import dataclass
from datetime import date, datetime
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
import joblib

from .utils import ensure_dir, to_iso


MODEL_FILENAME = "pricing_model.pkl"
MODEL_META_FILENAME = "pricing_model.meta.json"


def _safe_float(v: Any) -> Optional[float]:
    try:
        if v is None or (isinstance(v, float) and np.isnan(v)):
            return None
        return float(v)
    except Exception:
        return None


def _infer_cols(df: pd.DataFrame) -> Tuple[Optional[str], Optional[str], Optional[str], Optional[str]]:
    date_col = None
    for c in df.columns:
        if str(c).strip().lower() in ("date", "day", "dt"):
            date_col = c
            break
    target_col = None
    for c in df.columns:
        lc = str(c).strip().lower()
        # expanded target synonyms: ADR/Rate/Price plus ARR/APR commonly used in PMS exports
        if lc in ("published_rate", "adr", "rate", "price", "arr", "apr"):
            target_col = c
            break
    occ_col = None
    pickup_col = None
    for c in df.columns:
        lc = str(c).strip().lower()
        if occ_col is None and lc in ("occupancy_pct", "occupancy", "occ"):
            occ_col = c
        if pickup_col is None and lc in ("pickup_24h", "pickup", "new_bookings_24h"):
            pickup_col = c
    return date_col, target_col, occ_col, pickup_col


def _month_seasonality(month: int) -> float:
    # Mild default seasonality prior if no explicit signals exist
    return {6: 10.0, 7: 15.0, 8: 10.0, 12: 5.0}.get(month, 0.0)


def build_features_for_date(
    *,
    d: date,
    published_rate: Optional[float],
    occupancy_pct: Optional[float],
    pickup_24h: Optional[float],
    event_impact: Optional[float],
) -> Dict[str, float]:
    dow = d.weekday()
    month = d.month
    is_weekend = 1.0 if dow in (4, 5) else 0.0
    pub = published_rate if (published_rate is not None and published_rate > 0) else 150.0
    occ = occupancy_pct if (occupancy_pct is not None and occupancy_pct >= 0) else 0.0
    pick = float(pickup_24h) if (pickup_24h is not None and pickup_24h >= 0) else 0.0
    ev = float(event_impact) if (event_impact is not None and event_impact >= 0) else 0.0
    seas = _month_seasonality(month)
    return {
        "dow": float(dow),
        "month": float(month),
        "is_weekend": is_weekend,
        "published_rate": float(pub),
        "occupancy_pct": float(occ),
        "pickup_24h": float(pick),
        "event_impact": float(ev),
        "seasonality_prior": float(seas),
    }


FEATURE_ORDER = [
    "dow",
    "month",
    "is_weekend",
    "published_rate",
    "occupancy_pct",
    "pickup_24h",
    "event_impact",
    "seasonality_prior",
]


@dataclass
class MLPriceModel:
    pipeline: Pipeline
    feature_order: List[str]
    version: str = "gbrt-v1"

    def predict_price(self, feature_row: Dict[str, float]) -> float:
        X = np.array([[feature_row.get(k, 0.0) for k in self.feature_order]], dtype=float)
        y = self.pipeline.predict(X)
        return float(y[0])

    def save(self, cache_dir: str) -> None:
        ensure_dir(cache_dir)
        joblib.dump(self.pipeline, os.path.join(cache_dir, MODEL_FILENAME))
        meta = {
            "feature_order": self.feature_order,
            "version": self.version,
        }
        with open(os.path.join(cache_dir, MODEL_META_FILENAME), "w", encoding="utf-8") as f:
            json.dump(meta, f, indent=2)

    @staticmethod
    def load(cache_dir: str) -> Optional["MLPriceModel"]:
        path = os.path.join(cache_dir, MODEL_FILENAME)
        meta_path = os.path.join(cache_dir, MODEL_META_FILENAME)
        if not os.path.exists(path) or not os.path.exists(meta_path):
            return None
        try:
            pipeline = joblib.load(path)
            with open(meta_path, "r", encoding="utf-8") as f:
                meta = json.load(f)
            feature_order = meta.get("feature_order", FEATURE_ORDER)
            version = meta.get("version", "gbrt-v1")
            return MLPriceModel(pipeline=pipeline, feature_order=feature_order, version=version)
        except Exception:
            return None

    @staticmethod
    def train_from_data_dir(data_dir: str, cache_dir: str) -> Optional["MLPriceModel"]:
        if not os.path.exists(data_dir):
            return None

        frames: List[pd.DataFrame] = []
        for fname in os.listdir(data_dir):
            if fname.lower().endswith(".csv") or fname.lower().endswith(".xlsx"):
                path = os.path.join(data_dir, fname)
                try:
                    df = pd.read_csv(path) if path.lower().endswith(".csv") else pd.read_excel(path)
                    frames.append(df)
                except Exception:
                    continue

        if not frames:
            return None

        df_all = pd.concat(frames, ignore_index=True)
        date_col, target_col, occ_col, pickup_col = _infer_cols(df_all)
        if not date_col or not target_col:
            return None

        rows: List[Dict[str, float]] = []
        targets: List[float] = []
        for _, row in df_all.iterrows():
            try:
                # prefer dayfirst=True for EU-style dates; fallback to default
                dts = pd.to_datetime(row[date_col], dayfirst=True, errors="coerce")
                if pd.isna(dts):
                    dts = pd.to_datetime(row[date_col], errors="coerce")
                if pd.isna(dts):
                    continue
                d = dts.date()
            except Exception:
                continue
            y = _safe_float(row[target_col])
            if y is None or y <= 0:
                continue
            occ = _safe_float(row[occ_col]) if occ_col else None
            if occ is not None and occ > 1.5:
                occ = occ / 100.0
            pickup = _safe_float(row[pickup_col]) if pickup_col else None
            feats = build_features_for_date(
                d=d,
                published_rate=y,  # using historical rate as published baseline proxy
                occupancy_pct=occ,
                pickup_24h=pickup,
                event_impact=0.0,  # historical unknown
            )
            rows.append(feats)
            targets.append(y)

        if not rows:
            return None

        X = np.array([[r[k] for k in FEATURE_ORDER] for r in rows], dtype=float)
        y = np.array(targets, dtype=float)

        # Train/val split for sanity; we won't block on poor scores, but this informs metadata
        X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=0.2, random_state=42)
        pipeline = Pipeline([
            ("scaler", StandardScaler()),
            ("gbrt", GradientBoostingRegressor(random_state=42)),
        ])
        pipeline.fit(X_tr, y_tr)
        y_pred = pipeline.predict(X_te)
        mae = float(mean_absolute_error(y_te, y_pred)) if len(y_te) > 0 else None

        model = MLPriceModel(pipeline=pipeline, feature_order=FEATURE_ORDER)
        model.save(cache_dir)

        # Save simple training metrics in meta
        try:
            meta_path = os.path.join(cache_dir, MODEL_META_FILENAME)
            with open(meta_path, "r", encoding="utf-8") as f:
                meta = json.load(f)
            meta["mae_val"] = mae
            meta["n_samples"] = int(len(y))
            with open(meta_path, "w", encoding="utf-8") as f:
                json.dump(meta, f, indent=2)
        except Exception:
            pass

        return model



