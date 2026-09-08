import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
from scipy import stats


# ============================================================
# TASK 1 - STATISTICAL ANALYSIS
# ============================================================
#
# Analytical Question:
#
# Was there a significant difference in attacking performance
# between Argentina's forward players and midfielders at the
# 2026 FIFA World Cup?
#
# Main variable:
# G+A per 90
#
# Groups:
# FW = Forwards
# MF = Midfielders
#
# ============================================================


# ============================================================
# 1. FILE LOCATIONS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent

input_file = (
    BASE_DIR /
    "output" /
    "argentina_analysis.csv"
)

output_dir = (
    BASE_DIR /
    "output"
)


# ============================================================
# 2. LOAD CLEAN ANALYSIS DATA
# ============================================================

df = pd.read_csv(
    input_file
)


print("=" * 70)
print("TASK 1 STATISTICAL ANALYSIS")
print("=" * 70)

print(
    f"Total analysis observations: {len(df)}"
)


# ============================================================
# 3. DATA PREPARATION AND SAMPLE
# ============================================================

fw = df[
    df["Pos"] == "FW"
]["ga_per90"].dropna()

mf = df[
    df["Pos"] == "MF"
]["ga_per90"].dropna()


print("\n" + "=" * 70)
print("DATA PREPARATION")
print("=" * 70)

print(
    f"Forwards: {len(fw)}"
)

print(
    f"Midfielders: {len(mf)}"
)


# ============================================================
# 4. DESCRIPTIVE STATISTICS
# ============================================================

descriptive = (
    df
    .groupby("Pos")["ga_per90"]
    .agg(
        n="count",
        mean="mean",
        median="median",
        standard_deviation="std",
        minimum="min",
        maximum="max"
    )
    .round(3)
)


print("\n" + "=" * 70)
print("DESCRIPTIVE STATISTICS")
print("=" * 70)

print(
    descriptive
)


descriptive_file = (
    output_dir /
    "descriptive_statistics.csv"
)

descriptive.to_csv(
    descriptive_file
)


# ============================================================
# 5. CONFIDENCE INTERVAL FUNCTION
# ============================================================

def calculate_ci(
    values,
    confidence=0.95
):

    n = len(values)

    mean = values.mean()

    standard_error = stats.sem(
        values
    )

    t_critical = stats.t.ppf(
        (1 + confidence) / 2,
        n - 1
    )

    margin = (
        t_critical *
        standard_error
    )

    lower = mean - margin

    upper = mean + margin

    return (
        n,
        mean,
        lower,
        upper
    )


# ============================================================
# 6. CALCULATE 95% CONFIDENCE INTERVALS
# ============================================================

ci_results = []


for position in ["FW", "MF"]:

    values = df[
        df["Pos"] == position
    ]["ga_per90"].dropna()

    n, mean, lower, upper = (
        calculate_ci(values)
    )

    ci_results.append({

        "Position": position,

        "n": n,

        "Mean_GA_per90": mean,

        "CI_Lower_95": lower,

        "CI_Upper_95": upper
    })


ci_df = pd.DataFrame(
    ci_results
).round(3)


print("\n" + "=" * 70)
print("95% CONFIDENCE INTERVALS")
print("=" * 70)

print(
    ci_df.to_string(index=False)
)


ci_file = (
    output_dir /
    "confidence_intervals.csv"
)

ci_df.to_csv(
    ci_file,
    index=False
)


# ============================================================
# 7. TWO-SAMPLE WELCH T-TEST
# ============================================================

print("\n" + "=" * 70)
print("TWO-SAMPLE T-TEST")
print("=" * 70)


# H0:
# Mean FW G+A/90 = Mean MF G+A/90
#
# H1:
# Mean FW G+A/90 != Mean MF G+A/90


t_statistic, p_value = stats.ttest_ind(
    fw,
    mf,
    equal_var=False
)


alpha = 0.05


if p_value < alpha:

    decision = "Reject H0"

else:

    decision = "Fail to reject H0"


print(
    f"Forward mean: {fw.mean():.3f}"
)

print(
    f"Midfielder mean: {mf.mean():.3f}"
)

print(
    f"t-statistic: {t_statistic:.3f}"
)

print(
    f"p-value: {p_value:.4f}"
)

print(
    f"Significance level: {alpha}"
)

print(
    f"Decision: {decision}"
)


# ============================================================
# 8. SAVE T-TEST RESULTS
# ============================================================

test_results = pd.DataFrame([{

    "FW_n": len(fw),

    "MF_n": len(mf),

    "FW_mean": fw.mean(),

    "MF_mean": mf.mean(),

    "t_statistic": t_statistic,

    "p_value": p_value,

    "alpha": alpha,

    "decision": decision
}])


test_file = (
    output_dir /
    "hypothesis_test.csv"
)

test_results.to_csv(
    test_file,
    index=False
)


# ============================================================
# 9. OUTLIER CHECK
# ============================================================

print("\n" + "=" * 70)
print("OUTLIER CHECK")
print("=" * 70)


for position in ["FW", "MF"]:

    values = df[
        df["Pos"] == position
    ]["ga_per90"]

    q1 = values.quantile(0.25)

    q3 = values.quantile(0.75)

    iqr = q3 - q1

    lower = q1 - 1.5 * iqr

    upper = q3 + 1.5 * iqr

    outliers = values[
        (values < lower) |
        (values > upper)
    ]

    print(f"\n{position}")

    print(
        f"Q1: {q1:.3f}"
    )

    print(
        f"Q3: {q3:.3f}"
    )

    print(
        f"IQR: {iqr:.3f}"
    )

    print(
        f"Lower boundary: {lower:.3f}"
    )

    print(
        f"Upper boundary: {upper:.3f}"
    )

    if len(outliers) == 0:

        print(
            "No potential outliers."
        )

    else:

        print(
            "Potential outlier values:"
        )

        print(
            outliers.to_string()
        )


# ============================================================
# 10. BOXPLOT
# ============================================================

plt.figure(
    figsize=(8, 6)
)

plt.boxplot(
    [fw, mf],
    tick_labels=[
        "Forwards",
        "Midfielders"
    ]
)

plt.title(
    "Goal Contributions per 90: "
    "Forwards vs Midfielders"
)

plt.xlabel(
    "Player Position"
)

plt.ylabel(
    "G+A per 90"
)

plt.tight_layout()


boxplot_file = (
    output_dir /
    "FW_MF_boxplot.png"
)

plt.savefig(
    boxplot_file,
    dpi=300,
    bbox_inches="tight"
)

plt.show()


# ============================================================
# 11. MEAN + 95% CI GRAPH
# ============================================================

positions = [
    "FW",
    "MF"
]

means = []

lower_errors = []

upper_errors = []


for position in positions:

    values = df[
        df["Pos"] == position
    ]["ga_per90"].dropna()

    mean = values.mean()

    standard_error = stats.sem(
        values
    )

    t_critical = stats.t.ppf(
        0.975,
        len(values) - 1
    )

    margin = (
        t_critical *
        standard_error
    )

    lower = mean - margin

    upper = mean + margin

    means.append(mean)

    lower_errors.append(
        mean - lower
    )

    upper_errors.append(
        upper - mean
    )


plt.figure(
    figsize=(8, 6)
)

plt.errorbar(
    positions,
    means,
    yerr=[
        lower_errors,
        upper_errors
    ],
    fmt="o",
    capsize=6
)

plt.title(
    "Average Goal Contributions per 90 "
    "by Position (95% CI)"
)

plt.xlabel(
    "Player Position"
)

plt.ylabel(
    "Mean G+A per 90"
)

plt.tight_layout()


ci_graph_file = (
    output_dir /
    "FW_MF_mean_95CI.png"
)

plt.savefig(
    ci_graph_file,
    dpi=300,
    bbox_inches="tight"
)

plt.show()


# ============================================================
# 12. FINAL SUMMARY
# ============================================================

print("\n" + "=" * 70)
print("FINAL SUMMARY")
print("=" * 70)

print(
    f"FW mean G+A/90: {fw.mean():.3f}"
)

print(
    f"MF mean G+A/90: {mf.mean():.3f}"
)

print(
    f"Welch t-statistic: {t_statistic:.3f}"
)

print(
    f"p-value: {p_value:.4f}"
)

print(
    f"Decision: {decision}"
)

print("\nAnalysis completed successfully.")