#Scatter: trend vs housing value
plt.figure(figsize=(10, 6))
plt.scatter(tide_df["trend_m_per_year"], tide_df["MedHouseVal"], s=50)

plt.xlabel("Sea-level trend (m/year)")
plt.ylabel("Median house value (scaled units)")
plt.title("Sea-level trend vs median house value (California stations)")
plt.grid(True)

from adjustText import adjust_text

texts = []
for _, r in tide_df.iterrows():
    texts.append(
        plt.text(
            r["trend_m_per_year"],
            r["MedHouseVal"],
            r["station_name"],
            fontsize=7
        )
    )

adjust_text(texts)

scatter_out = os.path.join(OUTPUT_DIR, "scatter_trend_vs_housing.png")
plt.tight_layout()
plt.savefig(scatter_out, dpi=150)
plt.show()

#Bar chart: risk score by station
df_bar = tide_df.sort_values("risk_score", ascending=False).copy()

plt.figure(figsize=(12, 5))
plt.bar(df_bar["station_name"], df_bar["risk_score"])
plt.xticks(rotation=45, ha="right")
plt.ylabel("Risk score")
plt.title("Risk score by station")
plt.grid(axis="y")

bar_out = os.path.join(OUTPUT_DIR, "bar_risk_scores.png")
plt.tight_layout()
plt.savefig(bar_out, dpi=150)
plt.show()

#Line chart: sea-level trend by station
df_line = tide_df.sort_values("trend_m_per_year", ascending=False).copy()

plt.figure(figsize=(12, 5))
plt.plot(df_line["station_name"], df_line["trend_m_per_year"], marker="o", linewidth=1)
plt.xticks(rotation=45, ha="right")
plt.ylabel("Sea-level trend (m/year)")
plt.title("Sea-level trend by station")
plt.grid(True)

line_out = os.path.join(OUTPUT_DIR, "line_trends.png")
plt.tight_layout()
plt.savefig(line_out, dpi=150)
plt.show()
