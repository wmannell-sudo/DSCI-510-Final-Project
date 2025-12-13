import os
import pandas as pd
from sklearn.datasets import fetch_california_housing
from sklearn.neighbors import KDTree


#Paths

RAW_DATA_DIR = os.path.join("data", "raw")
PROCESSED_DATA_DIR = os.path.join("data", "processed")
TIMESERIES_DIR = os.path.join(RAW_DATA_DIR, "timeseries")

os.makedirs(PROCESSED_DATA_DIR, exist_ok=True)

#Loads raw data

def load_station_metadata():
    """
    Load NOAA California station metadata from data/raw/.

    Returns:
    pandas.DataFrame
        Columns:
        - station_id
        - station_name
        - lat
        - lon
    """
    path = os.path.join(RAW_DATA_DIR, "ca_noaa_stations.csv")
    return pd.read_csv(path)


def load_all_timeseries():
    """
    Load all raw water-level time series from data/raw/timeseries/.

    Returns:
    dict
        Mapping station_id -> DataFrame(datetime, water_level_m)
    """
    ts_dict = {}

    for fname in os.listdir(TIMESERIES_DIR):
        if not fname.endswith("_water_level.csv"):
            continue

        station_id = fname.split("_")[0]
        path = os.path.join(TIMESERIES_DIR, fname)

        df = pd.read_csv(path, parse_dates=["datetime"])
        ts_dict[station_id] = df

    return ts_dict


#Housing data

def load_housing_data():
    """
    Load California housing data from sklearn dataset.

    Returns:
    pandas.DataFrame
        Columns:
        - latitude
        - longitude
        - MedHouseVal
    """
    cal = fetch_california_housing(as_frame=True)
    housing_df = cal.frame.copy()

    housing_df["latitude"] = housing_df["Latitude"]
    housing_df["longitude"] = housing_df["Longitude"]

    return housing_df[["latitude", "longitude", "MedHouseVal"]]


#Cleaning / merging

def attach_nearest_housing(tide_df, housing_df):
    """
    Attach nearest housing median value to each tide station
    using KDTree nearest-neighbor matching.

    Parameters:
    
    tide_df : pandas.DataFrame
        Must contain columns:
        - lat
        - lon
    housing_df : pandas.DataFrame
        Must contain columns:
        - latitude
        - longitude
        - MedHouseVal

    Returns:
    
    pandas.DataFrame
        With added columns:
        - MedHouseVal
        - nearest_housing_distance_deg
    """
    tide_df = tide_df.copy()

    tide_coords = tide_df[["lat", "lon"]].to_numpy()
    house_coords = housing_df[["latitude", "longitude"]].to_numpy()

    tree = KDTree(house_coords)
    distances, indices = tree.query(tide_coords, k=1)

    tide_df["MedHouseVal"] = housing_df.iloc[indices.flatten()]["MedHouseVal"].to_numpy()
    tide_df["nearest_housing_distance_deg"] = distances.flatten()

    return tide_df


def build_clean_dataset(tide_df):
    """
    Build cleaned and merged dataset ready for analysis.

    Parameters:
    
    tide_df : pandas.DataFrame
        Output from analysis step (station-level trends)

    Returns:
    
    pandas.DataFrame
        Cleaned and merged dataset
    """
    housing_df = load_housing_data()
    clean_df = attach_nearest_housing(tide_df, housing_df)

    return clean_df


def save_clean_dataset(df, filename="cleaned_tide_housing_data.csv"):
    """
    Save cleaned dataset to data/processed/.

    Returns:
    str
        Path to saved file
    """
    out_path = os.path.join(PROCESSED_DATA_DIR, filename)
    df.to_csv(out_path, index=False)
    return out_path
