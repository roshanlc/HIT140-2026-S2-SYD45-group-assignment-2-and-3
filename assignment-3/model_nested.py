"""
Nested cross-validation for the two World Cup regression datasets.

Run from the directory containing the `raw/` folder:
    python model_nested.py

This script estimates performance using outer folds. Ridge/Lasso alpha values
are tuned only inside each outer training fold, avoiding tuning on the outer
validation fold. LR2.2 uses match_id groups to keep both teams from a match
in the same fold.
"""
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from sklearn.dummy import DummyRegressor
from sklearn.linear_model import LinearRegression, Ridge, Lasso
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import KFold, GroupKFold, GridSearchCV
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.impute import SimpleImputer

BASE = Path(__file__).resolve().parent
RAW = BASE / "raw"
OUT = BASE / "nested_model_results"
OUT.mkdir(exist_ok=True)

CONFIG = {
    "LR2.1": {
        "file": RAW / "regression_2_1.csv",
        "target": "goal_difference",
        "features": [
            "team_recent_gf", "team_recent_ga", "team_recent_points",
            "team_rest_days", "opponent_recent_gd",
            "opponent_recent_win_rate", "opponent_recent_clean_sheet_rate",
            "is_knockout",
        ],
        "rows": 104,
    },
    "LR2.2": {
        "file": RAW / "regression_2_2.csv",
        "target": "goals_scored",
        "features": [
            "team_recent_gf", "team_recent_ga", "team_recent_points",
            "team_rest_days", "opponent_recent_gf", "opponent_recent_ga",
            "opponent_recent_points", "opponent_rest_days",
        ],
        "rows": 208,
    },
}


def pipeline(model):
    return Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler", StandardScaler()),
        ("model", model),
    ])


def metrics(y, pred):
    return {
        "MAE": mean_absolute_error(y, pred),
        "RMSE": np.sqrt(mean_squared_error(y, pred)),
        "R2": r2_score(y, pred),
    }


def evaluate(label, cfg):
    path = cfg["file"]
    if not path.exists():
        raise FileNotFoundError(f"Cannot find {path}. Run build_datasets.py first.")

    df = pd.read_csv(path)
    if len(df) != cfg["rows"]:
        raise ValueError(f"{label}: expected {cfg['rows']} rows, found {len(df)}")
    needed = cfg["features"] + [cfg["target"]]
    missing = set(needed) - set(df.columns)
    if missing:
        raise ValueError(f"{label}: missing columns: {sorted(missing)}")

    X = df[cfg["features"]].apply(pd.to_numeric, errors="coerce")
    y = pd.to_numeric(df[cfg["target"]], errors="raise").to_numpy()
    if pd.isna(y).any():
        raise ValueError(f"{label}: target has missing values")

    grouped = label == "LR2.2"
    groups = df["match_id"].to_numpy() if grouped else None

    # Outer CV estimates generalisation. Inner CV tunes regularisation.
    outer = GroupKFold(n_splits=5) if grouped else KFold(
        n_splits=5, shuffle=True, random_state=42
    )
    outer_splits = list(
        outer.split(X, y, groups=groups) if grouped else outer.split(X, y)
    )

    oof = {}
    fold_rows = []
    alpha_rows = []
    models = {
        "Mean baseline": None,
        "OLS": pipeline(LinearRegression()),
        "Ridge default": pipeline(Ridge(alpha=1.0)),
        "Lasso default": pipeline(Lasso(alpha=1.0, max_iter=50000)),
        "Ridge tuned": pipeline(Ridge()),
        "Lasso tuned": pipeline(Lasso(max_iter=50000)),
    }
    for name in models:
        oof[name] = np.full(len(df), np.nan)

    # ridge_grid = {"model__alpha": [0.001, 0.01, 0.1, 1, 10, 100, 1000]}
    ridge_grid = {
    "model__alpha": [
        0.01, 0.1, 1, 10, 100, 300, 1000, 3000, 10000
    ]
    }
    lasso_grid = {"model__alpha": [0.001, 0.01, 0.1, 1, 10]}

    for fold, (train_idx, test_idx) in enumerate(outer_splits, start=1):
        X_train, X_test = X.iloc[train_idx], X.iloc[test_idx]
        y_train, y_test = y[train_idx], y[test_idx]
        train_groups = groups[train_idx] if grouped else None

        # Baseline uses training-fold mean only.
        baseline_pred = np.full(len(test_idx), np.mean(y_train))
        oof["Mean baseline"][test_idx] = baseline_pred

        for name in ["OLS", "Ridge default", "Lasso default"]:
            est = models[name]
            est.fit(X_train, y_train)
            oof[name][test_idx] = est.predict(X_test)

        inner = GroupKFold(n_splits=4) if grouped else KFold(
            n_splits=4, shuffle=True, random_state=100 + fold
        )
        inner_splits = list(
            inner.split(X_train, y_train, groups=train_groups)
            if grouped else inner.split(X_train, y_train)
        )

        for name, grid in [("Ridge tuned", ridge_grid), ("Lasso tuned", lasso_grid)]:
            search = GridSearchCV(
                pipeline(Ridge() if name == "Ridge tuned" else Lasso(max_iter=50000)),
                param_grid=grid,
                scoring="neg_mean_absolute_error",
                cv=inner_splits,
                refit=True,
                n_jobs=None,
            )
            search.fit(X_train, y_train)
            oof[name][test_idx] = search.predict(X_test)
            alpha_rows.append({
                "dataset": label,
                "outer_fold": fold,
                "model": name,
                "selected_alpha": search.best_params_["model__alpha"],
                "inner_CV_MAE": -search.best_score_,
            })

    for name, pred in oof.items():
        m = metrics(y, pred)
        fold_rows.append({
            "dataset": label,
            "model": name,
            "outer_CV_MAE": m["MAE"],
            "outer_CV_RMSE": m["RMSE"],
            "outer_CV_R2": m["R2"],
        })

    results = pd.DataFrame(fold_rows).sort_values("outer_CV_MAE")
    results.to_csv(OUT / f"{label.lower().replace('.', '_')}_nested_comparison.csv", index=False)
    pd.DataFrame(alpha_rows).to_csv(
        OUT / f"{label.lower().replace('.', '_')}_selected_alphas.csv", index=False
    )

    pred_df = pd.DataFrame({
        "row_index": np.arange(len(df)),
        "match_id": df["match_id"],
        "actual": y,
    })
    if "team" in df.columns:
        pred_df["team"] = df["team"]
    for name, pred in oof.items():
        pred_df[name] = pred
    pred_df.to_csv(OUT / f"{label.lower().replace('.', '_')}_oof_predictions.csv", index=False)

    # Visualise outer-fold out-of-fold predictions for the best model.
    best_name = results.iloc[0]["model"]
    best_pred = oof[best_name]
    fig, ax = plt.subplots(figsize=(6, 5))
    ax.scatter(y, best_pred, alpha=0.7)
    low = min(float(np.min(y)), float(np.min(best_pred)))
    high = max(float(np.max(y)), float(np.max(best_pred)))
    ax.plot([low, high], [low, high], linestyle="--")
    ax.set_xlabel("Actual target")
    ax.set_ylabel("Out-of-fold prediction")
    ax.set_title(f"{label}: {best_name} (nested CV)")
    fig.tight_layout()
    fig.savefig(OUT / f"{label.lower().replace('.', '_')}_best_model_oof.png", dpi=160)
    plt.close(fig)

    print(f"\n{'=' * 65}\n{label} — nested cross-validation")
    print(results.to_string(index=False))
    print(f"Best by outer-CV MAE: {best_name}")
    print(f"Saved outputs in: {OUT}")
    return results


def main():
    all_results = [evaluate(label, cfg) for label, cfg in CONFIG.items()]
    combined = pd.concat(all_results, ignore_index=True)
    combined.to_csv(OUT / "all_nested_comparisons.csv", index=False)
    print("\nCombined results:")
    print(combined.to_string(index=False))
    print("\nReminder: these metrics estimate performance on unseen rows/matches; they are not in-sample fit scores.")


if __name__ == "__main__":
    main()
