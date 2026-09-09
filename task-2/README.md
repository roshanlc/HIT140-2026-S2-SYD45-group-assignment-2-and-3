# Task 2 - Fouls by position (FIFA World Cup 2026)

Shrijan Neupane (s398335)

HIT140 Foundation of Data Science, Assessment 2

## My question

Do midfielders commit more fouls per 90 minutes than defenders at the
FIFA World Cup 2026?

Short answer: yes. Midfielders average 1.26 fouls per 90 and defenders
average 0.96, which is about 30% more. The t-test gives t(149) = 3.16
and p = .002, so I reject the null hypothesis.

## Where the data came from

FBref, Player Miscellaneous Stats for the 2026 World Cup:
https://fbref.com/en/comps/1/misc/World-Cup-Stats

I exported the table myself and saved it as `data/world_cup_misc.csv`
without changing anything.

One thing I had to work out: FBref gave me this table in "per 90 minutes"
mode, so the Fls column is already a rate and not a count. You can tell
because Messi has Fld = 2.44, and nobody can be fouled 2.44 times. This
changed how I did everything after that.

## Files

- `data/world_cup_misc.csv` - the raw file from FBref
- `src/discipline_analysis.py` - all of my analysis
- `output/results.txt` - what the script prints out
- `output/population_cleaned.csv` - the 570 players I kept
- `output/analysis_sample.csv` - the 300 players I sampled
- `output/chart_histograms.png` - histograms of both groups
- `output/chart_confidence.png` - the two confidence intervals

## How to run it

```
pip install pandas numpy scipy matplotlib
python src/discipline_analysis.py
```

I set the random seed to 42 so the sample comes out the same every time
and anyone can check my numbers.

## What I did

I followed the 4-step process from Week 4.

**Step 1 - State.** The question above.

**Step 2 - Plan.** My hypotheses are H0: the two means are equal, and Ha:
they are not equal. I used a two-sample independent t-test with alpha =
0.05.

Cleaning the data: I split the country code off the Squad column, because
it comes through as "us USA". I also made a new Position column from the
first two letters of Pos, since FBref writes hybrid roles like FWMF and
puts the main position first.

Then I removed some players. 33 of them never played, so a per 90 rate
means nothing for them. I took out the 62 goalkeepers as well because
their job is too different to compare fairly. Last, I removed anyone with
less than one full match. This one mattered the most, because the numbers
are already per 90 and a player with 9 minutes and one foul shows up as
20 fouls per 90. I checked this with the 1.5 x IQR rule from Week 2 and
it went from 32 outliers out of 722 players down to 12 out of 570.

That left 268 defenders and 302 midfielders. I took a simple random
sample of 150 from each. Both are well over 30 so the Central Limit
Theorem applies.

**Step 3 - Solve.** Descriptive statistics first, then the confidence
interval using CI = x-bar +/- z* (s / sqrt(n)) with z* = 1.960, then the
two-sample t-test. For the degrees of freedom I used the conservative
approach from Week 4 and took the smaller group minus one, which is 149.

**Step 4 - Conclude.** p = .002 is below 0.05 so I reject H0.

## Results

| Group | n | Mean | Median | SD | Variance | IQR | 95% CI |
|---|---|---|---|---|---|---|---|
| Defenders | 150 | 0.96 | 0.94 | 0.69 | 0.48 | 0.93 | 0.85 to 1.08 |
| Midfielders | 150 | 1.26 | 1.17 | 0.90 | 0.80 | 0.94 | 1.11 to 1.40 |

In both groups the mean is bigger than the median, so both distributions
are skewed to the right.

The two confidence intervals do not overlap, which is the same story the
t-test tells.

I was a bit worried that my minutes cut-off was doing all the work, so I
ran the same test again at stricter cut-offs:

- at least 1 match: p = .0001
- at least 2 matches: p = .003
- at least 3 matches: p = .037

It stays significant every time, so the answer is not just because of
where I drew the line.

## What this means

I expected defenders to foul more, since they are the ones tackling. The
data says the opposite. My guess is that midfield is where the ball
changes hands most often, and a quick foul in that moment is a normal
midfielder tactic. A centre-back has the opposite problem, because a foul
near their own goal gives away a dangerous free kick.

## Limitations

Fouls get recorded by the referee, so this really measures what got
punished and not every foul that happened. Different referees also call
games differently, and I have not accounted for that.

Both distributions are skewed rather than normal. The t-test still works
because the Central Limit Theorem is about the distribution of the sample
mean, not the raw data, but I would treat the p-value as strong evidence
rather than an exact number.
