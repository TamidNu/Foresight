# DS/ML readme:

```
├── **ml/**                                      ← MOVE & REPLACE `ds-ml/`
│   ├── **requirements-ml.txt**
│   ├── **data/**              (gitignored)
│   ├── **notebooks/**         (experiments only)
│   ├── **features/**
│   │   ├── **make_features.py**
│   │   └── **schema.py**
│   ├── **training/**
│   │   ├── **train_pricing.py**
│   │   └── **eval_pricing.py**
│   ├── **inference/**
│   │   ├── **load_artifact.py**
│   │   └── **predict.py**
│   ├── **pipelines/**
│   │   ├── **daily_retrain.py**
│   │   └── **batch_score.py**
│   ├── **artifacts/**          (dev only; prod → S3/R2)
│   └── **external/**
│       └── **weather/**
│           ├── **weather_pipeline.py**  ← from ds-ml/weather/weather-pipeline.py
│           └── **weather_notes.md**     ← from ds-ml/weather/weather.md
```

```
├── ml/                                      # rename ds-ml → ml
│   ├── requirements-ml.txt                   # scikit-learn, lightgbm or xgboost, shap, pandas, pyarrow
│   ├── notebooks/                            # EDA (outputs gitignored)
│   ├── data/                                 # gitignored (local only)
│   ├── features/
│   │   ├── make_features.py                  # builds features_daily & per-room-type views
│   │   ├── schema.py                         # Pydantic schemas for feature rows
│   │   └── event_impact.py                   # computes Impact Score (batch)
│   ├── training/
│   │   ├── train_pricing.py                  # trains per-room-type model or single multi-task model
│   │   └── eval_pricing.py                   # metrics, uplift checks, backtests
│   ├── inference/
│   │   ├── load_artifact.py                  # download + cache model from S3/R2
│   │   └── predict.py                        # pure predict(features) -> price, bounds, drivers
│   ├── pipelines/
│   │   ├── score_events.py                   # runs 4×/day → update events/impact_score
│   │   ├── hourly_refresh.py                 # recompute recs hourly (pilot cadence)
│   │   └── daily_retrain.py                  # 03:00 Europe/Dublin retrain if better
│   └── registry/
│       └── README.md
```
