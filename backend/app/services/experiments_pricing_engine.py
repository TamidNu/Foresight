from __future__ import annotations

import sys
from pathlib import Path
from typing import List, Tuple

from app.models.dto import PricingItem as PricingItemDTO


def _import_experiments_engine():
    """
    Ensure the repo root is on sys.path, then import experiments engine lazily.
    """
    here = Path(__file__).resolve()
    # backend/app/services/ -> backend/app -> backend -> repo root
    repo_root = here.parents[3]
    if str(repo_root) not in sys.path:
        sys.path.append(str(repo_root))
    # Now import experiments modules
    from experiments.pricing_engine.engine import score_dates  # type: ignore
    return score_dates, repo_root


class ExperimentsPricingEngine:
    """
    Adapter to call experiments/pricing_engine from the backend.
    Produces backend DTOs (app.models.dto.PricingItem).
    """

    def __init__(self, version: str = "experiments-ml-v1"):
        self.version = version
        self._score_dates, self._repo_root = _import_experiments_engine()
        self._default_data_dir = str(self._repo_root / "infra" / "foresight-data")
        self._default_cache_dir = str(self._repo_root / "experiments" / "cache")

    def quote(
        self,
        *,
        hotel_id: int,
        room_type_code: str,
        start_date: str,
        end_date: str,
    ) -> Tuple[List[PricingItemDTO], str]:
        items, _meta = self._score_dates(
            hotel_id=hotel_id,
            room_type_code=room_type_code,
            from_date=start_date,
            to_date=end_date,
            location=None,  # backend path avoids external calls by default
            data_dir=self._default_data_dir,
            cache_dir=self._default_cache_dir,
            disable_perplexity=True,
            disable_ml=False,
            ml_weight=0.6,
            smoothing_window=3,
        )
        dto_items: List[PricingItemDTO] = [
            PricingItemDTO(
                date=i.date,
                room_type_code=i.room_type_code,
                price_rec=i.price_rec,
                price_min=i.price_min,
                price_max=i.price_max,
                drivers=list(i.drivers),
            )
            for i in items
        ]
        return dto_items, self.version


