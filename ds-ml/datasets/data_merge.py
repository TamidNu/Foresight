import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_squared_error
from xgboost import XGBRegressor

# Load data
events = pd.read_csv("ds-ml/datasets/dublin_events.csv")
hotels = pd.read_csv("ds-ml/datasets/2025 PMS.csv")
hotels.columns = hotels.columns.str.lower()

# Merge on date
merged = hotels.merge(events, on="date", how="left")

# Target variable: next day's occupancy change
merged["target"] = merged["occ"].diff().shift(-1)

# Event-related features
merged["event_exists"] = merged["name"].notna().astype(int)
merged["event_type"] = merged["type"].fillna("None")
merged = pd.get_dummies(merged, columns=["event_type"])

# Convert date and extract time-based features
merged["date"] = pd.to_datetime(merged["date"], dayfirst=True, errors="coerce")
merged["dayofweek"] = merged["date"].dt.dayofweek
merged["month"] = merged["date"].dt.month

# Lag features
merged["occ_lag1"] = merged["occ"].shift(1)
merged["arr_lag1"] = merged["arr"].shift(1)

# Define features + target
features = [
    "event_exists", "arr", "avail", "rateplanrevenue",
    "dayofweek", "month", "occ_lag1", "arr_lag1"
] + [col for col in merged.columns if col.startswith("event_type_")]

target = "target"

# Separate numeric and categorical columns
numeric_features = ["arr", "avail", "rateplanrevenue", "dayofweek", "month", "occ_lag1", "arr_lag1"]
categorical_features = [col for col in merged.columns if col.startswith("event_type_")] + ["event_exists"]

# Fill missing values
merged[numeric_features] = merged[numeric_features].fillna(0)
merged[categorical_features] = merged[categorical_features].fillna(0)

# Scale numeric columns
scaler = StandardScaler()
merged[numeric_features] = scaler.fit_transform(merged[numeric_features])

# Prepare final dataset
X = merged[numeric_features + categorical_features]
y = merged[target].fillna(0)

# Split data
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train model
model = XGBRegressor(n_estimators=200, learning_rate=0.05, max_depth=4)
model.fit(X_train, y_train)

# Evaluate
preds = model.predict(X_test)
rmse = np.sqrt(mean_squared_error(y_test, preds))
print(f"✅ RMSE: {rmse:.4f}")