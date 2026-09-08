# Task 3 - Passing / Distribution

**Author:** Sudip Sunar (S398629)

## Analytical Question

Did players from the two 2026 FIFA World Cup finalist teams (Spain and
Argentina - Spain won the final) achieve a significantly higher pass
completion rate (%) than players from teams that did not reach the final?

## Why this focal point

This task looks at **passing/distribution**, which is distinct from the
other tasks in this project: Task 1 covers attacking output (goals and
assists), and Task 2 covers disciplinary behaviour (fouls). No metric is
repeated across tasks.

## Data Source

FBref (or FIFA's official Player Statistics page) - 2026 FIFA World Cup,
"Passing" stats table.

Main variables used:

| Column | Meaning |
| -- | -- |
| Player | Player name |
| Squad | Team name (used to tag Spain/Argentina as "Finalist") |
| Pos | Playing position |
| 90s | Minutes played, expressed in 90-minute units |
| Att | Passes attempted |
| Cmp | Passes completed |
| Cmp% | Pass completion percentage (key variable for this analysis) |

## Method

1. **Data wrangling** - load the raw passing table, drop missing values,
   and filter out players with negligible playing time or very few pass
   attempts (their Cmp% would be unreliable).
2. **Data preparation and sampling** - split players into two groups:
   *Finalist* (Spain, Argentina) and *Non-finalist* (everyone else). Draw
   a simple random sample of up to 30 players from each group.
3. **Descriptive statistics** - mean, median, standard deviation, min and
   max Cmp% for each group.
4. **Confidence interval** - 95% CI for the difference in mean Cmp%
   between the two groups.
5. **Two-sample t-test (Welch's)** - tests whether the difference in mean
   Cmp% between finalist and non-finalist players is statistically
   significant (alpha = 0.05).

## Files

- `task3_passing.py` - full analysis script (currently runs end-to-end on
  placeholder data; swap in the real CSV once downloaded)
- `data/wc2026_passing.csv` - real WC2026 passing data (to be added once
  downloaded from FBref/FIFA)

## How to Run

```
pip install -r ../requirements.txt
python task3_passing.py
```

The script prints descriptive statistics, the 95% confidence interval for
the difference in means, and the t-test result (t-statistic and p-value)
with a plain-English interpretation.

## Status

Placeholder data currently in use for testing the pipeline. Real WC2026
passing data still needs to be downloaded and substituted in (see the
"NEXT STEPS FOR YOU" comment block at the bottom of `task3_passing.py`).
