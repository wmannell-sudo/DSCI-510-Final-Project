lat_min, lat_max = tide_df["lat"].min(), tide_df["lat"].max()
lon_min, lon_max = tide_df["lon"].min(), tide_df["lon"].max()
center_lat, center_lon = (lat_min + lat_max) / 2, (lon_min + lon_max) / 2

m = folium.Map(location=[center_lat, center_lon], zoom_start=6, tiles="OpenStreetMap")
m.fit_bounds([[lat_min, lon_min], [lat_max, lon_max]])

for _, r in tide_df.iterrows():
    popup_txt = (
        f"{r['station_name']}<br>"
        f"Trend (m/yr): {r['trend_m_per_year']:.6f}<br>"
        f"Risk score: {r['risk_score']:.3f}<br>"
        f"MedHouseVal: {r['MedHouseVal']:.3f}"
    )
    folium.CircleMarker(
        location=[r["lat"], r["lon"]],
        radius=5,
        color="red",
        fill=True,
        fill_opacity=0.6,
        popup=popup_txt
    ).add_to(m)

map_out = os.path.join(OUTPUT_DIR, "ca_coastal_risk_map.html")
m.save(map_out)
