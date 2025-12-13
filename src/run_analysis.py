import os
import numpy as np
import pandas as pd


# Paths (rubric-compliant)

PROCESSED_DATA_DIR = os.path.join("data", "processed")
os.makedirs(PROCESSED_DATA_DIR, exist_ok=True)


# Trend analysis

def compute_linear_trend_m_per_year(ts_df):
    """
    Compute linear sea-level trend in meters per year
    from a water-level time series.

    Parameters:
    
    ts_df : pandas.DataFrame
        Must contain columns:
        - datetime
        - water_level_m

    Returns:
    
    slope_m_per_year : float
    intercept : float
    """
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


def build_trend_table(stations_df, timeseries_dict, days_back):
    """
    Build station-level trend table from raw time series.

    Parameters:
    
    stations_df : pandas.DataFrame
        Must contain:
        - station_id
        - station_name
        - lat
        - lon
    timeseries_dict : dict
        Mapping station_id -> DataFrame(datetime, water_level_m)
    days_back : int

    Returns:
    
    pandas.DataFrame
        Station-level trend table
    """
    records = []

    for _, row in stations_df.iterrows():
        sid = str(row["station_id"])
        ts = timeseries_dict.get(sid)

        if ts is None or ts.empty:
            continue

        slope, intercept = compute_linear_trend_m_per_year(ts)

        if np.isnan(slope):
            continue

        records.append({
            "station_id": sid,
            "station_name": row["station_name"],
            "lat": float(row["lat"]),
            "lon": float(row["lon"]),
            "trend_m_per_year": float(slope),
            "trend_intercept": float(intercept),
            "n_points": int(len(ts)),
            "days_back": int(days_back),
        })

    return pd.DataFrame(records)


def save_trend_table(df, filename="combined_ca_water_levels.csv"):
    """
    Save station-level trend table to data/processed/.
    """
    out_path = os.path.join(PROCESSED_DATA_DIR, filename)
    df.to_csv(out_path, index=False)
    return out_path


# Risk analysis

def compute_risk_score(df):
    """
    Compute normalized coastal risk score.

    Risk = normalized sea-level trend * normalized median housing value

    Parameters:
    
    df : pandas.DataFrame
        Must contain:
        - trend_m_per_year
        - MedHouseVal

    Returns:
    
    pandas.DataFrame
        With added columns:
        - trend_norm
        - house_norm
        - risk_score
    """
    df = df.copy()

    df["trend_norm"] = df["trend_m_per_year"] / df["trend_m_per_year"].max()
    df["house_norm"] = df["MedHouseVal"] / df["MedHouseVal"].max()
    df["risk_score"] = df["trend_norm"] * df["house_norm"]

    return df


def save_risk_table(df, filename="combined_risk_data.csv"):
    """
    Save final risk dataset to data/processed/.
    """
    out_path = os.path.join(PROCESSED_DATA_DIR, filename)
    df.to_csv(out_path, index=False)
    return out_path
