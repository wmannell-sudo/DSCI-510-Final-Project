#Cell 4.1: Imports and output directories

import os
import pandas as pd
import matplotlib.pyplot as plt
import folium

from adjustText import adjust_text

PROCESSED_DATA_DIR = os.path.join("data", "processed")
OUTPUT_DIR = "results"

os.makedirs(OUTPUT_DIR, exist_ok=True)

#Cell 4.2: Load processed analysis data

risk_path = os.path.join(
    PROCESSED_DATA_DIR,
    "combined_risk_data.csv"
)

df = pd.read_csv(risk_path)

#Cell 4.3: Scatter Plot - sea-level trend vs. housing value

plt.figure(figsize=(10, 6))

plt.scatter(
    df["trend_m_per_year"],
    df["MedHouseVal"],
    s=50
)

plt.xlabel("Sea-level trend (m/year)")
plt.ylabel("Median house value")
plt.title("Sea-level trend vs median house value (California tide stations)")
plt.grid(True)

texts = []
for _, r in df.iterrows():
    texts.append(
        plt.text(
            r["trend_m_per_year"],
            r["MedHouseVal"],
            r["station_name"],
            fontsize=7
        )
    )

adjust_text(texts, arrowprops=dict(arrowstyle="-", lw=0.5))

scatter_out = os.path.join(
    OUTPUT_DIR,
    "scatter_trend_vs_housing.png"
)

plt.tight_layout()
plt.savefig(scatter_out, dpi=150)
plt.show()

#Cell 4.4: Bar plot of risk score by station

df_bar = df.sort_values("risk_score", ascending=False)

plt.figure(figsize=(12, 5))
plt.bar(df_bar["station_name"], df_bar["risk_score"])

plt.xticks(rotation=45, ha="right")
plt.ylabel("Risk score")
plt.title("Coastal risk score by station")
plt.grid(axis="y")

bar_out = os.path.join(
    OUTPUT_DIR,
    "bar_risk_scores.png"
)

plt.tight_layout()
plt.savefig(bar_out, dpi=150)

#Cell 4.5: Line plot of sea-level rise trend by station

df_line = df.sort_values("trend_m_per_year", ascending=False)

plt.figure(figsize=(12, 5))
plt.plot(
    df_line["station_name"],
    df_line["trend_m_per_year"],
    marker="o",
    linewidth=1
)

plt.xticks(rotation=45, ha="right")
plt.ylabel("Sea-level trend (m/year)")
plt.title("Sea-level trend by station")
plt.grid(True)

line_out = os.path.join(
    OUTPUT_DIR,
    "line_trends.png"
)

plt.tight_layout()
plt.savefig(line_out, dpi=150)

#Cell 4.6: Interactive map of risk score along stations of the CA coast made using folium
lat_min, lat_max = df["lat"].min(), df["lat"].max()
lon_min, lon_max = df["lon"].min(), df["lon"].max()

center_lat = (lat_min + lat_max) / 2
center_lon = (lon_min + lon_max) / 2

m = folium.Map(
    location=[center_lat, center_lon],
    zoom_start=6,
    tiles="OpenStreetMap"
)

m.fit_bounds([[lat_min, lon_min], [lat_max, lon_max]])

for _, r in df.iterrows():
    popup_text = (
        f"{r['station_name']}<br>"
        f"Trend (m/yr): {r['trend_m_per_year']:.6f}<br>"
        f"Risk score: {r['risk_score']:.3f}<br>"
        f"Median house value: {r['MedHouseVal']:.3f}"
    )

    folium.CircleMarker(
        location=[r["lat"], r["lon"]],
        radius=5,
        color="red",
        fill=True,
        fill_opacity=0.6,
        popup=popup_text
    ).add_to(m)

map_out = os.path.join(
    OUTPUT_DIR,
    "ca_coastal_risk_map.html"
)

m.save(map_out)