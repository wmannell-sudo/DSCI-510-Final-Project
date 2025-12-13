import numpy as np

def compute_linear_trend_m_per_year(ts_df):
    df = ts_df.dropna().copy()
    if len(df) < 30:
        return np.nan, np.nan

    t0 = df["datetime"].min()
    df["time_s"] = (df["datetime"] - t0).dt.total_seconds()

    if df["time_s"].nunique() < 2:
        return np.nan, np.nan

    slope, intercept = np.polyfit(df["time_s"], df["water_level_m"], 1)
    slope_m_per_year = slope * 60 * 60 * 24 * 365
    return slope_m_per_year, intercept
