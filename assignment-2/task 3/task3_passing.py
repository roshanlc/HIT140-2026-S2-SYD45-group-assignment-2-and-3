"""
Author: Sudip Sunar (S398629)
Analytical Task 3

Analytical Question:
Did players from the two 2026 FIFA World Cup finalist teams (Spain and
Argentina - Spain won the final, defeating Argentina) achieve a
significantly higher pass completion rate (%) than players from teams
that did not reach the final?

Data source:
FBref (or FIFA official site) - 2026 FIFA World Cup, "Passing" stats table
(navigate: fbref.com -> 2026 World Cup -> Stats -> Passing)

Main variables (these match FBref's real Passing-table column names):
Player, Squad, Nation, Pos, Age, 90s, Cmp, Att, Cmp%, TotDist, PrgDist
  Cmp  = passes completed
  Att  = passes attempted
  Cmp% = pass completion percentage (this is your key variable)
  Squad = team name -> used to tag Finalist vs Non-finalist
"""

import numpy as np
import pandas as pd
from scipy import stats

ALPHA = 0.05
FINALIST_TEAMS = ["Spain", "Argentina"]   # WC2026 finalists (Spain won)

# ----------------------------------------------------------------------
# STEP 1: LOAD DATA
# ----------------------------------------------------------------------
# Once you've saved your FBref (or FIFA site) export, replace the block
# below with:
#     raw = pd.read_csv("data/wc2026_passing.csv")
#
# For now, placeholder data shaped like a real FBref Passing table export,
# with Spain/Argentina players given a slightly higher completion rate so
# you can see how the pipeline behaves when there IS a real difference.

rng = np.random.default_rng(11)
all_teams = ["USA", "MEX", "CAN", "BRA", "France", "England", "Germany",
             "Portugal", "Netherlands", "Belgium", "Croatia", "Morocco",
             "Japan", "South Korea", "Spain", "Argentina"]
n_players = 320
squads = rng.choice(all_teams, n_players)

raw = pd.DataFrame({
    "Player": [f"Player_{i}" for i in range(1, n_players + 1)],
    "Squad": squads,
    "Pos": rng.choice(["DF", "MF", "FW", "GK"], n_players),
    "90s": np.round(rng.uniform(0.1, 6.0, n_players), 1),
    "Att": rng.integers(5, 400, n_players),
})
# Give finalist-team players a slightly higher mean completion% (placeholder
# behaviour only - replace all of this with your real downloaded data).
is_finalist = raw["Squad"].isin(FINALIST_TEAMS)
base_mean = np.where(is_finalist, 85, 80)
raw["Cmp%"] = np.clip(rng.normal(loc=base_mean, scale=8, size=n_players), 40, 99).round(1)
raw["Cmp"] = (raw["Att"] * raw["Cmp%"] / 100).round().astype(int)

# ----------------------------------------------------------------------
# STEP 2: DATA WRANGLING
# ----------------------------------------------------------------------
passing = raw.dropna(subset=["Cmp%", "Att", "90s", "Squad"]).copy()

# Filter out players with negligible playing time / attempts - their
# completion% is based on too few passes to be a meaningful figure.
MIN_90S = 0.3
MIN_ATT = 10
passing = passing[(passing["90s"] >= MIN_90S) & (passing["Att"] >= MIN_ATT)]

# Create the group label used for comparison
passing["group"] = np.where(passing["Squad"].isin(FINALIST_TEAMS),
                             "Finalist", "Non-finalist")

print(f"Players remaining after wrangling/filtering: {len(passing)}")
print(passing["group"].value_counts())

# ----------------------------------------------------------------------
# STEP 3: DATA PREPARATION AND SAMPLING
# ----------------------------------------------------------------------
# POPULATION: all player passing performances that could occur at
#   World-Cup level of competition, split into two groups: players from
#   finalist teams (Spain, Argentina) and players from all other teams.
# SAMPLE: a simple random sample drawn from each group. Finalist squads
#   only have ~2 teams' worth of players, so we cap the finalist sample
#   at whatever is available and match the non-finalist sample size
#   for a fair-ish comparison (or just use all available finalist players
#   if the group is small).

finalist_group = passing[passing["group"] == "Finalist"]
non_finalist_group = passing[passing["group"] == "Non-finalist"]

n_finalist_sample = min(30, len(finalist_group))
n_nonfinalist_sample = min(30, len(non_finalist_group))

sample_finalist = finalist_group.sample(n=n_finalist_sample, random_state=11)
sample_nonfinalist = non_finalist_group.sample(n=n_nonfinalist_sample, random_state=11)

cmp_finalist = sample_finalist["Cmp%"]
cmp_nonfinalist = sample_nonfinalist["Cmp%"]

# ----------------------------------------------------------------------
# STEP 4: DESCRIPTIVE STATISTICS
# ----------------------------------------------------------------------
print("\n=== Descriptive statistics: pass completion % ===")
for label, data in [("Finalist teams (Spain, Argentina)", cmp_finalist),
                     ("Non-finalist teams", cmp_nonfinalist)]:
    print(f"  {label}: n={len(data)}, mean={data.mean():.2f}%, "
          f"std={data.std(ddof=1):.2f}, median={data.median():.2f}%, "
          f"min={data.min():.2f}%, max={data.max():.2f}%")

# ----------------------------------------------------------------------
# STEP 5: CONFIDENCE INTERVAL (for the DIFFERENCE in means)
# ----------------------------------------------------------------------
mean_diff = cmp_finalist.mean() - cmp_nonfinalist.mean()
n1, n2 = len(cmp_finalist), len(cmp_nonfinalist)
var1, var2 = cmp_finalist.var(ddof=1), cmp_nonfinalist.var(ddof=1)
se_diff = np.sqrt(var1 / n1 + var2 / n2)
# Welch-Satterthwaite degrees of freedom (doesn't assume equal variances)
df_welch = (var1 / n1 + var2 / n2) ** 2 / ((var1 / n1) ** 2 / (n1 - 1) + (var2 / n2) ** 2 / (n2 - 1))
ci_low, ci_high = stats.t.interval(0.95, df=df_welch, loc=mean_diff, scale=se_diff)
print(f"\n95% CI for difference in mean pass completion % "
      f"(Finalist - Non-finalist): ({ci_low:.2f}, {ci_high:.2f})")

# ----------------------------------------------------------------------
# STEP 6: TWO-SAMPLE T-TEST
# ----------------------------------------------------------------------
# H0: mean Cmp% (finalist teams) == mean Cmp% (non-finalist teams)
# H1: mean Cmp% (finalist teams) != mean Cmp% (non-finalist teams)
# equal_var=False -> Welch's t-test (safer default; doesn't assume equal variances)
t_stat, p_value = stats.ttest_ind(cmp_finalist, cmp_nonfinalist, equal_var=False)

print(f"\nTwo-sample t-test (Welch's):")
print(f"  t-statistic = {t_stat:.3f}")
print(f"  p-value     = {p_value:.4f}")

if p_value < ALPHA:
    direction = "higher" if mean_diff > 0 else "lower"
    print(f"  -> p < {ALPHA}: reject H0. Finalist-team players had a "
          f"significantly {direction} pass completion rate than non-finalist players.")
else:
    print(f"  -> p >= {ALPHA}: fail to reject H0. No significant difference "
          f"between finalist and non-finalist players.")

# ----------------------------------------------------------------------
# NEXT STEPS FOR YOU:
# ----------------------------------------------------------------------
# 1. Replace the placeholder `raw` DataFrame in STEP 1 with:
#      raw = pd.read_csv("data/wc2026_passing.csv")
# 2. Check that the Squad column's team names exactly match "Spain" and
#    "Argentina" as written in your real data (FBref/FIFA might use full
#    country names or abbreviations - adjust FINALIST_TEAMS accordingly).
# 3. Check other real column names match (Player, Squad, Pos, 90s, Att, Cmp%).
# 4. Re-run and screenshot the printed output for your slide.
# 5. Write 2-3 plain-English sentences interpreting the result, e.g.:
#    "With p = 0.03, which is below 0.05, we conclude that players from
#     the two finalist teams had a significantly higher pass completion
#     rate than players from non-finalist teams."
