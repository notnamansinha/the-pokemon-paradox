"""Generate verified academic serif figures with consistent editorial formatting.

Uses serif typography (Cambria / DejaVu Serif), muted professional palette,
and standardized academic footers. Exports all figures to output/charts/.
"""
from pathlib import Path
import json
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
OUT = ROOT / "output"
CHARTS = OUT / "charts"
CHARTS.mkdir(parents=True, exist_ok=True)

# Publication editorial style configuration
plt.rcParams.update({
    "font.family": "serif",
    "font.serif": ["Cambria", "Times New Roman", "DejaVu Serif"],
    "font.size": 10,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.edgecolor": "#777777",
    "axes.labelcolor": "#222222",
    "xtick.color": "#333333",
    "ytick.color": "#333333",
    "axes.axisbelow": True,
    "savefig.dpi": 300,
})

STEEL = "#2B5B84"
RUST = "#C0392B"
GREEN = "#27AE60"
GOLD = "#D4AC0D"
TEAL = "#16A085"
GRAY = "#7F8C8D"
LIGHT_GRAY = "#BDC3C7"


def save_chart(fig, filename: str):
    fig.supxlabel("Source: Official Pokédex Database (2008–2025), N = 1,219 unique Pokémon entries; author calculations.",
                  fontsize=7.5, color="#555555", y=0.01)
    fig.savefig(CHARTS / filename, facecolor="white", bbox_inches="tight")
    fig.savefig(CHARTS / filename.replace(".png", ".pdf"), facecolor="white", bbox_inches="tight")
    plt.close(fig)
    print(f"Verified chart exported: {filename}")


def main():
    cleaned_csv = DATA_DIR / "pokemon_database_cleaned.csv"
    if not cleaned_csv.exists():
        from build_analysis_data import clean_and_engineer, load_raw_data
        df_raw = load_raw_data()
        df, _ = clean_and_engineer(df_raw)
        df.to_csv(cleaned_csv, index=False)
    else:
        df = pd.read_csv(cleaned_csv)

    print(f"Rendering verified serif figures from {len(df)} records...")

    # Figure 1: Top 10 BST
    top_10 = df.nlargest(10, "Total")[["Name", "Total"]].sort_values("Total", ascending=False)
    fig, ax = plt.subplots(figsize=(9.5, 5))
    bars = ax.bar(range(len(top_10)), top_10["Total"], color=STEEL, width=0.6)
    ax.set_title("Top 10 Pokémon by Base Stat Total (BST)", loc="left", fontweight="bold", fontsize=12, pad=12)
    ax.set_ylabel("Total Base Stats")
    ax.set_xticks(range(len(top_10)))
    ax.set_xticklabels([n.replace("\r\n", " ") for n in top_10["Name"]], rotation=25, ha="right", fontsize=8.5)
    ax.set_ylim(0, 1250)
    ax.grid(axis="y", color="#E2E4E3", linewidth=0.6)
    for b in bars:
        h = b.get_height()
        ax.annotate(f"{int(h)}", xy=(b.get_x() + b.get_width()/2, h), xytext=(0, 3),
                    textcoords="offset points", ha="center", va="bottom", fontsize=8, fontweight="bold")
    save_chart(fig, "figure_1_top_10_bst.png")

    # Figure 6: Average Total Stats by Type
    type_stats = df.groupby("Primary_Type")["Total"].mean().sort_values(ascending=True)
    fig, ax = plt.subplots(figsize=(8.5, 7))
    bars = ax.barh(range(len(type_stats)), type_stats.values, color=TEAL, height=0.65)
    ax.set_title("Primary Elemental Types Ranked by Mean Base Stat Total", loc="left", fontweight="bold", fontsize=12, pad=12)
    ax.set_xlabel("Mean Total Stats (BST)")
    ax.set_yticks(range(len(type_stats)))
    ax.set_yticklabels(type_stats.index, fontsize=9)
    ax.set_xlim(0, 600)
    ax.grid(axis="x", color="#E2E4E3", linewidth=0.6)
    for b in bars:
        w = b.get_width()
        ax.annotate(f"{w:.1f}", xy=(w, b.get_y() + b.get_height()/2), xytext=(4, 0),
                    textcoords="offset points", ha="left", va="center", fontsize=7.5)
    save_chart(fig, "figure_6_type_average_bst.png")

    # Figure 9: Strong vs Legendary
    stats_to_plot = ["HP", "Attack", "Defense", "Sp. Atk", "Sp. Def", "Speed"]
    s_mean = df[df["Power_Category"] == "Strong"][stats_to_plot].mean()
    l_mean = df[df["Power_Category"] == "Legendary"][stats_to_plot].mean()
    fig, ax = plt.subplots(figsize=(9, 4.8))
    x = np.arange(len(stats_to_plot))
    w = 0.35
    b1 = ax.bar(x - w/2, s_mean, w, label="Strong (BST 451–600)", color=STEEL)
    b2 = ax.bar(x + w/2, l_mean, w, label="Legendary (BST 601–1200)", color="#D35400")
    ax.set_title("Mean Base Stats: Strong Tier vs. Legendary Tier", loc="left", fontweight="bold", fontsize=12, pad=12)
    ax.set_ylabel("Mean Stat Points")
    ax.set_xticks(x)
    ax.set_xticklabels(stats_to_plot, fontsize=9.5)
    ax.set_ylim(0, 155)
    ax.legend(frameon=False, loc="upper left")
    ax.grid(axis="y", color="#E2E4E3", linewidth=0.6)
    for b in b1:
        ax.annotate(f"{b.get_height():.1f}", xy=(b.get_x() + b.get_width()/2, b.get_height()),
                    xytext=(0, 2), textcoords="offset points", ha="center", va="bottom", fontsize=7.5)
    for b in b2:
        ax.annotate(f"{b.get_height():.1f}", xy=(b.get_x() + b.get_width()/2, b.get_height()),
                    xytext=(0, 2), textcoords="offset points", ha="center", va="bottom", fontsize=7.5, fontweight="bold")
    save_chart(fig, "figure_9_strong_vs_legendary_stats.png")

    print("Verified figures successfully rendered.")


if __name__ == "__main__":
    main()
