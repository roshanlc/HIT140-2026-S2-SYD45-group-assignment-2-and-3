"""
Chart for Task 3 - Passing/Distribution.
Two panels:
  A) Distribution of Cmp% by group (box + jittered points)
  B) Mean Cmp% by group with 95% CI error bars, annotated with the
     Welch's t-test result.

Colors follow the validated categorical palette (blue = slot 1, orange =
slot 2), light chart surface, muted gridlines/ink per the palette spec.
"""
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from scipy import stats

# ---- palette (validated categorical slots 1 & 2, light-mode chrome) ----
SURFACE = "#fcfcfb"
PAGE = "#f9f9f7"
INK_PRIMARY = "#0b0b0b"
INK_SECONDARY = "#52514e"
INK_MUTED = "#898781"
GRID = "#e1e0d9"
BASELINE = "#c3c2b7"
BLUE = "#2a78d6"     # Finalist
ORANGE = "#eb6834"   # Non-finalist

plt.rcParams["font.family"] = "DejaVu Sans"
plt.rcParams["axes.edgecolor"] = BASELINE
plt.rcParams["text.color"] = INK_PRIMARY

RANDOM_SEED = 398629

# ---- load + reproduce the exact sample used in the analysis ----
df = pd.read_csv("data/wc2026_passing.csv")
df = df.dropna(subset=["Player", "Squad", "Att", "Cmp_pct", "Group"]).drop_duplicates(
    subset=["Player", "Squad"]
)
df = df[df["Att"] >= 20]

fin = df[df.Group == "Finalist"].sample(n=30, random_state=RANDOM_SEED)["Cmp_pct"]
non = df[df.Group == "Non-finalist"].sample(n=30, random_state=RANDOM_SEED)["Cmp_pct"]

n1, n2 = len(fin), len(non)
m1, m2 = fin.mean(), non.mean()
v1, v2 = fin.var(ddof=1), non.var(ddof=1)
diff = m1 - m2
se = np.sqrt(v1 / n1 + v2 / n2)
dfw = (v1 / n1 + v2 / n2) ** 2 / ((v1 / n1) ** 2 / (n1 - 1) + (v2 / n2) ** 2 / (n2 - 1))
tcrit = stats.t.ppf(0.975, dfw)
lo, hi = diff - tcrit * se, diff + tcrit * se
t_stat, p_val = stats.ttest_ind(fin, non, equal_var=False)

# ---- figure ----
fig, axes = plt.subplots(1, 2, figsize=(11, 5.2), facecolor=PAGE)
fig.suptitle(
    "Pass completion rate: 2026 World Cup finalists vs. non-finalists",
    fontsize=14, fontweight="bold", color=INK_PRIMARY, x=0.02, ha="left", y=0.99,
)
fig.text(
    0.02, 0.935,
    "Random samples of 30 players per group (n=60). Spain + Argentina = Finalist.",
    fontsize=9.5, color=INK_SECONDARY, ha="left",
)

groups = ["Finalist\n(ESP + ARG)", "Non-finalist"]
colors = [BLUE, ORANGE]
data = [fin.values, non.values]

# --- Panel A: box + jitter ---
axA = axes[0]
axA.set_facecolor(SURFACE)
bp = axA.boxplot(
    data, positions=[1, 2], widths=0.42, patch_artist=True, showfliers=False,
    medianprops=dict(color=INK_PRIMARY, linewidth=2),
    whiskerprops=dict(color=INK_MUTED, linewidth=1.4),
    capprops=dict(color=INK_MUTED, linewidth=1.4),
    boxprops=dict(linewidth=1.4),
)
for patch, c in zip(bp["boxes"], colors):
    patch.set_facecolor(c)
    patch.set_alpha(0.18)
    patch.set_edgecolor(c)

rng = np.random.default_rng(RANDOM_SEED)
for i, (vals, c) in enumerate(zip(data, colors), start=1):
    jitter = rng.uniform(-0.12, 0.12, size=len(vals))
    axA.scatter(
        np.full(len(vals), i) + jitter, vals,
        s=26, color=c, alpha=0.75, edgecolor=SURFACE, linewidth=0.6, zorder=3,
    )

axA.set_xticks([1, 2])
axA.set_xticklabels(groups, fontsize=10.5, color=INK_PRIMARY)
axA.set_ylabel("Pass completion % (Cmp%)", fontsize=10, color=INK_SECONDARY)
axA.yaxis.grid(True, color=GRID, linewidth=1)
axA.set_axisbelow(True)
for spine in ["top", "right", "left"]:
    axA.spines[spine].set_visible(False)
axA.spines["bottom"].set_color(BASELINE)
axA.tick_params(colors=INK_MUTED, labelsize=9.5)
axA.set_title("A. Distribution by group", fontsize=11, color=INK_PRIMARY, loc="left", pad=10)

# --- Panel B: mean +/- 95% CI per group, with diff annotation ---
axB = axes[1]
axB.set_facecolor(SURFACE)
means = [m1, m2]
sems = [stats.t.ppf(0.975, n - 1) * s.std(ddof=1) / np.sqrt(n) for s, n in zip(data, [n1, n2])]

bars = axB.bar(
    [1, 2], means, width=0.5, color=colors, alpha=0.85,
    edgecolor=colors, linewidth=1.2, zorder=3,
)
axB.errorbar(
    [1, 2], means, yerr=sems, fmt="none", ecolor=INK_PRIMARY, elinewidth=1.6,
    capsize=5, capthick=1.6, zorder=4,
)
for x, m in zip([1, 2], means):
    axB.text(x, m + 3.2, f"{m:.1f}%", ha="center", va="bottom",
              fontsize=10.5, fontweight="bold", color=INK_PRIMARY)

axB.set_xticks([1, 2])
axB.set_xticklabels(groups, fontsize=10.5, color=INK_PRIMARY)
axB.set_ylim(0, 100)
axB.set_ylabel("Mean pass completion % (± 95% CI)", fontsize=10, color=INK_SECONDARY)
axB.yaxis.grid(True, color=GRID, linewidth=1)
axB.set_axisbelow(True)
for spine in ["top", "right", "left"]:
    axB.spines[spine].set_visible(False)
axB.spines["bottom"].set_color(BASELINE)
axB.tick_params(colors=INK_MUTED, labelsize=9.5)
axB.set_title("B. Group means — Welch's t-test", fontsize=11, color=INK_PRIMARY, loc="left", pad=10)

sig_text = "not significant" if p_val >= 0.05 else "significant"
axB.text(
    1.5, 8,
    f"diff = {diff:+.2f} pts, 95% CI ({lo:.2f}, {hi:.2f})\n"
    f"t({dfw:.0f}) = {t_stat:.2f}, p = {p_val:.3f} — {sig_text} at α = 0.05",
    ha="center", va="bottom", fontsize=9, color=INK_SECONDARY,
    bbox=dict(boxstyle="round,pad=0.4", facecolor=SURFACE, edgecolor=GRID, linewidth=1),
)

plt.tight_layout(rect=[0, 0, 1, 0.90])
fig.savefig("task3_chart.png", dpi=200, facecolor=PAGE)
print("saved task3_chart.png")
