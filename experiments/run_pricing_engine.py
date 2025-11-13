from __future__ import annotations

import argparse
import csv
import os
from datetime import datetime
from typing import List

from pricing_engine.engine import score_dates
from pricing_engine.utils import ensure_dir, load_env


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Run experimental pricing engine and export CSV.")
    p.add_argument("--hotel-id", type=int, default=1)
    p.add_argument("--room-type", type=str, default="DLX-QUEEN")
    p.add_argument("--from", dest="from_date", type=str, required=True, help="YYYY-MM-DD")
    p.add_argument("--to", dest="to_date", type=str, required=True, help="YYYY-MM-DD")
    p.add_argument("--location", type=str, default="Dublin, Ireland", help="City, Country for events search")
    p.add_argument("--data-dir", type=str, default=os.path.abspath(os.path.join(os.getcwd(), "infra/foresight-data")))
    p.add_argument("--cache-dir", type=str, default=os.path.abspath(os.path.join(os.getcwd(), "experiments/cache")))
    p.add_argument("--out-dir", type=str, default=os.path.abspath(os.path.join(os.getcwd(), "experiments/output")))
    p.add_argument("--disable-perplexity", action="store_true", help="Disable external Perplexity calls (use cache/fallback only)")
    p.add_argument("--max-perplexity-results", type=int, default=8, help="Max results to request from Perplexity")
    p.add_argument("--force-refresh-perplexity", action="store_true", help="Ignore cache for Perplexity and refresh")
    p.add_argument("--train-model", action="store_true", help="Train ML model from --data-dir and save into --cache-dir")
    p.add_argument("--disable-ml", action="store_true", help="Disable ML model usage (heuristics only)")
    p.add_argument("--ml-weight", type=float, default=0.6, help="Weight of ML prediction in ensemble [0..1]")
    p.add_argument("--smoothing-window", type=int, default=3, help="Rolling median window size for smoothing (>=1)")
    return p.parse_args()


def main() -> None:
    # Load .env from experiments/.env if present
    load_env()
    args = parse_args()
    ensure_dir(args.cache_dir)
    ensure_dir(args.out_dir)

    # Optional: Train ML model
    if args.train_model:
        from pricing_engine.model import MLPriceModel
        model = MLPriceModel.train_from_data_dir(args.data_dir, args.cache_dir)
        if model is None:
            print("[engine] training failed or no suitable data found")
        else:
            print(f"[engine] trained ML model {model.version} and saved to {args.cache_dir}")
        # If only training was requested, exit here
        if args.from_date is None or args.to_date is None:
            return

    items, meta = score_dates(
        hotel_id=args.hotel_id,
        room_type_code=args.room_type,
        from_date=args.from_date,
        to_date=args.to_date,
        location=args.location,
        data_dir=args.data_dir,
        cache_dir=args.cache_dir,
        disable_perplexity=args.disable_perplexity,
        max_perplexity_results=args.max_perplexity_results,
        force_refresh_perplexity=args.force_refresh_perplexity,
        disable_ml=args.disable_ml,
        ml_weight=max(0.0, min(1.0, args.ml_weight)),
        smoothing_window=max(1, args.smoothing_window),
    )

    # Print a preview
    print(f"[engine] scored {meta['num_items']} days "
          f"(hotel_id={meta['hotel_id']} room_type={meta['room_type_code']} location={meta['location']})")
    for row in items[:5]:
        print(f"  {row.date}  rec={row.price_rec:.2f}  min={row.price_min:.2f}  max={row.price_max:.2f}  drivers={', '.join(row.drivers)}")
    if len(items) > 5:
        print("  ...")

    # Write CSV
    ts = datetime.now().strftime("%Y%m%d-%H%M%S")
    out_path = os.path.join(args.out_dir, f"pricing_{ts}.csv")
    with open(out_path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["date", "room_type_code", "price_rec", "price_min", "price_max", "drivers"])
        for r in items:
            w.writerow([r.date, r.room_type_code, f"{r.price_rec:.2f}", f"{r.price_min:.2f}", f"{r.price_max:.2f}", "|".join(r.drivers)])

    print(f"[engine] wrote CSV → {out_path}")
    if meta.get("sources"):
        print(f"[engine] perplexity sources ({len(meta['sources'])}):")
        for s in meta["sources"][:5]:
            print(f"  - {s.get('title','')} :: {s.get('url','')}")
        if len(meta["sources"]) > 5:
            print("  ...")


if __name__ == "__main__":
    main()


