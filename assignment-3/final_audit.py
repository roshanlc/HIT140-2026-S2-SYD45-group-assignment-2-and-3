
    
  
"""Final pre-submission audit for Objective 2.

Run from the project code directory:
    python final_audit.py

Checks dataset structure, missing values, predictor overlap, LR2.2 paired rows,
saved nested-CV result files, and that model_nested.py includes the expanded
Ridge alpha grid. It does not prove that external source data are accurate;
cite and verify those sources separately.
"""
from pathlib import Path
import sys
import pandas as pd

BASE = Path(__file__).resolve().parent
RAW = BASE / "raw"
RESULTS = BASE / "nested_model_results"
MODEL_SCRIPT = BASE / "model_nested.py"

P21 = [
    "team_recent_gf", "team_recent_ga", "team_recent_points",
    "team_rest_days", "opponent_recent_gd", "opponent_recent_win_rate",
    "opponent_recent_clean_sheet_rate", "is_knockout",
]
P22 = [
    "team_recent_gf", "team_recent_ga", "team_recent_points",
    "team_rest_days", "opponent_recent_gf", "opponent_recent_ga",
    "opponent_recent_points", "opponent_rest_days",
]
errors = []
warnings = []

def check(condition, success, failure):
    if condition:
        print(f"PASS: {success}")
    else:
        print(f"FAIL: {failure}")
        errors.append(failure)

def main():
    p21 = RAW / "regression_2_1.csv"
    p22 = RAW / "regression_2_2.csv"

    check(p21.exists(), "LR2.1 dataset exists", f"Missing {p21}")
    check(p22.exists(), "LR2.2 dataset exists", f"Missing {p22}")
    if not p21.exists() or not p22.exists():
        sys.exit(1)

    d21 = pd.read_csv(p21)
    d22 = pd.read_csv(p22)

    check(len(d21) == 104, "LR2.1 has 104 rows", f"LR2.1 has {len(d21)} rows")
    check(len(d22) == 208, "LR2.2 has 208 rows", f"LR2.2 has {len(d22)} rows")
    check(set(P21).issubset(d21.columns), "LR2.1 has all eight expected predictors",
          "LR2.1 is missing expected predictors")
    check(set(P22).issubset(d22.columns), "LR2.2 has all eight expected predictors",
          "LR2.2 is missing expected predictors")

    if set(P21).issubset(d21.columns):
        check(len([c for c in d21.columns if c not in {"match_id", "goal_difference"}]) == 8,
              "LR2.1 contains exactly eight predictors (excluding IDs and target)",
              "LR2.1 predictor count is not exactly eight")
        check(not d21[P21].isna().any().any(), "LR2.1 predictors have no missing values",
              "LR2.1 has missing predictor values")
    if set(P22).issubset(d22.columns):
        check(len([c for c in d22.columns if c not in {"match_id", "team", "goals_scored"}]) == 8,
              "LR2.2 contains exactly eight predictors (excluding IDs and target)",
              "LR2.2 predictor count is not exactly eight")
        check(not d22[P22].isna().any().any(), "LR2.2 predictors have no missing values",
              "LR2.2 has missing predictor values")

    shared = set(P21) & set(P22)
    check(len(shared) == 4, f"Exactly four predictors shared: {sorted(shared)}",
          f"Expected exactly four shared predictors, found {len(shared)}: {sorted(shared)}")

    check("goal_difference" in d21.columns and not d21["goal_difference"].isna().any(),
          "LR2.1 target exists and has no missing values", "LR2.1 target missing or incomplete")
    check("goals_scored" in d22.columns and not d22["goals_scored"].isna().any(),
          "LR2.2 target exists and has no missing values", "LR2.2 target missing or incomplete")

    if "match_id" in d22.columns:
        counts = d22.groupby("match_id").size()
        check(len(counts) == 104 and (counts == 2).all(),
              "LR2.2 has exactly two team rows for each of 104 matches",
              "LR2.2 match_id grouping is not exactly two rows per match")

    check(MODEL_SCRIPT.exists(), "Nested-CV script exists", f"Missing {MODEL_SCRIPT}")
    if MODEL_SCRIPT.exists():
        code = MODEL_SCRIPT.read_text(encoding="utf-8")
        check("300" in code and "10000" in code,
              "Nested-CV script appears to include expanded Ridge alpha candidates",
              "Check model_nested.py: expanded Ridge alpha grid may not be present")

    expected_outputs = [
        "lr2_1_nested_comparison.csv",
        "lr2_2_nested_comparison.csv",
        "lr2_1_oof_predictions.csv",
        "lr2_2_oof_predictions.csv",
        "lr2_1_selected_alphas.csv",
        "lr2_2_selected_alphas.csv",
        "all_nested_comparisons.csv",
        "lr2_1_best_model_oof.png",
        "lr2_2_best_model_oof.png",
    ]
    missing_outputs = [name for name in expected_outputs if not (RESULTS / name).exists()]
    check(not missing_outputs, "Expected nested-CV result files and plots exist",
          f"Missing nested-CV outputs: {missing_outputs}")

    if not missing_outputs:
        r21 = pd.read_csv(RESULTS / "lr2_1_nested_comparison.csv")
        r22 = pd.read_csv(RESULTS / "lr2_2_nested_comparison.csv")
        print("\nSaved nested-CV results:")
        print(r21.to_string(index=False))
        print(r22.to_string(index=False))
        print("\nNote: compare these saved tables with the final terminal output.")
        print("If they differ, rerun model_nested.py and keep the outputs from that run.")

    print("\nSOURCE CHECK (manual):")
    print("- Record the URL, retrieval date, and fields used for the 2026 fixture dataset.")
    print("- Cite the international-results dataset used to calculate historical form.")
    print("- Confirm each feature uses only matches strictly before the fixture date.")
    print("- Keep a copy of the final scripts and both generated CSV datasets in the code repository.")

    if errors:
        print(f"\nAUDIT FAILED: {len(errors)} issue(s) need fixing.")
        sys.exit(1)
    print("\nSTRUCTURAL AUDIT PASSED. Complete the manual source checks before submission.")

if __name__ == "__main__":
    main()

