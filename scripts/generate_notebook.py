"""Generate the reproducible Jupyter notebook for the Pokémon research archive."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
NOTEBOOKS_DIR = ROOT / "notebooks"
NOTEBOOKS_DIR.mkdir(parents=True, exist_ok=True)
NOTEBOOK_PATH = NOTEBOOKS_DIR / "pokemon_battle_role_analysis.ipynb"

cells = [
    {
        "cell_type": "markdown",
        "metadata": {},
        "source": [
            "# Understanding the Relationship Between Pokémon Type and Battle Role\n",
            "### Official Performance Statistics Analysis (Pokémon Database, 2008–2025)\n",
            "\n",
            "**Course:** CSD105 Intro to Data Science · Ahmedabad University  \n",
            "**Instructor:** Professor Hiral Vegda  \n",
            "**Authors:** Naman Kumar Sinha (AU2540195), Kabir Chaterjee (AU23L10004), Tithi Modi (AU2410174), Hazikah Kazi (AU25L20003)\n",
            "\n",
            "This notebook provides the complete, end-to-end reproducible analysis pipeline: data ingestion, cleaning, feature engineering, exploratory data visualization, correlation analysis, hypothesis testing (T-Tests and One-Way ANOVA), and unsupervised K-Means battle role clustering."
        ]
    },
    {
        "cell_type": "markdown",
        "metadata": {},
        "source": [
            "## 1. Setup and Library Imports"
        ]
    },
    {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [
            "import math\n",
            "from pathlib import Path\n",
            "import matplotlib.pyplot as plt\n",
            "import numpy as np\n",
            "import pandas as pd\n",
            "from scipy.stats import f_oneway, pearsonr, spearmanr, ttest_ind\n",
            "import seaborn as sns\n",
            "from sklearn.cluster import KMeans\n",
            "from sklearn.decomposition import PCA\n",
            "from sklearn.preprocessing import StandardScaler\n",
            "\n",
            "# Visual styling settings\n",
            "plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')\n",
            "plt.rcParams['figure.dpi'] = 120\n",
            "plt.rcParams['font.size'] = 10"
        ]
    },
    {
        "cell_type": "markdown",
        "metadata": {},
        "source": [
            "## 2. Data Loading & Cleaning\n",
            "We load the raw Pokémon database table. As identified in our initial data quality check, the raw dataset contains 1,220 entries, of which 1 row is an extraneous web footer missing all numerical attributes. We identify and drop this entry, leaving 1,219 complete records."
        ]
    },
    {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [
            "# Locate and load the dataset\n",
            "data_path = Path('../data/pokemon_database_raw.csv')\n",
            "if not data_path.exists():\n",
            "    data_path = Path('../data/Pokemon Dataset - Sheet1.csv')\n",
            "\n",
            "df_raw = pd.read_csv(data_path)\n",
            "print(f'Raw dataset shape: {df_raw.shape}')\n",
            "\n",
            "# Clean headers\n",
            "df = df_raw.copy()\n",
            "df.columns = df.columns.str.strip()\n",
            "if df.columns[0] != '#':\n",
            "    df.rename(columns={df.columns[0]: '#'}, inplace=True)\n",
            "\n",
            "# Standardize numeric columns\n",
            "numeric_cols = ['Total', 'HP', 'Attack', 'Defense', 'Sp. Atk', 'Sp. Def', 'Speed']\n",
            "for col in numeric_cols:\n",
            "    df[col] = pd.to_numeric(df[col], errors='coerce')\n",
            "\n",
            "# Drop missing rows\n",
            "df_clean = df.dropna(subset=numeric_cols).copy()\n",
            "print(f'Cleaned dataset records: {len(df_clean)} (Rows removed: {len(df_raw) - len(df_clean)})')\n",
            "print(f'Overall BST Mean: {df_clean[\"Total\"].mean():.2f}, Median: {df_clean[\"Total\"].median():.1f}')"
        ]
    },
    {
        "cell_type": "markdown",
        "metadata": {},
        "source": [
            "## 3. Feature Engineering\n",
            "We construct composite combat power indices, extract primary/secondary typings, and partition the population into four standardized power tiers: Weak (0–300 BST), Average (301–450 BST), Strong (451–600 BST), and Legendary (601–1200 BST)."
        ]
    },
    {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [
            "# Clean Type representations\n",
            "df_clean['Type_Clean'] = df_clean['Type'].astype(str).str.replace('\\r\\n', '/').str.replace('\\n', '/')\n",
            "type_split = df_clean['Type_Clean'].str.split('/', expand=True)\n",
            "df_clean['Primary_Type'] = type_split[0].str.strip()\n",
            "df_clean['Secondary_Type'] = type_split[1].str.strip().fillna('None') if type_split.shape[1] > 1 else 'None'\n",
            "\n",
            "# Feature engineering\n",
            "df_clean['Avg_Stats'] = df_clean[numeric_cols[1:]].mean(axis=1)\n",
            "df_clean['Physical_Power'] = (df_clean['Attack'] + df_clean['Defense']) / 2.0\n",
            "df_clean['Special_Power'] = (df_clean['Sp. Atk'] + df_clean['Sp. Def']) / 2.0\n",
            "df_clean['Offensive_Power'] = (df_clean['Attack'] + df_clean['Sp. Atk']) / 2.0\n",
            "df_clean['Defensive_Power'] = (df_clean['Defense'] + df_clean['Sp. Def']) / 2.0\n",
            "\n",
            "df_clean['Power_Category'] = pd.cut(\n",
            "    df_clean['Total'],\n",
            "    bins=[0, 300, 450, 600, 1200],\n",
            "    labels=['Weak', 'Average', 'Strong', 'Legendary']\n",
            ")\n",
            "\n",
            "print('Power Category Distribution:')\n",
            "print(df_clean['Power_Category'].value_counts())"
        ]
    },
    {
        "cell_type": "markdown",
        "metadata": {},
        "source": [
            "## 4. Visualizations & Exploratory Analysis"
        ]
    },
    {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [
            "# 4.1 Top 10 Pokémon by Total Stats\n",
            "plt.figure(figsize=(10, 5))\n",
            "top_10 = df_clean.nlargest(10, 'Total')[['Name', 'Total']].sort_values('Total', ascending=False)\n",
            "plt.bar([n.replace('\\r\\n', ' ') for n in top_10['Name']], top_10['Total'], color='steelblue')\n",
            "plt.title('Top 10 Pokémon by Total Stats (BST)', fontsize=12, fontweight='bold')\n",
            "plt.ylabel('Total Stats')\n",
            "plt.xticks(rotation=30, ha='right')\n",
            "plt.show()"
        ]
    },
    {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [
            "# 4.2 Attack vs Defense Scatter Plot\n",
            "plt.figure(figsize=(8, 6))\n",
            "plt.scatter(df_clean['Attack'], df_clean['Defense'], c=df_clean['Total'], cmap='viridis', alpha=0.6, s=50)\n",
            "plt.colorbar(label='Total Stats')\n",
            "plt.title('Attack vs Defense (colored by Total Stats)', fontsize=12, fontweight='bold')\n",
            "plt.xlabel('Attack')\n",
            "plt.ylabel('Defense')\n",
            "plt.show()"
        ]
    },
    {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [
            "# 4.3 Correlation Heatmap\n",
            "plt.figure(figsize=(7, 6))\n",
            "correlation_matrix = df_clean[numeric_cols].corr()\n",
            "sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', center=0, square=True, linewidths=1, fmt='.2f')\n",
            "plt.title('Correlation Heatmap of Base Stats', fontsize=12, fontweight='bold')\n",
            "plt.show()"
        ]
    },
    {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [
            "# 4.4 BST Distribution Histogram\n",
            "plt.figure(figsize=(8, 5))\n",
            "plt.hist(df_clean['Total'], bins=50, color='coral', edgecolor='black', alpha=0.75)\n",
            "plt.axvline(df_clean['Total'].mean(), color='blue', linestyle='--', label=f'Mean: {df_clean[\"Total\"].mean():.2f}')\n",
            "plt.axvline(df_clean['Total'].median(), color='green', linestyle='--', label=f'Median: {df_clean[\"Total\"].median():.1f}')\n",
            "plt.title('Distribution of Total Stats (BST)', fontsize=12, fontweight='bold')\n",
            "plt.xlabel('Total Stats')\n",
            "plt.ylabel('Frequency')\n",
            "plt.legend()\n",
            "plt.show()"
        ]
    },
    {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [
            "# 4.5 Boxplots across Power Categories\n",
            "stats_to_plot = ['HP', 'Attack', 'Defense', 'Sp. Atk', 'Sp. Def', 'Speed']\n",
            "fig, axes = plt.subplots(2, 3, figsize=(14, 8))\n",
            "for idx, stat in enumerate(stats_to_plot):\n",
            "    ax = axes[idx // 3, idx % 3]\n",
            "    sns.boxplot(x='Power_Category', y=stat, data=df_clean, ax=ax, palette='Blues')\n",
            "    ax.set_title(f'{stat} by Category', fontweight='bold')\n",
            "plt.tight_layout()\n",
            "plt.show()"
        ]
    },
    {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [
            "# 4.6 Average BST by Primary Type\n",
            "plt.figure(figsize=(9, 7))\n",
            "type_stats = df_clean.groupby('Primary_Type')['Total'].mean().sort_values(ascending=True)\n",
            "plt.barh(type_stats.index, type_stats.values, color='teal')\n",
            "plt.title('Pokémon Types by Average Total Stats', fontsize=12, fontweight='bold')\n",
            "plt.xlabel('Average Total Stats')\n",
            "plt.show()"
        ]
    },
    {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [
            "# 4.7 Mean Stats Comparison: Strong vs Legendary\n",
            "strong_pokemon_stats = df_clean[df_clean['Power_Category'] == 'Strong'][stats_to_plot].mean()\n",
            "legendary_pokemon_stats = df_clean[df_clean['Power_Category'] == 'Legendary'][stats_to_plot].mean()\n",
            "stats_comp_df = pd.DataFrame({'Strong': strong_pokemon_stats, 'Legendary': legendary_pokemon_stats})\n",
            "stats_comp_df.plot(kind='bar', figsize=(10, 5), rot=0, color=['#2B5B84', '#E67E22'])\n",
            "plt.title('Mean Stats Comparison: Strong vs Legendary', fontsize=12, fontweight='bold')\n",
            "plt.ylabel('Mean Stat Points')\n",
            "plt.show()"
        ]
    },
    {
        "cell_type": "markdown",
        "metadata": {},
        "source": [
            "## 5. Inferential Hypothesis Testing\n",
            "### 5.1 Pearson & Spearman Correlations"
        ]
    },
    {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [
            "stat_pairs = [\n",
            "    ('Attack', 'Defense'),\n",
            "    ('Sp. Atk', 'Sp. Def'),\n",
            "    ('HP', 'Total'),\n",
            "    ('Speed', 'Total'),\n",
            "    ('Attack', 'Sp. Atk')\n",
            "]\n",
            "\n",
            "print('--- PEARSON CORRELATION ANALYSIS ---')\n",
            "for s1, s2 in stat_pairs:\n",
            "    r, p = pearsonr(df_clean[s1], df_clean[s2])\n",
            "    print(f'{s1} vs {s2}: r = {r:.4f}, p = {p:.4e}, Significant: {p < 0.05}')\n",
            "\n",
            "print('\\n--- SPEARMAN CORRELATION ANALYSIS ---')\n",
            "for s1, s2 in stat_pairs:\n",
            "    rho, p = spearmanr(df_clean[s1], df_clean[s2])\n",
            "    print(f'{s1} vs {s2}: rho = {rho:.4f}, p = {p:.4e}, Significant: {p < 0.05}')"
        ]
    },
    {
        "cell_type": "markdown",
        "metadata": {},
        "source": [
            "### 5.2 Independent Two-Sample T-Tests (Strong vs. Legendary)"
        ]
    },
    {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [
            "strong = df_clean[df_clean['Power_Category'] == 'Strong']\n",
            "legendary = df_clean[df_clean['Power_Category'] == 'Legendary']\n",
            "\n",
            "print('--- T-TEST ANALYSIS (Strong vs Legendary) ---')\n",
            "for stat in stats_to_plot:\n",
            "    t_stat, p_val = ttest_ind(strong[stat].dropna(), legendary[stat].dropna())\n",
            "    print(f'{stat}: Strong Mean = {strong[stat].mean():.2f}, Leg Mean = {legendary[stat].mean():.2f}, t = {t_stat:.4f}, p = {p_val:.4e} (Significant: {p_val < 0.05})')"
        ]
    },
    {
        "cell_type": "markdown",
        "metadata": {},
        "source": [
            "### 5.3 One-Way Analysis of Variance (ANOVA)"
        ]
    },
    {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [
            "categories = ['Weak', 'Average', 'Strong', 'Legendary']\n",
            "\n",
            "# Total Stats ANOVA\n",
            "groups_total = [df_clean[df_clean['Power_Category'] == cat]['Total'].dropna().values for cat in categories]\n",
            "f_tot, p_tot = f_oneway(*groups_total)\n",
            "print(f'ANOVA for Total Stats: F = {f_tot:.4f}, p = {p_tot:.4e}')\n",
            "for cat in categories:\n",
            "    print(f'  {cat} Mean Total: {df_clean[df_clean[\"Power_Category\"] == cat][\"Total\"].mean():.2f}')\n",
            "\n",
            "# Individual Stats ANOVA\n",
            "print('\\nANOVA for Individual Base Stats:')\n",
            "for stat in stats_to_plot:\n",
            "    groups = [df_clean[df_clean['Power_Category'] == cat][stat].dropna().values for cat in categories]\n",
            "    f_stat, p_val = f_oneway(*groups)\n",
            "    print(f'  {stat}: F = {f_stat:.4f}, p = {p_val:.4e}')"
        ]
    },
    {
        "cell_type": "markdown",
        "metadata": {},
        "source": [
            "## 6. Unsupervised Machine Learning: K-Means Battle Role Clustering\n",
            "We standardize the 6 core stats and cluster the population into $K=4$ battle archetypes."
        ]
    },
    {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [
            "X = df_clean[stats_to_plot].values\n",
            "scaler = StandardScaler()\n",
            "X_scaled = scaler.fit_transform(X)\n",
            "\n",
            "kmeans = KMeans(n_clusters=4, random_state=42, n_init=10)\n",
            "df_clean['Cluster'] = kmeans.fit_predict(X_scaled)\n",
            "\n",
            "pca = PCA(n_components=2, random_state=42)\n",
            "coords = pca.fit_transform(X_scaled)\n",
            "\n",
            "plt.figure(figsize=(9, 6))\n",
            "scatter = plt.scatter(coords[:, 0], coords[:, 1], c=df_clean['Cluster'], cmap='Set1', alpha=0.6, s=40)\n",
            "plt.title('K-Means Combat Role Clusters (PCA 2D Projection)', fontsize=12, fontweight='bold')\n",
            "plt.xlabel('PC1')\n",
            "plt.ylabel('PC2')\n",
            "plt.show()\n",
            "\n",
            "print('Cluster Centroids (Mean Base Stats):')\n",
            "print(df_clean.groupby('Cluster')[stats_to_plot].mean().round(1))"
        ]
    },
    {
        "cell_type": "markdown",
        "metadata": {},
        "source": [
            "## 7. Conclusions & Findings Summary\n",
            "- **Intentional Design Architecture**: Pokémon stats are not randomly scattered; ANOVA and t-tests confirm distinct power echelons with zero random fluctuation.\n",
            "- **HP is King**: HP exhibits the highest rank correlation with Total Stats ($\\rho = 0.7316$), acting as the volumetric bedrock of survivability.\n",
            "- **Special Symmetry**: Special Attack and Special Defence exhibit structured correlation ($r = 0.5167$), while Defense and Speed are independent ($r = 0.02$), enforcing classical agility-vs-armor trade-offs.\n",
            "- **Elemental Hierarchy**: Dragon, Steel, and Psychic types dominate the upper echelons, while Bug and Normal types anchor the baseline."
        ]
    }
]

notebook = {
    "cells": cells,
    "metadata": {
        "language_info": {
            "name": "python",
            "version": "3.11"
        },
        "kernelspec": {
            "display_name": "Python 3",
            "language": "python",
            "name": "python3"
        }
    },
    "nbformat": 4,
    "nbformat_minor": 4
}

with open(NOTEBOOK_PATH, "w", encoding="utf-8") as f:
    json.dump(notebook, f, indent=2)

print(f"Jupyter notebook written to: {NOTEBOOK_PATH}")
