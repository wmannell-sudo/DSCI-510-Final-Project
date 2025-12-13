import numpy as np
import pandas as pd


def compute_linear_trend_m_per_year(ts_df):
    """
    Compute a linear sea-level trend (m/year) from a water-level time series.

    Parameters
    ----------
    ts_df : pandas.DataFrame
        Must contain columns:
        - datetime
        - water_level_m

    Returns
    -------
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


def build_trend_table(
    stations_df,
    fetch_water_level_timeseries,
    days_back,
    sleep_sec=0.0
):
    """
    Build a table of sea-level trends for multiple stations.

    Parameters
    ----------
    stations_df : pandas.DataFrame
        Must contain columns:
        - station_id
        - station_name
        - lat
        - lon
    fetch_water_level_timeseries : callable
        Function that fetches a water-level time series for a station
    days_back : int
        Number of days of data to use
    sleep_sec : float
        Optional delay between API calls

    Returns
    -------
    pandas.DataFrame
        Columns:
        - station_id
        - station_name
        - lat
        - lon
        - trend_m_per_year
        - trend_intercept
        - n_points
        - days_back
    """
    import time

    records = []

    for _, row in stations_df.iterrows():
        sid = str(row["station_id"])
        sname = row["station_name"]

        ts = fetch_water_level_timeseries(sid, days_back=days_back)
        time.sleep(sleep_sec)

        if ts is None or ts.empty:
            continue

        slope, intercept = compute_linear_trend_m_per_year(ts)

        if np.isnan(slope):
            continue

        records.append({
            "station_id": sid,
            "station_name": sname,
            "lat": float(row["lat"]),
            "lon": float(row["lon"]),
            "trend_m_per_year": float(slope),
            "trend_intercept": float(intercept),
            "n_points": int(len(ts)),
            "days_back": int(days_back),
        })

    return pd.DataFrame(records)


def compute_risk_score(df):
    """
    Compute a normalized coastal risk score.

    Risk = normalized sea-level trend * normalized median housing value

    Parameters
    ----------
    df : pandas.DataFrame
        Must contain columns:
        - trend_m_per_year
        - MedHouseVal

    Returns
    -------
    pandas.DataFrame
        Same DataFrame with added columns:
        - trend_norm
        - house_norm
        - risk_score
    """
    df = df.copy()

    df["trend_norm"] = df["trend_m_per_year"] / df["trend_m_per_year"].max()
    df["house_norm"] = df["MedHouseVal"] / df["MedHouseVal"].max()
    df["risk_score"] = df["trend_norm"] * df["house_norm"]

    return df
