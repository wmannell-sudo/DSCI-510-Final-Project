import os
import pandas as pd
import matplotlib.pyplot as plt
import folium

from adjustText import adjust_text


# Paths

PROCESSED_DATA_DIR = os.path.join("data", "processed")
OUTPUT_FIG_DIR = "outputs"

os.makedirs(OUTPUT_FIG_DIR, exist_ok=True)


# Load processed data

def load_processed_data(filename="combined_risk_data.csv"):
    """
    Load processed dataset containing trends and risk scores.
    """
    path = os.path.join(PROCESSED_DATA_DIR, filename)
    return pd.read_csv(path)


# Scatter plot: sea-level trend vs housing value

def plot_trend_vs_housing(df):
    """
    Scatter plot of sea-level trend vs median house value
    with readable, non-overlapping labels.
    """
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

    out_path = os.path.join(OUTPUT_FIG_DIR, "scatter_trend_vs_housing.png")
    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()

    return out_path


# Bar chart: risk score by station

def plot_risk_bar_chart(df):
    """
    Bar chart of risk score by station.
    """
    df_plot = df.sort_values("risk_score", ascending=False)

    plt.figure(figsize=(12, 5))
    plt.bar(df_plot["station_name"], df_plot["risk_score"])
    plt.xticks(rotation=45, ha="right")
    plt.ylabel("Risk score")
    plt.title("Coastal risk score by station")
    plt.grid(axis="y")

    out_path = os.path.join(OUTPUT_FIG_DIR, "bar_risk_scores.png")
    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()

    return out_path


# Line plot: sea-level trend by station

def plot_trend_line(df):
    """
    Line plot of sea-level trend by station.
    """
    df_plot = df.sort_values("trend_m_per_year", ascending=False)

    plt.figure(figsize=(12, 5))
    plt.plot(
        df_plot["station_name"],
        df_plot["trend_m_per_year"],
        marker="o",
        linewidth=1
    )

    plt.xticks(rotation=45, ha="right")
    plt.ylabel("Sea-level trend (m/year)")
    plt.title("Sea-level trend by station")
    plt.grid(True)

    out_path = os.path.join(OUTPUT_FIG_DIR, "line_trends.png")
    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()

    return out_path


# Folium map: Risk Along the California Coast

def build_folium_map(df):
    """
    Build an optimized Folium map focused on California coastal stations.
    """
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

    out_path = os.path.join(OUTPUT_FIG_DIR, "ca_coastal_risk_map.html")
    m.save(out_path)

    return out_path


# Run all visualizations

def run_all_visualizations():
    """
    Generate all plots and maps.
    """
    df = load_processed_data()

    outputs = {
        "scatter": plot_trend_vs_housing(df),
        "bar": plot_risk_bar_chart(df),
        "line": plot_trend_line(df),
        "map": build_folium_map(df),
    }

    return outputs
