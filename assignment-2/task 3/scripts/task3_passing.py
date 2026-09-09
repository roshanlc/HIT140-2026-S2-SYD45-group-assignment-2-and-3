"""
Task 3 - Passing / Distribution
Author: Sudip Sunar (S398629)

Analytic question
------------------
Did players from the two 2026 FIFA World Cup finalist teams (Spain and
Argentina - Spain won the final 1-0 after extra time) achieve a
significantly higher pass completion rate (Cmp%) than players from teams
that did not reach the final?

Data source
------------
FIFA's official "Player Statistics" page for the 2026 FIFA World Cup
(Distribution -> Passes), https://www.fifa.com/en/tournaments/mens/worldcup/
canadamexicousa2026/statistics/player-statistics?group=gcp_distribution&stat=passes

NOTE ON SOURCE SWITCH: the original plan was to use FBref's "Passing" table.
FBref sits behind a Cloudflare bot-verification challenge that cannot be
solved programmatically (and shouldn't be - see README), so the real data
below was instead pulled from FIFA's own official statistics page, which
publishes the same underlying figures (passes attempted and passing
accuracy %) without a CAPTCHA wall. The variable set is very slightly
different as a result - see "Deviations from the original plan" in the
README.

Main variables used
--------------------
Player    : Player name
Squad     : Team (3-letter code) - used to tag Spain/Argentina as "Finalist"
Pos       : Playing position (GK/DF/MF/FW)
Att       : Total passes attempted in the tournament
Cmp       : Total passes completed (derived: round(Att * Cmp_pct / 100))
Cmp_pct   : Pass completion percentage as published by FIFA (key variable)
Group     : "Finalist" (ESP, ARG) or "Non-finalist" (everyone else)

Method
------
1. Data wrangling      - load the raw CSV, drop missing values, drop
                          duplicate player/squad rows, and filter out
                          players with too few passing involvements for a
                          stable Cmp% (Att < MIN_ATT are dropped).
2. Data preparation     - split into Finalist vs Non-finalist groups, draw a
   & sampling             simple random sample of up to N_SAMPLE=30 players
                          from each group (with a fixed random seed for
                          reproducibility).
3. Descriptive stats    - mean, median, standard deviation, min, max of
                          Cmp% for each sample group.
4. Confidence interval  - 95% CI for the difference in mean Cmp% between
                          the two groups (Welch-Satterthwaite CI).
5. Two-sample t-test    - Welch's t-test (unequal variances) for
   (Welch's)               H0: mean Cmp%(Finalist) = mean Cmp%(Non-finalist)
                          vs H1: mean Cmp%(Finalist) != mean Cmp%(Non-finalist)
                          at alpha = 0.05.

Run
---
    pip install -r requirements.txt
    python task3_passing.py
"""

import numpy as np
import pandas as pd
from scipy import stats

# ----------------------------------------------------------------------
# Configuration
# ----------------------------------------------------------------------
DATA_PATH = "data/wc2026_passing.csv"
MIN_ATT = 20          # drop players with fewer than this many passes attempted
                       # (stand-in for "negligible playing time" - see README;
                       # FIFA's public table does not expose minutes/90s)
N_SAMPLE = 30          # max sample size drawn per group
ALPHA = 0.05
RANDOM_SEED = 398629   # student ID, for a reproducible random sample


def load_and_wrangle(path: str) -> pd.DataFrame:
    """Load the raw passing CSV and clean it."""
    df = pd.read_csv(path)

    required_cols = {"Player", "Squad", "Pos", "Att", "Cmp", "Cmp_pct", "Group"}
    missing = required_cols - set(df.columns)
    if missing:
        raise ValueError(f"Input CSV is missing expected columns: {missing}")

    before = len(df)
    df = df.dropna(subset=["Player", "Squad", "Att", "Cmp_pct", "Group"]).copy()
    df = df.drop_duplicates(subset=["Player", "Squad"])
    df = df[df["Att"] >= MIN_ATT].copy()
    after = len(df)

    print(f"Wrangling: kept {after} of {before} rows "
          f"(dropped missing values, duplicates, and Att < {MIN_ATT}).")
    return df


def sample_groups(df: pd.DataFrame, n: int, seed: int):
    """Draw a simple random sample of up to n players from each group."""
    finalist_pop = df[df["Group"] == "Finalist"]
    nonfinalist_pop = df[df["Group"] == "Non-finalist"]

    finalist_sample = finalist_pop.sample(
        n=min(n, len(finalist_pop)), random_state=seed
    )
    nonfinalist_sample = nonfinalist_pop.sample(
        n=min(n, len(nonfinalist_pop)), random_state=seed
    )

    print(f"\nPopulation sizes after wrangling: "
          f"Finalist = {len(finalist_pop)}, Non-finalist = {len(nonfinalist_pop)}")
    print(f"Sample sizes drawn: "
          f"Finalist = {len(finalist_sample)}, Non-finalist = {len(nonfinalist_sample)}")

    return finalist_sample, nonfinalist_sample


def describe(sample: pd.Series, label: str) -> dict:
    desc = {
        "group": label,
        "n": int(sample.count()),
        "mean": sample.mean(),
        "median": sample.median(),
        "std": sample.std(ddof=1),
        "min": sample.min(),
        "max": sample.max(),
    }
    return desc


def print_descriptives(desc: dict):
    print(f"\n{desc['group']} (n={desc['n']}):")
    print(f"  mean   = {desc['mean']:.2f}%")
    print(f"  median = {desc['median']:.2f}%")
    print(f"  std    = {desc['std']:.2f}")
    print(f"  min    = {desc['min']:.2f}%")
    print(f"  max    = {desc['max']:.2f}%")


def welch_ci_diff_means(a: pd.Series, b: pd.Series, alpha: float):
    """95% CI for the difference in means (a - b), Welch-Satterthwaite df."""
    n1, n2 = a.count(), b.count()
    m1, m2 = a.mean(), b.mean()
    v1, v2 = a.var(ddof=1), b.var(ddof=1)

    diff = m1 - m2
    se = np.sqrt(v1 / n1 + v2 / n2)

    # Welch-Satterthwaite degrees of freedom
    df = (v1 / n1 + v2 / n2) ** 2 / (
        (v1 / n1) ** 2 / (n1 - 1) + (v2 / n2) ** 2 / (n2 - 1)
    )

    t_crit = stats.t.ppf(1 - alpha / 2, df)
    margin = t_crit * se
    return diff, (diff - margin, diff + margin), df


def main():
    df = load_and_wrangle(DATA_PATH)
    finalist_sample, nonfinalist_sample = sample_groups(df, N_SAMPLE, RANDOM_SEED)

    fin_cmp = finalist_sample["Cmp_pct"]
    non_cmp = nonfinalist_sample["Cmp_pct"]

    print("\n" + "=" * 60)
    print("DESCRIPTIVE STATISTICS - Pass completion % (Cmp%)")
    print("=" * 60)
    print_descriptives(describe(fin_cmp, "Finalist (Spain + Argentina)"))
    print_descriptives(describe(non_cmp, "Non-finalist"))

    print("\n" + "=" * 60)
    print("95% CONFIDENCE INTERVAL - difference in mean Cmp%")
    print("=" * 60)
    diff, (lo, hi), df_welch = welch_ci_diff_means(fin_cmp, non_cmp, ALPHA)
    print(f"Mean difference (Finalist - Non-finalist) = {diff:.2f} percentage points")
    print(f"Welch-Satterthwaite df = {df_welch:.1f}")
    print(f"95% CI for the difference = ({lo:.2f}, {hi:.2f})")

    print("\n" + "=" * 60)
    print("TWO-SAMPLE T-TEST (Welch's, unequal variances)")
    print("=" * 60)
    t_stat, p_value = stats.ttest_ind(fin_cmp, non_cmp, equal_var=False)
    print(f"t-statistic = {t_stat:.3f}")
    print(f"p-value     = {p_value:.4f}")
    print(f"alpha       = {ALPHA}")

    print("\nInterpretation:")
    if p_value < ALPHA:
        direction = "higher" if diff > 0 else "lower"
        print(
            f"  p = {p_value:.4f} < alpha = {ALPHA}, so we reject H0.\n"
            f"  Finalist players had a statistically significantly {direction}\n"
            f"  mean pass completion rate than non-finalist players in this sample."
        )
    else:
        print(
            f"  p = {p_value:.4f} >= alpha = {ALPHA}, so we fail to reject H0.\n"
            f"  There is not enough evidence in this sample to conclude that\n"
            f"  finalist and non-finalist players differ in mean pass completion rate."
        )

    if lo <= 0 <= hi:
        print("  (The 95% CI for the difference includes 0, consistent with the test result.)")
    else:
        print("  (The 95% CI for the difference does not include 0, consistent with the test result.)")


if __name__ == "__main__":
    main()
