# HIT140 Foundation of Data Science - Assessment 2
# Task 2: Do midfielders commit more fouls per 90 minutes than defenders?
# Shrijan Neupane
#
# Data: FBref Player Miscellaneous Stats, FIFA World Cup 2026
# https://fbref.com/en/comps/1/misc/World-Cup-Stats
#
# Note: FBref gave me this table in "per 90 minutes" mode so the Fls
# column is already a rate, not a count. Messi has Fld = 2.44 and you
# cannot be fouled 2.44 times, so that is how I worked it out.
#
# I followed the 4 step process.

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy import stats

# seed so my random sample is the same every time I run this
np.random.seed(42)
SEED = 42

blue = "#2a78d6"    # defenders
orange = "#eb6834"  # midfielders


# ==============================================================
# STEP 1: STATE

print("STEP 1: STATE")
print("Do midfielders commit more fouls per 90 minutes than defenders")
print("at the FIFA World Cup 2026?")
print()


# ==============================================================
# DATA WRANGLING

# The FBref file has a blank line and then a row full of the word
# "Performance" before the real headers, so I skip the first 2 rows.
df = pd.read_csv("data/world_cup_misc.csv", skiprows=2)

print("Players in the file:", len(df))

# Squad comes through as "us USA" so I split off the country code
df["Squad"] = df["Squad"].str.split(" ", n=1).str[1]

# Pos has combined roles like FWMF. FBref puts the main position first
# so I take the first 2 letters to make a new Position column.
df["Position"] = df["Pos"].str[:2]

# make sure the columns I need are numbers
df["90s"] = pd.to_numeric(df["90s"], errors="coerce")
df["Fls"] = pd.to_numeric(df["Fls"], errors="coerce")

# PKwon and PKcon are completely empty in this file so I drop them
df = df.drop(columns=["PKwon", "PKcon"])

# rename so the code is easier to read
df = df.rename(columns={"90s": "Nineties", "Fls": "FoulsPer90"})

print("Players who never played:", len(df[df["Nineties"] == 0]))
print("Goalkeepers:", len(df[df["Position"] == "GK"]))
print()


# ==============================================================
# STEP 2: PLAN

print("STEP 2: PLAN")
print("H0: mean fouls per 90 is the same for midfielders and defenders")
print("Ha: mean fouls per 90 is not the same")
print("Two sample independent t-test, alpha = 0.05")
print()

# I only want outfield players who actually played, so I drop the
# goalkeepers and anyone with 0 minutes (listwise deletion).
outfield = df[(df["Nineties"] > 0) & (df["Position"].isin(["DF", "MF"]))]


# a small function so I can check outliers before and after my cut off
def count_outliers(values):
    # 1.5 x IQR rule
    q1 = np.percentile(values, 25)
    q3 = np.percentile(values, 75)
    iqr = q3 - q1
    low = q1 - 1.5 * iqr
    high = q3 + 1.5 * iqr
    return len(values[(values < low) | (values > high)])


# I also drop players with less than one full match. The numbers are
# already per 90 so someone who played 9 minutes and made 1 foul comes
# out as 20 fouls per 90, which is not really how they played.
players = outfield[outfield["Nineties"] >= 1].copy()

print("Outliers using the 1.5 x IQR rule:")
print("  before the cut off:", count_outliers(outfield["FoulsPer90"]),
      "out of", len(outfield))
print("  after the cut off: ", count_outliers(players["FoulsPer90"]),
      "out of", len(players))

defenders = players[players["Position"] == "DF"]
midfielders = players[players["Position"] == "MF"]

print("Defenders in the population:", len(defenders))
print("Midfielders in the population:", len(midfielders))

# simple random sample of 150 from each group. Both are well over 30
# so the Central Limit Theorem applies.
def_sample = defenders.sample(n=150, random_state=SEED)
mid_sample = midfielders.sample(n=150, random_state=SEED)

def_fouls = def_sample["FoulsPer90"]
mid_fouls = mid_sample["FoulsPer90"]

print("Sample size for each group:", len(def_fouls))
print()


# ==============================================================
# STEP 3: SOLVE

print("STEP 3: SOLVE")
print()

# ---- descriptive statistics 

print("Descriptive statistics for fouls per 90:")
for name, fouls in [("Defenders  ", def_fouls), ("Midfielders", mid_fouls)]:
    mean = fouls.mean()
    median = fouls.median()
    sd = fouls.std()            # pandas already uses n-1 for a sample
    variance = fouls.var()
    iqr = fouls.quantile(0.75) - fouls.quantile(0.25)
    data_range = fouls.max() - fouls.min()

    print(name, "mean =", round(mean, 2),
          " median =", round(median, 2),
          " SD =", round(sd, 2),
          " variance =", round(variance, 2),
          " IQR =", round(iqr, 2),
          " range =", round(data_range, 2))

print()
print("The mean is bigger than the median in both groups so both")
print("distributions are skewed to the right.")
print()


# ---- confidence intervals 
# CI = x-bar +/- z* (s / sqrt(n)), and z* = 1.960 for 95% confidence
def confidence_interval(fouls):
    n = len(fouls)
    mean = fouls.mean()
    sd = fouls.std()
    standard_error = sd / np.sqrt(n)
    margin_of_error = 1.960 * standard_error
    return mean, margin_of_error


print("95% confidence intervals (z* = 1.960):")
for name, fouls in [("Defenders  ", def_fouls), ("Midfielders", mid_fouls)]:
    mean, margin = confidence_interval(fouls)
    print(name, round(mean, 2), "+/-", round(margin, 2),
          " so", round(mean - margin, 2), "to", round(mean + margin, 2))
print()


# ---- two sample t-test 
# t* = (x-bar1 - x-bar2) / sqrt(s1^2/n1 + s2^2/n2)
n1 = len(mid_fouls)
n2 = len(def_fouls)
mean1 = mid_fouls.mean()
mean2 = def_fouls.mean()
var1 = mid_fouls.var()
var2 = def_fouls.var()

standard_error = np.sqrt(var1 / n1 + var2 / n2)
t_star = (mean1 - mean2) / standard_error

#  to take the conservative approach and use the smaller
# degrees of freedom
df_smaller = min(n1 - 1, n2 - 1)

# two sided p-value
p_value = 2 * (1 - stats.t.cdf(abs(t_star), df_smaller))

print("Two sample t-test:")
print("  difference in means =", round(mean1 - mean2, 2))
print("  standard error =", round(standard_error, 4))
print("  t* =", round(t_star, 2))
print("  degrees of freedom =", df_smaller)
print("  p-value =", round(p_value, 4))
print()


# ==============================================================
# STEP 4: CONCLUDE

print("STEP 4: CONCLUDE")
if p_value <= 0.05:
    print("p is less than 0.05 so I reject H0.")
    print("Midfielders commit about", round(mean1 - mean2, 2),
          "more fouls per 90 than defenders,")
    print("which is roughly", round(100 * (mean1 / mean2 - 1)), "% more.")
else:
    print("p is greater than 0.05 so I do not reject H0.")
print()

# I wanted to check my minutes cut off was not deciding the answer,
# so I ran the same test again with stricter cut offs.
print("Same test with different minutes cut offs:")
for cut in [1, 2, 3]:
    check = outfield[outfield["Nineties"] >= cut]
    a = check[check["Position"] == "MF"]["FoulsPer90"]
    b = check[check["Position"] == "DF"]["FoulsPer90"]
    se = np.sqrt(a.var() / len(a) + b.var() / len(b))
    t = (a.mean() - b.mean()) / se
    dof = min(len(a) - 1, len(b) - 1)
    p = 2 * (1 - stats.t.cdf(abs(t), dof))
    print("  at least", cut, "match(es): MF =", round(a.mean(), 2),
          " DF =", round(b.mean(), 2),
          " t* =", round(t, 2), " p =", round(p, 4))
print()


# ==============================================================
# CHARTS

# Chart 1: a histogram for each group, one above the other.
# I kept them separate because when I overlapped them the two colours
# mixed into a third colour and it was hard to read.
fig, ax = plt.subplots(2, 1, figsize=(9, 5.2), sharex=True)
bins = np.linspace(0, 4.5, 19)

ax[0].hist(def_fouls, bins=bins, color=blue)
ax[0].axvline(def_fouls.mean(), color="black")
ax[0].axvline(def_fouls.median(), color="black", linestyle="--")
ax[0].set_title("Defenders    mean " + str(round(def_fouls.mean(), 2)) +
                "    median " + str(round(def_fouls.median(), 2)),
                loc="left", color=blue, fontweight="bold")

ax[1].hist(mid_fouls, bins=bins, color=orange)
ax[1].axvline(mid_fouls.mean(), color="black")
ax[1].axvline(mid_fouls.median(), color="black", linestyle="--")
ax[1].set_title("Midfielders    mean " + str(round(mid_fouls.mean(), 2)) +
                "    median " + str(round(mid_fouls.median(), 2)),
                loc="left", color=orange, fontweight="bold")

for a in ax:
    a.set_ylabel("Number of players")
    a.spines["top"].set_visible(False)
    a.spines["right"].set_visible(False)
    a.grid(axis="y", color="#e1e0d9")
    a.set_axisbelow(True)

ax[1].set_xlabel("Fouls committed per 90 minutes")
fig.tight_layout(rect=[0, 0.05, 1, 1])
fig.text(0.01, 0.02, "Solid line = mean, dashed line = median",
         color="grey")
fig.savefig("output/chart_histograms.png", dpi=200)
plt.close()

# Chart 2: the two confidence intervals on the same scale
fig, ax = plt.subplots(figsize=(9, 3.4))

y = 0
for name, fouls, colour in [("Defenders", def_fouls, blue),
                            ("Midfielders", mid_fouls, orange)]:
    mean, margin = confidence_interval(fouls)
    ax.plot([mean - margin, mean + margin], [y, y], color=colour, linewidth=3)
    ax.plot(mean, y, "o", color=colour, markersize=10)
    ax.text(mean + margin + 0.04, y,
            str(round(mean, 2)) + "  [" + str(round(mean - margin, 2)) +
            ", " + str(round(mean + margin, 2)) + "]", va="center")
    y = y + 1

ax.set_yticks([0, 1])
ax.set_yticklabels(["Defenders", "Midfielders"])
ax.set_xlim(0.6, 1.85)
ax.set_ylim(-0.6, 1.5)
ax.set_xlabel("Mean fouls per 90 minutes with 95% confidence interval")
ax.set_title("The two intervals do not overlap", loc="left",
             fontweight="bold")
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
ax.grid(axis="x", color="#e1e0d9")
ax.set_axisbelow(True)
fig.tight_layout()
fig.savefig("output/chart_confidence.png", dpi=200)
plt.close()

# save the cleaned data and my sample so someone can check my work
players.to_csv("output/population_cleaned.csv", index=False)
sample = pd.concat([def_sample, mid_sample])
sample.to_csv("output/analysis_sample.csv", index=False)

print("Charts and csv files saved in the output folder.")
