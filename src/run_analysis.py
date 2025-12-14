#Cell 3.1: Imports and Paths

import os
import numpy as np
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"
PROCESSED_DIR = DATA_DIR / "processed"

#Cell 3.2: Load cleaned station data from clean_data.py

stations_path = os.path.join(
    PROCESSED_DATA_DIR,
    "stations_with_housing.csv"
)

stations_df = pd.read_csv(stations_path)

stations_df.head()

#Cell 4.3: Load water-level timeseries data from get_data.py

def load_timeseries_cache(timeseries_dir):
    timeseries = {}

    for fname in os.listdir(timeseries_dir):
        if not fname.endswith("_water_level.csv"):
            continue

        station_id = fname.replace("_water_level.csv", "")
        path = os.path.join(timeseries_dir, fname)

        df = pd.read_csv(path, parse_dates=["datetime"])
        timeseries[station_id] = df

    return timeseries

timeseries_dict = load_timeseries_cache(TIMESERIES_DIR)

len(timeseries_dict)

#Cell 3.4: Compute linear sea-level trend in meters/year

def compute_linear_trend_m_per_year(ts_df):
    df = ts_df.copy().dropna()

    if len(df) < 30:
        return np.nan, np.nan

    t0 = df["datetime"].min()
    df["time_s"] = (df["datetime"] - t0).dt.total_seconds()

    if df["time_s"].nunique() < 2:
        return np.nan, np.nan

    slope_m_per_s, intercept = np.polyfit(
        df["time_s"].to_numpy(),
        df["water_level_m"].to_numpy(),
        1
    )

    slope_m_per_year = slope_m_per_s * 60 * 60 * 24 * 365
    return slope_m_per_year, intercept

#Cell 3.5: Build station-level trend table

trend_records = []

for _, row in stations_df.iterrows():
    station_id = str(row["station_id"])
    ts = timeseries_dict.get(station_id)

    if ts is None or ts.empty:
        continue

    slope, intercept = compute_linear_trend_m_per_year(ts)

    if np.isnan(slope):
        continue

    trend_records.append({
        "station_id": station_id,
        "station_name": row["station_name"],
        "lat": row["lat"],
        "lon": row["lon"],
        "trend_m_per_year": slope,
        "trend_intercept": intercept,
        "MedHouseVal": row["MedHouseVal"],
        "nearest_housing_distance_deg": row["nearest_housing_distance_deg"],
        "n_points": len(ts),
    })

trend_df = pd.DataFrame(trend_records)

trend_df.head()

#Cell 3.6: Save station trend data to data/processed

trend_out = os.path.join(
    PROCESSED_DATA_DIR,
    "combined_ca_water_levels.csv"
)

trend_df.to_csv(trend_out, index=False)

trend_out

#Cell 3.7: Normalize variables and compute risk score

trend_df = trend_df.copy()

trend_df["trend_norm"] = trend_df["trend_m_per_year"] / trend_df["trend_m_per_year"].max()
trend_df["house_norm"] = trend_df["MedHouseVal"] / trend_df["MedHouseVal"].max()

trend_df["risk_score"] = trend_df["trend_norm"] * trend_df["house_norm"]

trend_df.head()

#Cell 3.8: Save final risk dataset to data/processed

risk_out = os.path.join(
    PROCESSED_DATA_DIR,
    "combined_risk_data.csv"
)

trend_df.to_csv(risk_out, index=False)

risk_out