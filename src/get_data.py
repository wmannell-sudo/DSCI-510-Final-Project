import os
import time
from datetime import datetime, timedelta, timezone

import pandas as pd
import requests

from src.utils.utils import safe_get_json, ensure_float_series

#Paths for Data

RAW_DATA_DIR = os.path.join("data", "raw")
TIMESERIES_DIR = os.path.join(RAW_DATA_DIR, "timeseries")

os.makedirs(RAW_DATA_DIR, exist_ok=True)
os.makedirs(TIMESERIES_DIR, exist_ok=True)

#Fetch NOAA station metadata

def fetch_noaa_ca_station_metadata():
    """
    Download NOAA tide station metadata and filter to California stations.

    Returns:
    
    pandas.DataFrame
        Columns:
        - station_id
        - station_name
        - lat
        - lon
    """
    url = "https://api.tidesandcurrents.noaa.gov/mdapi/prod/webapi/stations.json"
    params = {
        "expand": "details,products,latlon",
        "type": "waterlevels",
    }

    data, status, _ = safe_get_json(url, params=params)

    if data is None or "stations" not in data:
        return pd.DataFrame(columns=["station_id", "station_name", "lat", "lon"])

    df = pd.DataFrame(data["stations"]).copy()

    rename_map = {}

    if "id" in df.columns:
        rename_map["id"] = "station_id"
    if "name" in df.columns:
        rename_map["name"] = "station_name"

    for col in ["lat", "latitude", "lat_dd"]:
        if col in df.columns:
            rename_map[col] = "lat"
            break

    for col in ["lon", "longitude", "lon_dd"]:
        if col in df.columns:
            rename_map[col] = "lon"
            break

    if "state" in df.columns:
        rename_map["state"] = "state"

    df = df.rename(columns=rename_map)

    needed = [c for c in ["station_id", "station_name", "lat", "lon", "state"] if c in df.columns]
    df = df[needed].copy()

    if "state" in df.columns:
        df = df[df["state"] == "CA"].copy()

    df["lat"] = ensure_float_series(df["lat"])
    df["lon"] = ensure_float_series(df["lon"])

    df = df.dropna(subset=["station_id", "station_name", "lat", "lon"]).reset_index(drop=True)

    return df[["station_id", "station_name", "lat", "lon"]]


def fallback_ca_station_list():
    """
    Fallback list of California tide stations.
    Used if NOAA metadata endpoint fails.
    """
    return pd.DataFrame([
        {"station_id": "9410170", "station_name": "San Diego",       "lat": 32.7142, "lon": -117.1736},
        {"station_id": "9410230", "station_name": "La Jolla",        "lat": 32.8669, "lon": -117.2571},
        {"station_id": "9410660", "station_name": "Los Angeles",     "lat": 33.7197, "lon": -118.2722},
        {"station_id": "9410840", "station_name": "Santa Monica",    "lat": 34.0083, "lon": -118.5000},
        {"station_id": "9411340", "station_name": "Santa Barbara",   "lat": 34.4033, "lon": -119.6920},
        {"station_id": "9412110", "station_name": "Port San Luis",   "lat": 35.1683, "lon": -120.7540},
        {"station_id": "9413450", "station_name": "Monterey",        "lat": 36.6050, "lon": -121.8883},
        {"station_id": "9414290", "station_name": "San Francisco",   "lat": 37.8063, "lon": -122.4659},
        {"station_id": "9414523", "station_name": "Redwood City",    "lat": 37.5067, "lon": -122.2092},
        {"station_id": "9414750", "station_name": "Alameda",         "lat": 37.7717, "lon": -122.3000},
        {"station_id": "9414863", "station_name": "Richmond",        "lat": 37.9233, "lon": -122.4097},
        {"station_id": "9415020", "station_name": "Point Reyes",     "lat": 37.9967, "lon": -122.9750},
        {"station_id": "9416841", "station_name": "Arena Cove",      "lat": 38.9140, "lon": -123.7110},
        {"station_id": "9418767", "station_name": "North Spit",      "lat": 40.7667, "lon": -124.2167},
        {"station_id": "9419750", "station_name": "Crescent City",   "lat": 41.7456, "lon": -124.1839},
    ])


def save_station_metadata():
    """
    Download and save California NOAA station metadata to data/raw/.
    """
    stations = fetch_noaa_ca_station_metadata()

    if stations.empty:
        stations = fallback_ca_station_list()

    out_path = os.path.join(RAW_DATA_DIR, "ca_noaa_stations.csv")
    stations.to_csv(out_path, index=False)

    return stations


#Prep for NOAA water-level time series

def fetch_water_level_timeseries(station_id, days_back=30):
    """
    Fetch raw NOAA water-level time series

    Returns:
    
    pandas.DataFrame or None
        Columns:
        - datetime
        - water_level_m
    """
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

        data, status, _ = safe_get_json(url, params=params)

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


def download_all_timeseries(
    stations_df,
    days_back=30,
    sleep_sec=0.2
):
    """
    Download and save raw water-level time series for all stations.

    Saves one CSV per station in data/raw/timeseries/.
    """
    for _, row in stations_df.iterrows():
        sid = str(row["station_id"])
        ts = fetch_water_level_timeseries(sid, days_back=days_back)

        if ts is None or ts.empty:
            continue

        out_path = os.path.join(TIMESERIES_DIR, f"{sid}_water_level.csv")
        ts.to_csv(out_path, index=False)

        time.sleep(sleep_sec)

