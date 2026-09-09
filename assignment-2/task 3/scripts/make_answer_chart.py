"""
Headline "answer card" for Task 3's analytical question:
  "Did players from the two 2026 FIFA World Cup finalist teams (Spain and
  Argentina - Spain won the final) achieve a significantly higher pass
  completion rate (%) than players from teams that did not reach the final?"

Single panel: group means with 95% CI, the question as title, and a plain
-English answer line beneath the chart.
"""
import textwrap
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
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
RANDOM_SEED = 398629

# ---- reproduce the exact sample used in the analysis ----
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
sems = [stats.t.ppf(0.975, n - 1) * s.std(ddof=1) / np.sqrt(n) for s, n in zip([fin, non], [n1, n2])]

question = (
    "Did players from the two 2026 FIFA World Cup finalist teams (Spain and "
    "Argentina — Spain won the final) achieve a significantly higher pass "
    "completion rate (%) than players from teams that did not reach the final?"
)
wrapped_q = "\n".join(textwrap.wrap(question, width=72))

fig, ax = plt.subplots(figsize=(9, 8.6), facecolor=PAGE)
fig.subplots_adjust(top=0.68, bottom=0.20, left=0.13, right=0.92)

fig.text(0.06, 0.975, wrapped_q, fontsize=13, fontweight="bold",
          color=INK_PRIMARY, ha="left", va="top", linespacing=1.35)
fig.text(0.06, 0.705,
          "n = 30 players per group (simple random sample) · Welch's two-sample t-test, α = 0.05",
          fontsize=9.5, color=INK_SECONDARY, ha="left", va="top")

groups = ["Finalist\n(Spain + Argentina)", "Non-finalist"]
colors = [BLUE, ORANGE]
means = [m1, m2]

ax.set_facecolor(SURFACE)
ax.bar([1, 2], means, width=0.5, color=colors, alpha=0.88, edgecolor=colors, linewidth=1.2, zorder=3)
ax.errorbar([1, 2], means, yerr=sems, fmt="none", ecolor=INK_PRIMARY, elinewidth=1.8,
            capsize=6, capthick=1.8, zorder=4)
for x, m in zip([1, 2], means):
    ax.text(x, m + 3.5, f"{m:.1f}%", ha="center", va="bottom",
             fontsize=13, fontweight="bold", color=INK_PRIMARY)

ax.set_xticks([1, 2])
ax.set_xticklabels(groups, fontsize=11.5, color=INK_PRIMARY)
ax.set_ylim(0, 100)
ax.set_ylabel("Mean pass completion % (± 95% CI)", fontsize=10.5, color=INK_SECONDARY)
ax.yaxis.grid(True, color=GRID, linewidth=1)
ax.set_axisbelow(True)
for spine in ["top", "right", "left"]:
    ax.spines[spine].set_visible(False)
ax.spines["bottom"].set_color(BASELINE)
ax.tick_params(colors=INK_MUTED, labelsize=10)

# answer strip
fig.text(0.06, 0.135, "Answer: No.", fontsize=13, fontweight="bold", color=INK_PRIMARY, ha="left")
fig.text(
    0.06, 0.105,
    f"Finalists were {diff:+.2f} points higher on average (87.9% vs 86.9%), but Welch's "
    f"t-test gives t({dfw:.0f}) = {t_stat:.2f}, p = {p_val:.3f}, and the 95% CI for the "
    f"difference, ({lo:.2f}, {hi:.2f}) pts, crosses zero — not statistically significant.",
    fontsize=9.5, color=INK_SECONDARY, ha="left", va="top", wrap=True,
)

fig.savefig("task3_answer_card.png", dpi=200, facecolor=PAGE)
print("saved task3_answer_card.png")
