# ML service

from __future__ import annotations

import logging
from typing import Dict, List, Optional, Tuple

from pydantic import BaseModel

from app.repositories.model_registry_repo import get_active_model_uri
from app.repositories.features_repo import fetch_features_for_dates
from app.repositories.predictions_repo import log_prediction_batch

from app.services.feature_builder import build_feature_rows
from ml.inference.load_artifact import load_model
from ml.inference.predict import predict_price

logger = logging.getLogger(__name__)


class PricingItem(BaseModel):
    date: str
    room_type_code: str
    price_rec: float
    price_min: float
    price_max: float
    drivers: List[str] = []


class MLService:
    """
    Loads/refreshes the active pricing model and exposes a quote() API for controllers.
    Keep this stateful instance in FastAPI DI (single per-process).
    """

    def __init__(self, hotel_id_default: Optional[int] = None):
        self._hotel_id_default = hotel_id_default
        self._model_uri: Optional[str] = None
        self._model = None
        self._feature_names: Optional[List[str]] = None
        self._load_active_model()

    # -------- internal helpers --------
    def _load_active_model(self) -> None:
        """Load active model from registry into memory."""
        uri = get_active_model_uri()
        if not uri:
            logger.warning("No active model found in registry.")
            self._model = None
            self._model_uri = None
            self._feature_names = None
            return

        if uri == self._model_uri and self._model is not None:
            # already loaded
            return

        logger.info("Loading model artifact: %s", uri)
        model = load_model(uri)  # implement: download & joblib.load(...)
        # optional: extract feature names from model if available
        feature_names = getattr(model, "feature_names_in_", None)
        self._model = model
        self._model_uri = uri
        self._feature_names = list(feature_names) if feature_names is not None else None
        logger.info("Model loaded (version uri=%s).", self._model_uri)

    def refresh_if_changed(self) -> None:
        """Hot-reload if a new artifact has been promoted in the registry."""
        current_uri = get_active_model_uri()
        if current_uri != self._model_uri:
            logger.info("Detected new active model. Reloading...")
            self._load_active_model()

    # -------- public API --------
    def quote(
        self,
        *,
        hotel_id: int,
        room_type_code: str,
        dates: List[str],
        as_of: Optional[str] = None,
        persist: bool = True
    ) -> Tuple[List[PricingItem], str]:
        """
        Return price recommendations for (hotel, room_type, dates).
        """
        # Ensure a model is ready
        self.refresh_if_changed()
        if self._model is None:
            raise RuntimeError("No active model is loaded. Train/publish a model first.")

        # 1) Pull base features from DB (features_daily or raw tables)
        base_df = fetch_features_for_dates(
            hotel_id=hotel_id, room_type_code=room_type_code, dates=dates, as_of=as_of
        )

        # 2) Build final feature rows expected by the model (types, defaults, derived cols)
        rows = build_feature_rows(
            base_df=base_df,
            model_feature_names=self._feature_names,
        )  # returns List[Dict[str, Any]] aligned to (date -> row)

        # 3) Predict
        items: List[PricingItem] = []
        for row in rows:
            # predict_price returns dict: {price_rec, price_min, price_max, drivers}
            out = predict_price(self._model, row)
            items.append(
                PricingItem(
                    date=row["date"],
                    room_type_code=room_type_code,
                    price_rec=float(out["price_rec"]),
                    price_min=float(out["price_min"]),
                    price_max=float(out["price_max"]),
                    drivers=list(out.get("drivers", [])),
                )
            )

        # 4) Optional: log the batch for audit/analytics
        if persist:
            try:
                log_prediction_batch(
                    hotel_id=hotel_id,
                    room_type_code=room_type_code,
                    items=[i.model_dump() for i in items],
                    model_uri=self._model_uri or "unknown",
                    inputs_df=base_df,
                )
            except Exception as e:
                logger.warning("Failed to persist predictions: %s", e)

        # return items + model version
        version = self._model_uri or "unknown"
        return items, version


# ---- FastAPI DI helper ----
_ml_service_singleton: Optional[MLService] = None

def get_ml_service() -> MLService:
    global _ml_service_singleton
    if _ml_service_singleton is None:
        _ml_service_singleton = MLService()
    return _ml_service_singleton
