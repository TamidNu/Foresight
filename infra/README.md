# Infrastructure layout (suggested)

look at the infra/ folder layout

```
tamidnu-foresight/
├── README.md
├── dev-setup.md
├── PRD.md
├── tech_README.md
├── **docs/**
│   ├── **api-contracts.md**
│   └── **ml-architecture.md**
├── **infra/**
│   ├── **render/**
│   │   ├── **web-backend.yaml**         # FastAPI service
│   │   ├── **worker-train.yaml**        # training worker
│   │   └── **cron-daily-retrain.yaml**  # cron binding → worker
│   └── **vercel/**
│       └── **vercel.json**              # (optional overrides)
├── backend/
│   ├── main.py
│   ├── requirements.txt
│   ├── .env.example
│   └── app/
│       ├── controllers/
│       │   ├── hello_controller.py
│       │   ├── **pricing_controller.py**         ← NEW
│       │   └── user_controller.py
│       ├── models/
│       │   ├── dto.py
│       │   ├── orm.py
│       │   └── **schemas.sql**                   ← NEW (Neon DDL)
│       ├── repositories/
│       │   ├── database.py
│       │   ├── user_repo.py
│       │   ├── **features_repo.py**             ← NEW
│       │   └── **model_registry_repo.py**       ← NEW
│       └── services/
│           ├── user_service.py
│           ├── **feature_builder.py**           ← NEW
│           └── **ml_service.py**                ← NEW
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
├── frontend/
│   ├── next.config.ts
│   ├── package.json
│   ├── src/
│   │   ├── **api/**                          ← KEEP, but standardize naming
│   │   │   ├── apiClient.ts
│   │   │   ├── user.ts
│   │   │   └── **pricing.ts**               ← NEW (getQuote, getRange)
│   │   ├── app/
│   │   │   ├── (routes)/
│   │   │   │   ├── recommendations/         ← NEW page (table)
│   │   │   │   │   └── page.tsx
│   │   │   │   └── events/                  ← NEW (MVP1)
│   │   │   │       └── page.tsx
│   │   ├── components/
│   │   │   ├── **RecommendationsTable.tsx** ← NEW
│   │   │   └── **ShapBadge.tsx**            ← NEW (simple “reason” chips)
│   │   ├── types/
│   │   │   └── **pricing.ts**               ← NEW (PriceQuote, etc.)
│   │   └── **lib/**
│   │       └── **date.ts**                  ← NEW (helpers)
└── .github/
    └── workflows/
        └── **lint-test.yml**                ← NEW (CI basic)

```
