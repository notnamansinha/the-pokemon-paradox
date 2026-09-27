"""Reconcile empirical database values against text narrative claims and tables.

Performs mathematical auditing to ensure zero numerical drift across:
- Record counts (1,220 raw -> 1 dropped -> 1,219 clean)
- Power category partitions (Weak + Average + Strong + Legendary == 1,219)
- Elemental type distribution (18 types summing to 1,219 and 100.0%)
- Summary statistics (Mean: 443.68, Median: 465.0)
- Focal correlation coefficients
- T-test and ANOVA parameters
"""
from pathlib import Path
import json
import math
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "output"
DATA_PATH = OUT / "analysis_data.json"
CLEAN_CSV = ROOT / "data" / "pokemon_database_cleaned.csv"


def reconcile():
    print("Beginning reconciliation audit...")
    data = json.loads(DATA_PATH.read_text(encoding="utf-8"))
    df = pd.read_csv(CLEAN_CSV)

    audits = []

    def audit(label: str, passed: bool, details: str = ""):
        audits.append({"audit": label, "passed": passed, "details": details})
        status = "PASSED" if passed else "FAILED"
        print(f"[{status}] {label}: {details}")

    # 1. Population Counts
    raw_n = data["metadata"]["raw_record_count"]
    clean_n = data["metadata"]["cleaned_record_count"]
    dropped_n = data["metadata"]["rows_removed"]
    audit("Record Count Balance", raw_n - dropped_n == clean_n == len(df) == 1219,
          f"Raw: {raw_n}, Dropped: {dropped_n}, Clean: {clean_n}")

    # 2. Power Categories Partition
    cats = data["power_categories"]
    cat_sum = sum(c["count"] for c in cats.values())
    cat_pct_sum = sum(c["percentage"] for c in cats.values())
    audit("Power Category Sum Parity", cat_sum == 1219 and math.isclose(cat_pct_sum, 100.0, abs_tol=0.2),
          f"Count Sum: {cat_sum}, Pct Sum: {cat_pct_sum:.2f}%")

    # 3. Elemental Type Distribution
    types = data["primary_types"]
    type_sum = sum(t["count"] for t in types.values())
    type_pct_sum = sum(t["percentage"] for t in types.values())
    audit("Type Distribution Sum Parity", type_sum == 1219 and math.isclose(type_pct_sum, 100.0, abs_tol=0.2),
          f"Types: {len(types)}, Count Sum: {type_sum}, Pct Sum: {type_pct_sum:.2f}%")

    # 4. Central Tendency Check
    mean_bst = data["summary_statistics"]["Total"]["mean"]
    med_bst = data["summary_statistics"]["Total"]["median"]
    audit("Total BST Central Tendency", math.isclose(mean_bst, 443.678425, abs_tol=1e-4) and med_bst == 465.0,
          f"Mean: {mean_bst:.4f} (expected 443.6784), Median: {med_bst}")

    # 5. Peak Strongest Entity
    top1 = data["strongest_pokemon"]
    audit("Apex Entity Verification", "Eternatus" in top1["name"] and top1["total"] == 1125.0,
          f"Name: {top1['name']}, Total: {top1['total']}")

    # 6. Focal Pair Correlations
    for pair_data in data["focal_pair_correlations"]:
        p_name = pair_data["pair"]
        r = pair_data["pearson_r"]
        rho = pair_data["spearman_rho"]
        sig = pair_data["pearson_significant"] and pair_data["spearman_significant"]
        audit(f"Correlation: {p_name}", sig and -1.0 <= r <= 1.0 and -1.0 <= rho <= 1.0,
              f"Pearson: {r:.4f}, Spearman: {rho:.4f}")

    # 7. ANOVA Total Stats
    anova_tot = data["hypothesis_testing"]["anova_results"]["total_stats"]
    audit("ANOVA Total Significance", anova_tot["f_statistic"] > 2500 and anova_tot["p_value"] < 1e-100,
          f"F: {anova_tot['f_statistic']:.2f}, p: {anova_tot['p_value_formatted']}")

    # 8. T-Tests Strong vs Legendary
    ttests = data["hypothesis_testing"]["t_tests_strong_vs_legendary"]
    all_sig = all(t["significant"] and t["difference"] > 0 for t in ttests.values())
    audit("All T-Tests Statistically Significant", all_sig,
          f"Tested {len(ttests)} base stats across Strong vs Legendary cohorts.")

    all_passed = all(a["passed"] for a in audits)
    print("\n------------------------------------------------")
    print(f"Reconciliation Summary: {len(audits)} checks performed. All Passed: {all_passed}")
    return all_passed


if __name__ == "__main__":
    reconcile()
