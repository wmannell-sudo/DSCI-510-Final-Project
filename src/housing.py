from sklearn.datasets import fetch_california_housing
from sklearn.neighbors import KDTree

def attach_nearest_housing(tide_df):
    cal = fetch_california_housing(as_frame=True)
    housing_df = cal.frame.copy()
    housing_df["latitude"] = housing_df["Latitude"]
    housing_df["longitude"] = housing_df["Longitude"]
    housing_df = housing_df[["latitude", "longitude", "MedHouseVal"]]

    tide_coords = tide_df[["lat", "lon"]].to_numpy()
    house_coords = housing_df[["latitude", "longitude"]].to_numpy()

    tree = KDTree(house_coords)
    distances, indices = tree.query(tide_coords, k=1)

    tide_df["MedHouseVal"] = housing_df.iloc[indices.flatten()]["MedHouseVal"].to_numpy()
    tide_df["nearest_housing_distance_deg"] = distances.flatten()
    return tide_df
