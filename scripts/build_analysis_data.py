"""Build analysis dataset and statistical model results.

Extracts data from data/pokemon_database_raw.csv or data/Pokemon Dataset - Sheet1.csv,
performs cleaning, feature engineering, correlation analysis, hypothesis testing
(T-Tests, ANOVA), and K-Means battle role clustering.
Exports data/pokemon_database_cleaned.csv and output/analysis_data.json.
"""
from pathlib import Path
import json
import math
import numpy as np
import pandas as pd
from scipy.stats import pearsonr, spearmanr, ttest_ind, f_oneway
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
OUT = ROOT / "output"
OUT.mkdir(exist_ok=True)
CHARTS_DIR = OUT / "charts"
CHARTS_DIR.mkdir(exist_ok=True)


def load_raw_data() -> pd.DataFrame:
    candidates = [
        DATA_DIR / "pokemon_database_raw.csv",
        DATA_DIR / "Pokemon Dataset - Sheet1.csv",
    ]
    for p in candidates:
        if p.exists():
            return pd.read_csv(p)
    raise FileNotFoundError("Raw Pokémon dataset not found in data/ directory.")


def clean_and_engineer(df_raw: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    raw_count = len(df_raw)
    df = df_raw.copy()
    df.columns = df.columns.str.strip()
    
    # Standardize column names
    col_map = {}
    if df.columns[0] != "#":
        col_map[df.columns[0]] = "#"
    # Map Sp. Atk and Sp. Def if named differently
    for col in df.columns:
        if "special attack" in col.lower() and col not in ["Sp. Atk"]:
            col_map[col] = "Sp. Atk"
        elif "special defence" in col.lower() or "special defense" in col.lower() and col not in ["Sp. Def"]:
            col_map[col] = "Sp. Def"
    if col_map:
        df.rename(columns=col_map, inplace=True)

    numeric_cols = ["Total", "HP", "Attack", "Defense", "Sp. Atk", "Sp. Def", "Speed"]
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    # Cleaning: drop rows missing numeric stats
    df_clean = df.dropna(subset=numeric_cols).copy()
    cleaned_count = len(df_clean)
    rows_removed = raw_count - cleaned_count

    # Clean Name and Type strings
    df_clean["Name"] = df_clean["Name"].astype(str).str.strip().str.replace("\r\n", " ").str.replace("\n", " ")
    df_clean["Type_Clean"] = df_clean["Type"].astype(str).str.strip().str.replace("\r\n", "/").str.replace("\n", "/")
    
    # Split types
    type_split = df_clean["Type_Clean"].str.split("/", expand=True)
    df_clean["Primary_Type"] = type_split[0].str.strip()
    df_clean["Secondary_Type"] = type_split[1].str.strip().fillna("None") if type_split.shape[1] > 1 else "None"
    df_clean["Is_Dual_Type"] = df_clean["Secondary_Type"] != "None"

    # Core engineered features
    df_clean["Avg_Stats"] = df_clean[numeric_cols[1:]].mean(axis=1)
    df_clean["Physical_Power"] = (df_clean["Attack"] + df_clean["Defense"]) / 2.0
    df_clean["Special_Power"] = (df_clean["Sp. Atk"] + df_clean["Sp. Def"]) / 2.0
    df_clean["Offensive_Power"] = (df_clean["Attack"] + df_clean["Sp. Atk"]) / 2.0
    df_clean["Defensive_Power"] = (df_clean["Defense"] + df_clean["Sp. Def"]) / 2.0

    # Power categories: Weak (0-300), Average (301-450), Strong (451-600), Legendary (601-1200)
    df_clean["Power_Category"] = pd.cut(
        df_clean["Total"],
        bins=[0, 300, 450, 600, 1200],
        labels=["Weak", "Average", "Strong", "Legendary"],
    )

    meta = {
        "raw_record_count": raw_count,
        "cleaned_record_count": cleaned_count,
        "rows_removed": rows_removed,
    }
    return df_clean, meta


def compute_statistics(df_clean: pd.DataFrame, meta: dict) -> dict:
    numeric_cols = ["Total", "HP", "Attack", "Defense", "Sp. Atk", "Sp. Def", "Speed"]
    categories = ["Weak", "Average", "Strong", "Legendary"]
    stats_to_plot = ["HP", "Attack", "Defense", "Sp. Atk", "Sp. Def", "Speed"]

    # Basic stats
    stat_summary = {}
    for col in numeric_cols:
        series = df_clean[col]
        stat_summary[col] = {
            "count": int(series.count()),
            "mean": float(round(series.mean(), 6)),
            "std": float(round(series.std(), 6)),
            "median": float(round(series.median(), 6)),
            "min": float(series.min()),
            "max": float(series.max()),
            "q25": float(round(series.quantile(0.25), 6)),
            "q75": float(round(series.quantile(0.75), 6)),
        }

    # Top 10 Pokémon by Total Stats
    top_10_df = df_clean.nlargest(10, "Total")[["#", "Name", "Primary_Type", "Secondary_Type", "Total"] + stats_to_plot]
    top_10 = []
    for _, row in top_10_df.iterrows():
        top_10.append({
            "number": str(row["#"]),
            "name": str(row["Name"]),
            "primary_type": str(row["Primary_Type"]),
            "secondary_type": str(row["Secondary_Type"]),
            "total": float(row["Total"]),
            "hp": float(row["HP"]),
            "attack": float(row["Attack"]),
            "defense": float(row["Defense"]),
            "sp_atk": float(row["Sp. Atk"]),
            "sp_def": float(row["Sp. Def"]),
            "speed": float(row["Speed"]),
        })

    # Correlation Matrices
    pearson_matrix = {}
    spearman_matrix = {}
    pearson_p_matrix = {}
    spearman_p_matrix = {}

    for c1 in numeric_cols:
        pearson_matrix[c1] = {}
        spearman_matrix[c1] = {}
        pearson_p_matrix[c1] = {}
        spearman_p_matrix[c1] = {}
        for c2 in numeric_cols:
            pr, pp = pearsonr(df_clean[c1], df_clean[c2])
            sr, sp = spearmanr(df_clean[c1], df_clean[c2])
            pearson_matrix[c1][c2] = float(round(pr, 4))
            pearson_p_matrix[c1][c2] = float(pp)
            spearman_matrix[c1][c2] = float(round(sr, 4))
            spearman_p_matrix[c1][c2] = float(sp)

    # Key focal pairs
    focal_pairs = [
        ("Attack", "Defense"),
        ("Sp. Atk", "Sp. Def"),
        ("HP", "Total"),
        ("Speed", "Total"),
        ("Attack", "Sp. Atk"),
    ]
    paired_findings = []
    for s1, s2 in focal_pairs:
        pr, pp = pearsonr(df_clean[s1], df_clean[s2])
        sr, sp = spearmanr(df_clean[s1], df_clean[s2])
        paired_findings.append({
            "pair": f"{s1} vs {s2}",
            "stat1": s1,
            "stat2": s2,
            "pearson_r": float(round(pr, 4)),
            "pearson_p": float(pp),
            "pearson_significant": bool(pp < 0.05),
            "spearman_rho": float(round(sr, 4)),
            "spearman_p": float(sp),
            "spearman_significant": bool(sp < 0.05),
        })

    # Primary Type analysis
    type_counts = df_clean["Primary_Type"].value_counts()
    type_bst_means = df_clean.groupby("Primary_Type")["Total"].agg(["count", "mean", "std", "median"]).sort_values("mean", ascending=False)
    type_summary = {}
    for t_name, row in type_bst_means.iterrows():
        type_summary[t_name] = {
            "count": int(row["count"]),
            "percentage": float(round((row["count"] / len(df_clean)) * 100, 2)),
            "mean_total": float(round(row["mean"], 2)),
            "std_total": float(round(row["std"], 2)),
            "median_total": float(round(row["median"], 2)),
        }

    # Power Category breakdown
    cat_counts = df_clean["Power_Category"].value_counts()[categories]
    cat_summary = {}
    for cat in categories:
        sub = df_clean[df_clean["Power_Category"] == cat]
        cat_summary[cat] = {
            "count": int(len(sub)),
            "percentage": float(round((len(sub) / len(df_clean)) * 100, 2)),
            "mean_total": float(round(sub["Total"].mean(), 2)),
            "median_total": float(round(sub["Total"].median(), 2)),
            "stats_mean": {s: float(round(sub[s].mean(), 2)) for s in stats_to_plot},
        }

    # Hypothesis Testing: Independent T-Tests ('Strong' vs 'Legendary')
    strong_df = df_clean[df_clean["Power_Category"] == "Strong"]
    legendary_df = df_clean[df_clean["Power_Category"] == "Legendary"]
    ttest_results = {}
    for stat in stats_to_plot:
        s_vals = strong_df[stat].dropna()
        l_vals = legendary_df[stat].dropna()
        t_stat, p_val = ttest_ind(s_vals, l_vals)
        s_mean = float(round(s_vals.mean(), 2))
        l_mean = float(round(l_vals.mean(), 2))
        diff = float(round(l_mean - s_mean, 2))
        # Cohen's d
        pooled_std = math.sqrt(((len(s_vals) - 1) * s_vals.var() + (len(l_vals) - 1) * l_vals.var()) / (len(s_vals) + len(l_vals) - 2))
        cohens_d = float(round(diff / pooled_std, 4)) if pooled_std > 0 else 0.0

        ttest_results[stat] = {
            "strong_mean": s_mean,
            "legendary_mean": l_mean,
            "difference": diff,
            "t_statistic": float(round(t_stat, 4)),
            "p_value": float(p_val),
            "p_value_formatted": f"{p_val:.4e}",
            "significant": bool(p_val < 0.05),
            "cohens_d": cohens_d,
        }

    # Hypothesis Testing: One-Way ANOVA
    # Total Stats across 4 categories
    anova_groups_total = [df_clean[df_clean["Power_Category"] == cat]["Total"].dropna().values for cat in categories]
    f_total, p_total = f_oneway(*anova_groups_total)
    
    anova_individual = {}
    for stat in stats_to_plot:
        groups = [df_clean[df_clean["Power_Category"] == cat][stat].dropna().values for cat in categories]
        f_val, p_val = f_oneway(*groups)
        anova_individual[stat] = {
            "f_statistic": float(round(f_val, 4)),
            "p_value": float(p_val),
            "p_value_formatted": f"{p_val:.4e}",
            "significant": bool(p_val < 0.05),
        }

    anova_results = {
        "total_stats": {
            "f_statistic": float(round(f_total, 4)),
            "p_value": float(p_total),
            "p_value_formatted": f"{p_total:.4e}",
            "significant": bool(p_total < 0.05),
            "category_means": {cat: float(round(df_clean[df_clean["Power_Category"] == cat]["Total"].mean(), 2)) for cat in categories},
        },
        "individual_stats": anova_individual,
    }

    # K-Means Battle Role Clustering
    features_for_clustering = df_clean[stats_to_plot].values
    scaler = StandardScaler()
    scaled_features = scaler.fit_transform(features_for_clustering)
    
    # 4 clusters corresponding to empirical roles:
    # Wall, Sweeper, Balanced/Tank, Low-Stat
    kmeans = KMeans(n_clusters=4, random_state=42, n_init=10)
    cluster_labels = kmeans.fit_predict(scaled_features)
    df_clean["Cluster"] = cluster_labels

    # Map clusters to roles based on mean centroids
    cluster_means = df_clean.groupby("Cluster")[stats_to_plot].mean()
    cluster_profiles = {}
    for c_id, row in cluster_means.iterrows():
        tot = row.sum()
        spd = row["Speed"]
        atk_agg = (row["Attack"] + row["Sp. Atk"]) / 2.0
        def_agg = (row["Defense"] + row["Sp. Def"]) / 2.0
        hp = row["HP"]
        
        # Identification heuristic:
        if tot < 360:
            role = "Low-Stat Unevolved"
        elif spd > 85 and atk_agg > 90:
            role = "Sweeper (Fast Offensive)"
        elif def_agg > 85 and spd < 70:
            role = "Wall (Defensive Stall)"
        else:
            role = "Balanced / Tank"
            
        cluster_profiles[int(c_id)] = {
            "provisional_role": role,
            "total_mean": float(round(tot, 2)),
            "hp": float(round(hp, 2)),
            "attack": float(round(row["Attack"], 2)),
            "defense": float(round(row["Defense"], 2)),
            "sp_atk": float(round(row["Sp. Atk"], 2)),
            "sp_def": float(round(row["Sp. Def"], 2)),
            "speed": float(round(spd, 2)),
            "count": int(sum(df_clean["Cluster"] == c_id)),
        }

    return {
        "metadata": {
            "title": "Understanding the Relationship between Pokémon Type and its Battle Role",
            "course": "CSD105 Data Science",
            "institution": "Ahmedabad University",
            "instructor": "Professor Hiral Vegda",
            "authors": [
                {"name": "Naman Kumar Sinha", "id": "AU2540195"},
                {"name": "Kabir Chaterjee", "id": "AU23L10004"},
                {"name": "Tithi Modi", "id": "AU2410174"},
                {"name": "Hazikah Kazi", "id": "AU25L20003"},
            ],
            **meta,
        },
        "summary_statistics": stat_summary,
        "strongest_pokemon": top_10[0],
        "top_10_pokemon": top_10,
        "most_common_primary_type": {
            "type": type_counts.index[0],
            "count": int(type_counts.iloc[0]),
            "percentage": float(round((type_counts.iloc[0] / len(df_clean)) * 100, 2)),
        },
        "primary_types": type_summary,
        "power_categories": cat_summary,
        "focal_pair_correlations": paired_findings,
        "pearson_correlation_matrix": pearson_matrix,
        "spearman_correlation_matrix": spearman_matrix,
        "hypothesis_testing": {
            "t_tests_strong_vs_legendary": ttest_results,
            "anova_results": anova_results,
        },
        "clustering_analysis": {
            "k_clusters": 4,
            "profiles": cluster_profiles,
        },
    }


def main():
    print("Loading raw Pokémon data...")
    df_raw = load_raw_data()
    print(f"Loaded {len(df_raw)} records.")

    print("Cleaning data and engineering features...")
    df_clean, meta = clean_and_engineer(df_raw)
    print(f"Clean records: {len(df_clean)}, Removed: {meta['rows_removed']}.")

    # Save cleaned CSV
    cleaned_csv_path = DATA_DIR / "pokemon_database_cleaned.csv"
    df_clean.to_csv(cleaned_csv_path, index=False)
    print(f"Exported cleaned dataset: {cleaned_csv_path}")

    print("Computing statistical analyses and hypothesis tests...")
    results = compute_statistics(df_clean, meta)

    # Save analysis data JSON
    json_path = OUT / "analysis_data.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
    print(f"Exported analysis data: {json_path}")
    print("Done! Total Mean BST:", results["summary_statistics"]["Total"]["mean"])


if __name__ == "__main__":
    main()
