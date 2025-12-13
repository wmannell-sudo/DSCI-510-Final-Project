import pandas as pd
import numpy as np
from datetime import datetime, timedelta, timezone
from .utils import safe_get_json, ensure_float_series

def fetch_water_level_timeseries(station_id, days_back):
    end = datetime.now(timezone.utc)
    start = end - timedelta(days=days_back)

    datums_to_try = ["MSL", "MLLW", "NAVD"]
    url = "https://api.tidesandcurrents.noaa.gov/api/prod/datagetter"

    for datum in datums_to_try:
        params = {
            "product": "water_level",
            "application": "CA_Risk_Project",
            "station": station_id,
            "begin_date": start.strftime("%Y%m%d"),
            "end_date": end.strftime("%Y%m%d"),
            "datum": datum,
            "time_zone": "gmt",
            "units": "metric",
            "format": "json",
        }

        data, status, head = safe_get_json(url, params=params)
        if status != 200 or data is None or "data" not in data:
            continue

        df = pd.DataFrame(data["data"]).copy()
        if "t" not in df.columns or "v" not in df.columns:
            continue

        df["datetime"] = pd.to_datetime(df["t"], utc=True, errors="coerce")
        df["water_level_m"] = ensure_float_series(df["v"])
        df = df[["datetime", "water_level_m"]].dropna()

        if len(df) < 30:
            continue

        return df

    return None
