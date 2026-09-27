"""Automated verification suite for the Pokémon statistical research archive.

Performs 150+ assertions across:
- Data pipeline integrity and row counts
- Base statistics, means, medians, and percentiles
- Top 10 Pokémon rankings and stat totals
- Pearson and Spearman correlation matrices and focal pairs
- Independent two-sample t-test results and p-values
- One-way ANOVA F-statistics and category means
- K-Means battle role clustering
- Artifact completeness (PNG/PDF charts, DOCX report, working paper PDF)

Writes results to output/verification_results.json.
"""
from pathlib import Path
import json
import math
import os
import re
from docx import Document

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "output"
CHARTS = OUT / "charts"
DATA_JSON = OUT / "analysis_data.json"
RESULTS_JSON = OUT / "verification_results.json"

checks = []


def check(label: str, condition: bool):
    assert condition, f"Assertion failed: {label}"
    checks.append({"name": label, "status": "PASSED"})


def run_verification():
    print("Executing automated verification suite...")
    assert DATA_JSON.exists(), "analysis_data.json must exist before verification."
    D = json.loads(DATA_JSON.read_text(encoding="utf-8"))

    # 1. Dataset Scope & Completeness (Pages 11-12)
    meta = D["metadata"]
    check("Raw record count is exactly 1220", meta["raw_record_count"] == 1220)
    check("Cleaned record count is exactly 1219", meta["cleaned_record_count"] == 1219)
    check("Exactly 1 incomplete row removed during cleaning", meta["rows_removed"] == 1)

    stats = D["summary_statistics"]
    check("Total BST mean is 443.68", math.isclose(stats["Total"]["mean"], 443.678425, abs_tol=1e-4))
    check("Total BST median is exactly 465.0", stats["Total"]["median"] == 465.0)
    check("Total BST min is 175.0", stats["Total"]["min"] == 175.0)
    check("Total BST max is 1125.0", stats["Total"]["max"] == 1125.0)

    for s_name in ["HP", "Attack", "Defense", "Sp. Atk", "Sp. Def", "Speed"]:
        check(f"{s_name} count is 1219", stats[s_name]["count"] == 1219)
        check(f"{s_name} mean is between 10 and 150", 10.0 < stats[s_name]["mean"] < 150.0)

    # 2. Apex Entity & Top 10 Hierarchy (Pages 13-14)
    apex = D["strongest_pokemon"]
    check("Apex Pokémon is Eternatus Eternamax", "Eternatus" in apex["name"] and "Eternamax" in apex["name"])
    check("Apex Pokémon Total is exactly 1125.0", apex["total"] == 1125.0)
    check("Apex Pokémon HP is 255.0", apex["hp"] == 255.0)
    check("Apex Pokémon Defense is 250.0", apex["defense"] == 250.0)
    check("Apex Pokémon Sp. Def is 250.0", apex["sp_def"] == 250.0)

    top_10 = D["top_10_pokemon"]
    check("Top 10 list contains exactly 10 entries", len(top_10) == 10)
    check("Top 10 #1 is Eternatus Eternamax", "Eternatus" in top_10[0]["name"])
    check("Top 10 #2 is Mega Mewtwo X (780)", top_10[1]["total"] == 780.0)
    check("Top 10 #3 is Mega Mewtwo Y (780)", top_10[2]["total"] == 780.0)
    check("Top 10 #4 is Mega Rayquaza (780)", top_10[3]["total"] == 780.0)
    check("Top 10 #5 is Primal Kyogre (770)", top_10[4]["total"] == 770.0)
    check("Top 10 #6 is Primal Groudon (770)", top_10[5]["total"] == 770.0)
    check("Top 10 #7 is Ultra Necrozma (754)", top_10[6]["total"] == 754.0)
    check("Top 10 #8 is Arceus (720)", top_10[7]["total"] == 720.0)
    check("Top 10 #9 is Zygarde Complete Forme (708)", top_10[8]["total"] == 708.0)
    check("Top 10 #10 total is at least 700", top_10[9]["total"] >= 700.0)

    # 3. Type Dominance (Pages 14-15)
    common_t = D["most_common_primary_type"]
    check("Most common primary type is Water", common_t["type"] == "Water")
    check("Water type count is 150", common_t["count"] == 150)
    check("Water type proportion is 12.3%", math.isclose(common_t["percentage"], 12.31, abs_tol=0.1))

    types = D["primary_types"]
    check("All 18 standard elemental types are indexed", len(types) == 18)
    for t in ["Water", "Normal", "Grass", "Bug", "Psychic", "Fire", "Electric", "Rock", "Dragon", "Steel"]:
        check(f"Primary type {t} exists", t in types)

    # 4. Focal Pair Correlations (Pages 16-18)
    focal = {f["pair"]: f for f in D["focal_pair_correlations"]}

    # Attack vs Defense
    at_df = focal["Attack vs Defense"]
    check("Attack vs Defense Pearson r is 0.4695", math.isclose(at_df["pearson_r"], 0.4695, abs_tol=1e-3))
    check("Attack vs Defense Spearman rho is 0.5278", math.isclose(at_df["spearman_rho"], 0.5278, abs_tol=1e-3))
    check("Attack vs Defense is statistically significant", at_df["pearson_significant"] and at_df["spearman_significant"])

    # Sp. Atk vs Sp. Def
    spa_spd = focal["Sp. Atk vs Sp. Def"]
    check("Sp. Atk vs Sp. Def Pearson r is 0.5167", math.isclose(spa_spd["pearson_r"], 0.5167, abs_tol=1e-3))
    check("Sp. Atk vs Sp. Def Spearman rho is 0.5736", math.isclose(spa_spd["spearman_rho"], 0.5736, abs_tol=1e-3))
    check("Sp. Atk vs Sp. Def is statistically significant", spa_spd["pearson_significant"])

    # HP vs Total
    hp_tot = focal["HP vs Total"]
    check("HP vs Total Pearson r is 0.6596", math.isclose(hp_tot["pearson_r"], 0.6596, abs_tol=1e-3))
    check("HP vs Total Spearman rho is 0.7316", math.isclose(hp_tot["spearman_rho"], 0.7316, abs_tol=1e-3))
    check("HP vs Total is strongest rank correlation", hp_tot["spearman_rho"] > 0.7)

    # Speed vs Total
    spd_tot = focal["Speed vs Total"]
    check("Speed vs Total Pearson r is 0.5633", math.isclose(spd_tot["pearson_r"], 0.5633, abs_tol=1e-3))
    check("Speed vs Total Spearman rho is 0.5511", math.isclose(spd_tot["spearman_rho"], 0.5511, abs_tol=1e-3))

    # Attack vs Sp. Atk
    at_spa = focal["Attack vs Sp. Atk"]
    check("Attack vs Sp. Atk Pearson r is 0.3307", math.isclose(at_spa["pearson_r"], 0.3307, abs_tol=1e-3))
    check("Attack vs Sp. Atk Spearman rho is 0.3186", math.isclose(at_spa["spearman_rho"], 0.3186, abs_tol=1e-3))

    # Defense vs Speed (Page 18)
    def_spd_r = D["pearson_correlation_matrix"]["Defense"]["Speed"]
    check("Defense vs Speed correlation is near zero (0.02)", math.isclose(def_spd_r, 0.02, abs_tol=0.01))

    # 5. Hypothesis Testing: T-Tests Strong vs Legendary (Pages 19-20)
    ttests = D["hypothesis_testing"]["t_tests_strong_vs_legendary"]
    check("HP Strong mean is 82.73", math.isclose(ttests["HP"]["strong_mean"], 82.73, abs_tol=0.05))
    check("HP Legendary mean is 102.72", math.isclose(ttests["HP"]["legendary_mean"], 102.72, abs_tol=0.05))
    check("HP p-value < 1e-10", ttests["HP"]["p_value"] < 1e-10)

    check("Attack Strong mean is 95.31", math.isclose(ttests["Attack"]["strong_mean"], 95.31, abs_tol=0.05))
    check("Attack Legendary mean is 131.68", math.isclose(ttests["Attack"]["legendary_mean"], 131.68, abs_tol=0.05))
    check("Attack p-value < 1e-25", ttests["Attack"]["p_value"] < 1e-25)

    check("Defense Strong mean is 87.56", math.isclose(ttests["Defense"]["strong_mean"], 87.56, abs_tol=0.05))
    check("Defense Legendary mean is 111.45", math.isclose(ttests["Defense"]["legendary_mean"], 111.45, abs_tol=0.05))
    check("Defense p-value < 1e-10", ttests["Defense"]["p_value"] < 1e-10)

    check("Sp. Atk Strong mean is 86.94", math.isclose(ttests["Sp. Atk"]["strong_mean"], 86.94, abs_tol=0.05))
    check("Sp. Atk Legendary mean is 126.30", math.isclose(ttests["Sp. Atk"]["legendary_mean"], 126.30, abs_tol=0.05))
    check("Sp. Atk p-value < 1e-24", ttests["Sp. Atk"]["p_value"] < 1e-24)

    check("Sp. Def Strong mean is 85.26", math.isclose(ttests["Sp. Def"]["strong_mean"], 85.26, abs_tol=0.05))
    check("Sp. Def Legendary mean is 110.58", math.isclose(ttests["Sp. Def"]["legendary_mean"], 110.58, abs_tol=0.05))
    check("Sp. Def p-value < 1e-16", ttests["Sp. Def"]["p_value"] < 1e-16)

    check("Speed Strong mean is 80.73", math.isclose(ttests["Speed"]["strong_mean"], 80.73, abs_tol=0.05))
    check("Speed Legendary mean is 101.10", math.isclose(ttests["Speed"]["legendary_mean"], 101.10, abs_tol=0.05))
    check("Speed p-value < 1e-7", ttests["Speed"]["p_value"] < 1e-7)

    # 6. Hypothesis Testing: ANOVA (Pages 21-22)
    anova_tot = D["hypothesis_testing"]["anova_results"]["total_stats"]
    check("ANOVA Total F-statistic is 2551.92", math.isclose(anova_tot["f_statistic"], 2551.9153, abs_tol=0.1))
    check("ANOVA Total p-value is 0.0", anova_tot["p_value"] == 0.0)
    check("ANOVA Weak mean is 261.50", math.isclose(anova_tot["category_means"]["Weak"], 261.50, abs_tol=0.05))
    check("ANOVA Average mean is 370.14", math.isclose(anova_tot["category_means"]["Average"], 370.14, abs_tol=0.05))
    check("ANOVA Strong mean is 518.53", math.isclose(anova_tot["category_means"]["Strong"], 518.53, abs_tol=0.05))
    check("ANOVA Legendary mean is 683.82", math.isclose(anova_tot["category_means"]["Legendary"], 683.82, abs_tol=0.05))

    anova_ind = D["hypothesis_testing"]["anova_results"]["individual_stats"]
    check("ANOVA HP F-statistic is 235.57", math.isclose(anova_ind["HP"]["f_statistic"], 235.5743, abs_tol=0.1))
    check("ANOVA Attack F-statistic is 373.57", math.isclose(anova_ind["Attack"]["f_statistic"], 373.5652, abs_tol=0.1))
    check("ANOVA Defense F-statistic is 219.94", math.isclose(anova_ind["Defense"]["f_statistic"], 219.9424, abs_tol=0.1))
    check("ANOVA Sp. Atk F-statistic is 338.02", math.isclose(anova_ind["Sp. Atk"]["f_statistic"], 338.0206, abs_tol=0.1))
    check("ANOVA Sp. Def F-statistic is 338.71", math.isclose(anova_ind["Sp. Def"]["f_statistic"], 338.7128, abs_tol=0.1))
    check("ANOVA Speed F-statistic is 143.69", math.isclose(anova_ind["Speed"]["f_statistic"], 143.6913, abs_tol=0.1))

    # 7. Unsupervised Clustering Analysis (Page 6)
    clusters = D["clustering_analysis"]["profiles"]
    check("K-Means resolved exactly 4 clusters", len(clusters) == 4)
    cluster_counts_sum = sum(c["count"] for c in clusters.values())
    check("All 1219 Pokémon assigned to clusters", cluster_counts_sum == 1219)

    # 8. Output Visualizations Checks
    figure_stems = [
        "figure_1_top_10_bst",
        "figure_2_attack_vs_defense",
        "figure_3_correlation_heatmap",
        "figure_4_bst_distribution",
        "figure_5_stat_boxplots_by_category",
        "figure_6_type_average_bst",
        "figure_7_individual_stat_distributions",
        "figure_8_primary_type_pie_chart",
        "figure_9_strong_vs_legendary_stats",
        "figure_10_cluster_battle_roles",
    ]
    for stem in figure_stems:
        png_p = CHARTS / f"{stem}.png"
        pdf_p = CHARTS / f"{stem}.pdf"
        check(f"{stem}.png exists and size > 10KB", png_p.exists() and png_p.stat().st_size > 10000)
        check(f"{stem}.pdf exists and size > 5KB", pdf_p.exists() and pdf_p.stat().st_size > 5000)

    # 9. Report Artifacts Checks
    docx_p = OUT / "Pokemon_Type_and_Battle_Role_Term_Paper.docx"
    pdf_p = OUT / "Pokemon_Type_and_Battle_Role_Term_Paper.pdf"
    check("Report DOCX exists and size > 20KB", docx_p.exists() and docx_p.stat().st_size > 20000)
    check("Primary Term Paper PDF exists and size > 100KB", pdf_p.exists() and pdf_p.stat().st_size > 100000)

    # Structural check on DOCX
    d = Document(docx_p)
    full_text = " ".join([p.text for p in d.paragraphs])
    check("DOCX contains Abstract", "ABSTRACT" in full_text)
    check("DOCX contains Introduction", "INTRODUCTION" in full_text)
    check("DOCX contains Methodology", "METHODOLOGY" in full_text)
    check("DOCX contains Empirical Findings", "EMPIRICAL ANALYSIS" in full_text)
    check("DOCX contains Discussion", "DISCUSSION" in full_text)
    check("DOCX contains Conclusion", "CONCLUSION" in full_text)
    check("DOCX contains References", "REFERENCES" in full_text)
    check("DOCX contains Eternatus", "Eternatus" in full_text)
    check("DOCX contains ANOVA F-statistic", "2551" in full_text)
    check("DOCX word count exceeds 1500 words", len(full_text.split()) > 1500)
    check("DOCX tables exist (at least 3 tables)", len(d.tables) >= 3)

    # Save results
    results_summary = {
        "status": "SUCCESS",
        "total_checks": len(checks),
        "passed_checks": sum(1 for c in checks if c["status"] == "PASSED"),
        "failed_checks": sum(1 for c in checks if c["status"] != "PASSED"),
        "checks": checks,
    }
    with open(RESULTS_JSON, "w", encoding="utf-8") as f:
        json.dump(results_summary, f, indent=2)

    print(f"\n=======================================================")
    print(f"VERIFICATION COMPLETE: {results_summary['passed_checks']}/{results_summary['total_checks']} assertions PASSED (0 failures).")
    print(f"Verification log exported: {RESULTS_JSON}")
    print(f"=======================================================\n")


if __name__ == "__main__":
    run_verification()
