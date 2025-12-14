#Cell 2.1: Imports
import os
import pandas as pd
import numpy as np

from pathlib import Path
from sklearn.datasets import fetch_california_housing
from sklearn.neighbors import KDTree

#Cell 2.2: Directory Configuration

RAW_DATA_DIR = os.path.join("data", "raw")
PROCESSED_DATA_DIR = os.path.join("data", "processed")

TIMESERIES_DIR = os.path.join(RAW_DATA_DIR, "timeseries_cache")

os.makedirs(PROCESSED_DATA_DIR, exist_ok=True)

#Cell 2.3: Load station metadata from data/raw

stations_path = os.path.join(RAW_DATA_DIR, "ca_noaa_stations.csv")

stations_df = pd.read_csv(stations_path)

stations_df.head()

#Cell 2.4: Load raw water-level timeseries into memory

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

#Cell 2.5  Prepare CA housing data, not in get_data.py because we used the pre-defined fetch_ca_housing_data function from sklearn.datasets
cal = fetch_california_housing(as_frame=True)

housing_df = cal.frame.copy()
housing_df["latitude"] = housing_df["Latitude"]
housing_df["longitude"] = housing_df["Longitude"]

housing_df = housing_df[["latitude", "longitude", "MedHouseVal"]]

housing_df.head()

#Cell 2.6: Attatch nearest housing value index to tide stations

def attach_housing_data_to_stations(stations_df, housing_df):
    station_coords = stations_df[["lat", "lon"]].to_numpy()
    housing_coords = housing_df[["latitude", "longitude"]].to_numpy()

    tree = KDTree(housing_coords)
    distances, indices = tree.query(station_coords, k=1)

    stations_df = stations_df.copy()
    stations_df["MedHouseVal"] = housing_df.iloc[indices.flatten()]["MedHouseVal"].to_numpy()
    stations_df["nearest_housing_distance_deg"] = distances.flatten()

    return stations_df

stations_with_housing = attach_housing_data_to_stations(
    stations_df,
    housing_df
)

stations_with_housing.head()

#Cell 2.7: Saved cleaned station metadata to data/processed

processed_path = os.path.join(
    PROCESSED_DATA_DIR,
    "stations_with_housing.csv"
)

stations_with_housing.to_csv(processed_path, index=False)

processed_path