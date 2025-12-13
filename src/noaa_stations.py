import pandas as pd
from .utils import safe_get_json, ensure_float_series

def fetch_noaa_ca_station_metadata():
    url = "https://api.tidesandcurrents.noaa.gov/mdapi/prod/webapi/stations.json"
    params = {
        "expand": "details,products,latlon",
        "type": "waterlevels"
    }

    data, status, head = safe_get_json(url, params=params)
    if data is None or "stations" not in data:
        return pd.DataFrame(columns=["station_id", "station_name", "lat", "lon"])

    df = pd.DataFrame(data["stations"]).copy()

    rename_map = {}
    if "id" in df.columns:
        rename_map["id"] = "station_id"
    if "name" in df.columns:
        rename_map["name"] = "station_name"

    for col in ["lat", "latitude", "lat_dd", "lt"]:
        if col in df.columns:
            rename_map[col] = "lat"
            break

    for col in ["lon", "lng", "longitude", "lon_dd", "ln"]:
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
    return df[["station_id", "station_name", "lat", "lon"]].copy()


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
        {"station_id": "9414523", "station_name": "Redwood City", "lat": 37.5067, "lon": -122.2092},
        {"station_id": "9414750", "station_name": "Alameda", "lat": 37.7717, "lon": -122.3000},
        {"station_id": "9414863", "station_name": "Richmond", "lat": 37.9233, "lon": -122.4097},
        {"station_id": "9415020", "station_name": "Point Reyes", "lat": 37.9967, "lon": -122.9750},
        {"station_id": "9416841", "station_name": "Arena Cove", "lat": 38.9140, "lon": -123.7110},
        {"station_id": "9418767", "station_name": "North Spit", "lat": 40.7667, "lon": -124.2167},
        {"station_id": "9419750", "station_name": "Crescent City", "lat": 41.7456, "lon": -124.1839},
    ])

