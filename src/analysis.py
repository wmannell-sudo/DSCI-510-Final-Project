def compute_linear_trend_m_per_year(ts_df):
    df = ts_df.copy()
    df = df.dropna()
    if len(df) < 30:
        return np.nan, np.nan

    t0 = df["datetime"].min()
    df["time_s"] = (df["datetime"] - t0).dt.total_seconds()

    if df["time_s"].nunique() < 2:
        return np.nan, np.nan

    slope_m_per_s, intercept = np.polyfit(df["time_s"].to_numpy(), df["water_level_m"].to_numpy(), 1)
    slope_m_per_year = slope_m_per_s * 60 * 60 * 24 * 365
    return slope_m_per_year, intercept


trend_records = []
ts_cache_dir = os.path.join(OUTPUT_DIR, "timeseries_cache")
os.makedirs(ts_cache_dir, exist_ok=True)

for _, row in stations_ca.iterrows():
    sid = str(row["station_id"])
    sname = row["station_name"]

    ts = fetch_water_level_timeseries(sid, days_back=DAYS_BACK)
    time.sleep(SLEEP_BETWEEN_STATIONS_SEC)

    if ts is None or ts.empty:
        continue

    # Save raw time series
    ts_path = os.path.join(ts_cache_dir, f"{sid}_water_level.csv")
    ts.to_csv(ts_path, index=False)

    slope_m_yr, intercept = compute_linear_trend_m_per_year(ts)
    if np.isnan(slope_m_yr):
        continue

    trend_records.append({
        "station_id": sid,
        "station_name": sname,
        "lat": float(row["lat"]),
        "lon": float(row["lon"]),
        "trend_m_per_year": float(slope_m_yr),
        "trend_intercept": float(intercept),
        "n_points": int(len(ts)),
        "days_back": int(DAYS_BACK),
    })

tide_df = pd.DataFrame(trend_records).reset_index(drop=True)

tide_out = os.path.join(OUTPUT_DIR, "combined_ca_water_levels.csv")
tide_df.to_csv(tide_out, index=False)

print("Stations with usable time series and computed trends:", len(tide_df))
display(tide_df.head())


#Housing data from sklearn California Housing
cal = fetch_california_housing(as_frame=True)
housing_df = cal.frame.copy()
housing_df["latitude"] = housing_df["Latitude"]
housing_df["longitude"] = housing_df["Longitude"]

#Keep only what we need
housing_df = housing_df[["latitude", "longitude", "MedHouseVal"]].copy()


#Nearest housing point for each tide station using KDTree
if tide_df.empty:
    raise RuntimeError("No tide stations produced usable water level data. Try reducing DAYS_BACK or rerun later.")

tide_coords = tide_df[["lat", "lon"]].to_numpy()
house_coords = housing_df[["latitude", "longitude"]].to_numpy()

tree = KDTree(house_coords)
distances, indices = tree.query(tide_coords, k=1)

tide_df["MedHouseVal"] = housing_df.iloc[indices.flatten()]["MedHouseVal"].to_numpy()
tide_df["nearest_housing_distance_deg"] = distances.flatten()


#Calculates Risk score
tide_df["trend_norm"] = tide_df["trend_m_per_year"] / tide_df["trend_m_per_year"].max()

# Normalize housing value
tide_df["house_norm"] = tide_df["MedHouseVal"] / tide_df["MedHouseVal"].max()

# Compute risk score
tide_df["risk_score"] = tide_df["trend_norm"] * tide_df["house_norm"]

risk_out = os.path.join(OUTPUT_DIR, "combined_risk_data.csv")
tide_df.to_csv(risk_out, index=False)
