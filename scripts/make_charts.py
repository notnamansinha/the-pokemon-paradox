"""Render all analytical figures in publication-grade PNG and PDF formats.

Produces:
- figure_1_top_10_bst (.png, .pdf)
- figure_2_attack_vs_defense (.png, .pdf)
- figure_3_correlation_heatmap (.png, .pdf)
- figure_4_bst_distribution (.png, .pdf)
- figure_5_stat_boxplots_by_category (.png, .pdf)
- figure_6_type_average_bst (.png, .pdf)
- figure_7_individual_stat_distributions (.png, .pdf)
- figure_8_primary_type_pie_chart (.png, .pdf)
- figure_9_strong_vs_legendary_stats (.png, .pdf)
- figure_10_cluster_battle_roles (.png, .pdf)
"""
from pathlib import Path
import json
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np
import pandas as pd
import seaborn as sns
from sklearn.decomposition import PCA

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
OUT = ROOT / "output"
CHARTS_DIR = OUT / "charts"
CHARTS_DIR.mkdir(parents=True, exist_ok=True)

# Publication style configuration
plt.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["Segoe UI", "Calibri", "DejaVu Sans", "Helvetica", "Arial"],
    "figure.dpi": 300,
    "savefig.dpi": 300,
    "axes.edgecolor": "#CCCCCC",
    "axes.linewidth": 0.8,
    "grid.color": "#E5E5E5",
    "grid.linestyle": "--",
    "grid.linewidth": 0.5,
})


def load_clean_data() -> pd.DataFrame:
    cleaned_csv = DATA_DIR / "pokemon_database_cleaned.csv"
    if not cleaned_csv.exists():
        from build_analysis_data import clean_and_engineer, load_raw_data
        df_raw = load_raw_data()
        df_clean, _ = clean_and_engineer(df_raw)
        df_clean.to_csv(cleaned_csv, index=False)
        return df_clean
    return pd.read_csv(cleaned_csv)


def save_fig(fig, name_stem: str):
    png_path = CHARTS_DIR / f"{name_stem}.png"
    pdf_path = CHARTS_DIR / f"{name_stem}.pdf"
    fig.savefig(png_path, bbox_inches="tight", dpi=300)
    fig.savefig(pdf_path, bbox_inches="tight")
    plt.close(fig)
    print(f"Saved: {png_path.name} & {pdf_path.name}")


def plot_figure_1_top_10(df: pd.DataFrame):
    fig, ax = plt.subplots(figsize=(12, 6.5))
    top_10 = df.nlargest(10, "Total")[["Name", "Total"]].sort_values("Total", ascending=False)
    
    # Clean multi-line names for display
    clean_names = [n.replace("\r\n", "\n").replace("  ", "\n") for n in top_10["Name"]]
    
    bars = ax.bar(clean_names, top_10["Total"], color="#3F729B", edgecolor="#1F3A52", width=0.65)
    ax.set_title("Top 10 Pokémon by Total Stats (Base Stat Total)", fontsize=14, fontweight="bold", pad=15)
    ax.set_ylabel("Total Stats", fontsize=11, fontweight="medium")
    ax.set_xlabel("Pokémon", fontsize=11, fontweight="medium", labelpad=10)
    ax.set_ylim(0, 1250)
    ax.grid(axis="y", alpha=0.5)
    
    # Value annotations on top of bars
    for bar in bars:
        h = bar.get_height()
        ax.annotate(f"{int(h)}",
                    xy=(bar.get_x() + bar.get_width() / 2, h),
                    xytext=(0, 4), textcoords="offset points",
                    ha="center", va="bottom", fontsize=9.5, fontweight="bold", color="#1F3A52")
    
    plt.xticks(rotation=25, ha="right", fontsize=9.5)
    save_fig(fig, "figure_1_top_10_bst")


def plot_figure_2_attack_vs_defense(df: pd.DataFrame):
    fig, ax = plt.subplots(figsize=(10, 7))
    scatter = ax.scatter(
        df["Attack"],
        df["Defense"],
        c=df["Total"],
        cmap="viridis",
        alpha=0.65,
        s=55,
        edgecolors="none"
    )
    cbar = plt.colorbar(scatter, ax=ax, shrink=0.85, pad=0.03)
    cbar.set_label("Total Stats", fontsize=10.5, labelpad=8)
    
    ax.set_title("Attack vs Defense (colored by Total Stats)", fontsize=13, fontweight="bold", pad=12)
    ax.set_xlabel("Attack", fontsize=11, labelpad=8)
    ax.set_ylabel("Defense", fontsize=11, labelpad=8)
    ax.set_xlim(0, 200)
    ax.set_ylim(0, 260)
    ax.grid(True, alpha=0.4)
    save_fig(fig, "figure_2_attack_vs_defense")


def plot_figure_3_heatmap(df: pd.DataFrame):
    numeric_cols = ["Total", "HP", "Attack", "Defense", "Sp. Atk", "Sp. Def", "Speed"]
    corr = df[numeric_cols].corr()
    
    fig, ax = plt.subplots(figsize=(8.5, 7.5))
    sns.heatmap(
        corr,
        annot=True,
        cmap="coolwarm",
        center=0,
        square=True,
        linewidths=1.2,
        linecolor="white",
        cbar_kws={"shrink": 0.82, "label": "Correlation Coefficient"},
        fmt=".2f",
        annot_kws={"size": 10.5, "weight": "medium"},
        ax=ax
    )
    ax.set_title("Correlation Heatmap of Pokémon Stats", fontsize=13.5, fontweight="bold", pad=15)
    save_fig(fig, "figure_3_correlation_heatmap")


def plot_figure_4_distribution(df: pd.DataFrame):
    fig, ax = plt.subplots(figsize=(10, 6))
    mean_val = df["Total"].mean()
    med_val = df["Total"].median()
    
    ax.hist(df["Total"], bins=50, color="#E87A5D", edgecolor="#333333", linewidth=0.6, alpha=0.75)
    ax.axvline(mean_val, color="#1B6CA8", linestyle="--", linewidth=1.5, label=f"Mean: {mean_val:.2f}")
    ax.axvline(med_val, color="#2D8B55", linestyle="--", linewidth=1.5, label=f"Median: {med_val:.2f}")
    
    ax.set_title("Distribution of Total Stats", fontsize=13, fontweight="bold", pad=12)
    ax.set_xlabel("Total Stats", fontsize=11, labelpad=8)
    ax.set_ylabel("Frequency", fontsize=11, labelpad=8)
    ax.legend(frameon=True, facecolor="white", framealpha=0.9, fontsize=10)
    ax.grid(axis="y", alpha=0.4)
    save_fig(fig, "figure_4_bst_distribution")


def plot_figure_5_boxplots(df: pd.DataFrame):
    stats_to_plot = ["HP", "Attack", "Defense", "Sp. Atk", "Sp. Def", "Speed"]
    fig, axes = plt.subplots(2, 3, figsize=(14, 9), sharey=False)
    fig.suptitle("Distribution of Stats by Power Category", fontsize=14, fontweight="bold", y=0.98)
    
    palette = ["#4E79A7", "#59A14F", "#EDC948", "#E15759"]
    order = ["Weak", "Average", "Strong", "Legendary"]
    
    for idx, stat in enumerate(stats_to_plot):
        ax = axes[idx // 3, idx % 3]
        sns.boxplot(
            x="Power_Category",
            y=stat,
            data=df,
            ax=ax,
            order=order,
            palette=palette,
            width=0.55,
            fliersize=3.5,
            linewidth=1.0
        )
        ax.set_title(f"{stat} by Power Category", fontsize=10.5, fontweight="bold", pad=6)
        ax.set_xlabel("Power Category", fontsize=9.5)
        ax.set_ylabel(stat, fontsize=9.5)
        ax.grid(axis="y", alpha=0.4)
        ax.tick_params(axis="x", rotation=15)
        
    plt.tight_layout(rect=[0, 0, 1, 0.96])
    save_fig(fig, "figure_5_stat_boxplots_by_category")


def plot_figure_6_type_horizontal_bar(df: pd.DataFrame):
    fig, ax = plt.subplots(figsize=(10.5, 8.5))
    type_stats = df.groupby("Primary_Type")["Total"].mean().sort_values(ascending=True)
    
    bars = ax.barh(type_stats.index, type_stats.values, color="#1D7874", edgecolor="#114B48", height=0.68)
    ax.set_title("Pokémon Types by Average Total Stats", fontsize=13, fontweight="bold", pad=12)
    ax.set_xlabel("Average Total Stats", fontsize=10.5, labelpad=8)
    ax.set_ylabel("Primary Type", fontsize=10.5, labelpad=8)
    ax.set_xlim(0, 600)
    ax.grid(axis="x", alpha=0.4)
    
    for bar in bars:
        w = bar.get_width()
        ax.annotate(f"{w:.1f}",
                    xy=(w, bar.get_y() + bar.get_height() / 2),
                    xytext=(5, 0), textcoords="offset points",
                    ha="left", va="center", fontsize=8.5, color="#114B48")
                    
    save_fig(fig, "figure_6_type_average_bst")


def plot_figure_7_individual_stat_histograms(df: pd.DataFrame):
    stats_to_plot = ["HP", "Attack", "Defense", "Sp. Atk", "Sp. Def", "Speed"]
    fig, axes = plt.subplots(2, 3, figsize=(14, 8.5), sharey=False)
    fig.suptitle("Distribution of Base Stats", fontsize=14, fontweight="bold", y=0.98)
    
    for idx, stat in enumerate(stats_to_plot):
        ax = axes[idx // 3, idx % 3]
        mean_v = df[stat].mean()
        med_v = df[stat].median()
        
        sns.histplot(df[stat], bins=30, kde=True, ax=ax, color="#4682B4", edgecolor="black", linewidth=0.5, alpha=0.6)
        ax.axvline(mean_v, color="#C0392B", linestyle="--", linewidth=1.2, label=f"Mean: {mean_v:.2f}")
        ax.axvline(med_v, color="#27AE60", linestyle="--", linewidth=1.2, label=f"Median: {med_v:.2f}")
        
        ax.set_title(f"Distribution of {stat}", fontsize=10.5, fontweight="bold")
        ax.set_xlabel(stat, fontsize=9.5)
        ax.set_ylabel("Frequency", fontsize=9.5)
        ax.legend(fontsize=8, frameon=True, facecolor="white", framealpha=0.85)
        ax.grid(axis="y", alpha=0.35)
        
    plt.tight_layout(rect=[0, 0, 1, 0.96])
    save_fig(fig, "figure_7_individual_stat_distributions")


def plot_figure_8_pie_chart(df: pd.DataFrame):
    fig, ax = plt.subplots(figsize=(9, 9))
    type_counts = df["Primary_Type"].value_counts()
    
    # Modern curated color palette for 18 types
    colors = [
        "#4A90E2", "#A8A878", "#78C850", "#A890F0", "#F08030",
        "#F85888", "#705848", "#B8A038", "#A040A0", "#E0C068",
        "#F8D030", "#EE99AC", "#98D8D8", "#705898", "#C03028",
        "#7038F8", "#B8B8D0", "#A8B820"
    ]
    
    wedges, texts, autotexts = ax.pie(
        type_counts,
        labels=type_counts.index,
        autopct="%1.1f%%",
        startangle=140,
        pctdistance=0.82,
        colors=colors[:len(type_counts)],
        wedgeprops=dict(width=0.45, edgecolor="white", linewidth=1.2)
    )
    plt.setp(texts, size=8.5)
    plt.setp(autotexts, size=7.5, weight="bold")
    ax.set_title("Distribution of Primary Pokémon Types", fontsize=13.5, fontweight="bold", pad=15)
    save_fig(fig, "figure_8_primary_type_pie_chart")


def plot_figure_9_grouped_bar_strong_legendary(df: pd.DataFrame):
    stats_to_plot = ["HP", "Attack", "Defense", "Sp. Atk", "Sp. Def", "Speed"]
    strong_means = df[df["Power_Category"] == "Strong"][stats_to_plot].mean()
    leg_means = df[df["Power_Category"] == "Legendary"][stats_to_plot].mean()
    
    stats_df = pd.DataFrame({
        "Strong": strong_means,
        "Legendary": leg_means
    })
    
    fig, ax = plt.subplots(figsize=(11, 6.5))
    x = np.arange(len(stats_to_plot))
    width = 0.35
    
    rects1 = ax.bar(x - width/2, stats_df["Strong"], width, label="Strong (BST 451–600)", color="#2B5B84", edgecolor="#183650")
    rects2 = ax.bar(x + width/2, stats_df["Legendary"], width, label="Legendary (BST 601–1200)", color="#E67E22", edgecolor="#934D0A")
    
    ax.set_title("Mean Stats Comparison: Strong vs Legendary", fontsize=13, fontweight="bold", pad=15)
    ax.set_xlabel("Base Stat", fontsize=11, labelpad=8)
    ax.set_ylabel("Mean Stat Value", fontsize=11, labelpad=8)
    ax.set_xticks(x)
    ax.set_xticklabels(stats_to_plot, fontsize=10.5)
    ax.set_ylim(0, 150)
    ax.legend(frameon=True, facecolor="white", framealpha=0.9, fontsize=10.5)
    ax.grid(axis="y", alpha=0.4)
    
    # Value labels
    for r in rects1:
        h = r.get_height()
        ax.annotate(f"{h:.1f}", xy=(r.get_x() + r.get_width() / 2, h), xytext=(0, 3),
                    textcoords="offset points", ha="center", va="bottom", fontsize=8.5, color="#183650")
    for r in rects2:
        h = r.get_height()
        ax.annotate(f"{h:.1f}", xy=(r.get_x() + r.get_width() / 2, h), xytext=(0, 3),
                    textcoords="offset points", ha="center", va="bottom", fontsize=8.5, color="#934D0A")
                    
    save_fig(fig, "figure_9_strong_vs_legendary_stats")


def plot_figure_10_battle_role_clusters(df: pd.DataFrame):
    stats_to_plot = ["HP", "Attack", "Defense", "Sp. Atk", "Sp. Def", "Speed"]
    from sklearn.preprocessing import StandardScaler
    from sklearn.cluster import KMeans
    
    scaler = StandardScaler()
    scaled = scaler.fit_transform(df[stats_to_plot].values)
    kmeans = KMeans(n_clusters=4, random_state=42, n_init=10)
    clusters = kmeans.fit_predict(scaled)
    
    pca = PCA(n_components=2, random_state=42)
    coords = pca.fit_transform(scaled)
    
    role_names = ["Low-Stat Unevolved", "Sweeper (Offensive)", "Wall (Defensive)", "Balanced / Tank"]
    # Map cluster index to label by centroid properties
    centroids = kmeans.cluster_centers_
    sorted_idx = np.argsort(centroids.sum(axis=1))
    cluster_to_role = {
        sorted_idx[0]: "Low-Stat Tier (Unevolved)",
        sorted_idx[1]: "Balanced / Tanks",
        sorted_idx[2]: "Walls / Defensive Specialists",
        sorted_idx[3]: "Sweepers / Apex Attackers",
    }
    
    fig, ax = plt.subplots(figsize=(10.5, 7.5))
    palette = ["#95A5A6", "#3498DB", "#2ECC71", "#E74C3C"]
    
    for c_id in range(4):
        mask = (clusters == c_id)
        ax.scatter(
            coords[mask, 0],
            coords[mask, 1],
            label=cluster_to_role[c_id],
            alpha=0.6,
            s=45,
            edgecolors="none",
            color=palette[c_id]
        )
        
    ax.set_title("K-Means Latent Battle Role Clustering (PCA 2D Projection)", fontsize=13, fontweight="bold", pad=15)
    ax.set_xlabel(f"Principal Component 1 ({pca.explained_variance_ratio_[0]*100:.1f}% Variance)", fontsize=10.5)
    ax.set_ylabel(f"Principal Component 2 ({pca.explained_variance_ratio_[1]*100:.1f}% Variance)", fontsize=10.5)
    ax.legend(frameon=True, facecolor="white", framealpha=0.9, fontsize=10)
    ax.grid(True, alpha=0.35)
    save_fig(fig, "figure_10_cluster_battle_roles")


def main():
    print("Loading data for chart rendering...")
    df = load_clean_data()
    print(f"Data ready with {len(df)} records.")
    
    plot_figure_1_top_10(df)
    plot_figure_2_attack_vs_defense(df)
    plot_figure_3_heatmap(df)
    plot_figure_4_distribution(df)
    plot_figure_5_boxplots(df)
    plot_figure_6_type_horizontal_bar(df)
    plot_figure_7_individual_stat_histograms(df)
    plot_figure_8_pie_chart(df)
    plot_figure_9_grouped_bar_strong_legendary(df)
    plot_figure_10_battle_role_clusters(df)
    
    print("All 10 figures rendered successfully in PNG & PDF!")


if __name__ == "__main__":
    main()
