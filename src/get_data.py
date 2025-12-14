#Cell 1.1: Imports
import os
import time
import requests
import pandas as pd
from datetime import datetime, timedelta, timezone

#Cell 1.2: Setup Directory and Configure Timeseries
RAW_DATA_DIR = os.path.join("data", "raw")
TIMESERIES_DIR = os.path.join(RAW_DATA_DIR, "timeseries_cache")

os.makedirs(RAW_DATA_DIR, exist_ok=True)
os.makedirs(TIMESERIES_DIR, exist_ok=True)

DAYS_BACK = 30
SLEEP_BETWEEN_STATIONS_SEC = 0.2

#Cell 1.3: Utility for this section
def safe_get_json(url, params=None, timeout=20):
    try:
        r = requests.get(url, params=params, timeout=timeout)
        status = r.status_code
        text_head = (r.text or "")[:200]
        try:
            return r.json(), status, text_head
        except Exception:
            return None, status, text_head
    except Exception as e:
        return None, None, str(e)[:200]


def ensure_float_series(s):
    return pd.to_numeric(s, errors="coerce")

#Cell 1.4: Defines function to fetch NOAA California station metadata (API)
def fetch_noaa_ca_station_metadata():
    url = "https://api.tidesandcurrents.noaa.gov/mdapi/prod/webapi/stations.json"
    params = {
        "expand": "details,products,latlon",
        "type": "waterlevels"
    }

    data, status, head = safe_get_json(url, params=params)

    # If API fails, return empty so fallback is used
    if data is None or "stations" not in data:
        return pd.DataFrame(columns=["station_id", "station_name", "lat", "lon"])

    df = pd.DataFrame(data["stations"]).copy()

    # Normalize ID and name
    rename_map = {}
    if "id" in df.columns:
        rename_map["id"] = "station_id"
    if "name" in df.columns:
        rename_map["name"] = "station_name"

    df = df.rename(columns=rename_map)

    # ---- LATITUDE ----
    lat_col = None
    for c in ["lat", "latitude", "lat_dd", "lt"]:
        if c in df.columns:
            lat_col = c
            break

    # ---- LONGITUDE ----
    lon_col = None
    for c in ["lon", "lng", "longitude", "lon_dd", "ln"]:
        if c in df.columns:
            lon_col = c
            break

    # If either coordinate is missing, bail out safely
    if lat_col is None or lon_col is None:
        return pd.DataFrame(columns=["station_id", "station_name", "lat", "lon"])

    # Rename to standard names
    df = df.rename(columns={lat_col: "lat", lon_col: "lon"})

    # Optional state filter
    if "state" in df.columns:
        df = df[df["state"] == "CA"].copy()

    # Convert types safely
    df["lat"] = ensure_float_series(df["lat"])
    df["lon"] = ensure_float_series(df["lon"])

    # Drop rows without valid coordinates
    df = df.dropna(subset=["station_id", "station_name", "lat", "lon"])

    return df[["station_id", "station_name", "lat", "lon"]].reset_index(drop=True)

#Cell 1.5: Creates Fallback station list in case of API mistake
def fallback_ca_station_list():
    return pd.DataFrame([
        {"station_id": "9410170", "station_name": "San Diego", "lat": 32.7142, "lon": -117.1736},
        {"station_id": "9410230", "station_name": "La Jolla", "lat": 32.8669, "lon": -117.2571},
        {"station_id": "9410660", "station_name": "Los Angeles", "lat": 33.7197, "lon": -118.2722},
        {"station_id": "9410840", "station_name": "Santa Monica", "lat": 34.0083, "lon": -118.5000},
        {"station_id": "9411340", "station_name": "Santa Barbara", "lat": 34.4033, "lon": -119.6920},
        {"station_id": "9412110", "station_name": "Port San Luis", "lat": 35.1683, "lon": -120.7540},
        {"station_id": "9413450", "station_name": "Monterey", "lat": 36.6050, "lon": -121.8883},
        {"station_id": "9414290", "station_name": "San Francisco", "lat": 37.8063, "lon": -122.4659},
        {"station_id": "9416841", "station_name": "Arena Cove", "lat": 38.9140, "lon": -123.7110},
        {"station_id": "9418767", "station_name": "North Spit", "lat": 40.7667, "lon": -124.2167},
        {"station_id": "9419750", "station_name": "Crescent City", "lat": 41.7456, "lon": -124.1839},
    ])

#Cell 1.6:  Save Raw station metadata from API to data/raw
stations_df = fetch_noaa_ca_station_metadata()

if stations_df.empty:
    stations_df = fallback_ca_station_list()

stations_path = os.path.join(RAW_DATA_DIR, "ca_noaa_stations.csv")
stations_df.to_csv(stations_path, index=False)

stations_df.head()

#Cell 1.7: Fetch water-level timeseries for each station
def fetch_water_level_timeseries(station_id, days_back=DAYS_BACK):
    end = datetime.now(timezone.utc)
    start = end - timedelta(days=days_back)

    datums_to_try = ["MSL", "MLLW", "NAVD"]
    url = "https://api.tidesandcurrents.noaa.gov/api/prod/datagetter"

    for datum in datums_to_try:
        params = {
            "product": "water_level",
            "application": "CA_Coastal_Project",
            "station": station_id,
            "begin_date": start.strftime("%Y%m%d"),
            "end_date": end.strftime("%Y%m%d"),
            "datum": datum,
            "time_zone": "gmt",
            "units": "metric",
            "format": "json",
        }

        data, status, _ = safe_get_json(url, params=params)

        if status != 200 or data is None or "data" not in data:
            continue

        df = pd.DataFrame(data["data"])
        if "t" not in df.columns or "v" not in df.columns:
            continue

        df["datetime"] = pd.to_datetime(df["t"], utc=True, errors="coerce")
        df["water_level_m"] = ensure_float_series(df["v"])
        df = df[["datetime", "water_level_m"]].dropna()

        if len(df) >= 30:
            return df

    return None

#Cell 1.8: saves timereis data to data/raw
for _, row in stations_df.iterrows():
    station_id = row["station_id"]
    print("Downloading water levels for:", station_id)

    ts_df = fetch_water_level_timeseries(station_id)
    time.sleep(SLEEP_BETWEEN_STATIONS_SEC)

    if ts_df is None or ts_df.empty:
        continue

    ts_path = os.path.join(
        TIMESERIES_DIR,
        f"{station_id}_water_level.csv"
    )
    ts_df.to_csv(ts_path, index=False)