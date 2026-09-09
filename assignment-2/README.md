Assignment-2 Details

## Group (SYD 45) Members - Assingment 2
| Name  | Student ID | Analytical Task |
| -- |--- |---|
| Roshan Lamichhane| S399178| Task 1|
| Shrijan Neupane  | S398335| Task 2|



# Run Guide
Before anything, please run these
1. Install the requirements
> `pip install -r requirements.txt`
2. Start/activate virtualenv
> `python -m venv venv`

3.It should start virtualenv automatically. If not run,
> `. ./venv/bin/activate`



# For Analytical Task 1

<b>Author: Roshan Lamichhane (S399178)</b>

```
Analytical Task:
 Was there a significant difference in attacking performance
 between Argentina's forward players and midfielders at the
 2026 FIFA World Cup?

 Data source:
 FBref - Argentina 2026 FIFA World Cup Standard Stats

 Main variables:
 Player, Position, Minutes, 90s, Goals, Assists
```

## Steps to Run Analytical Task 1
- Inside the `task1` directory, run
```bash
python task1_wrangling.py # converts raw csv into clean ones
python  task1_analysis.py # run the actual analysis code

# output will be available on output folder of task1 directory
```
## Results of Task 1
This project analyses whether there was a significant difference in attacking performance between Argentina’s forwards and midfielders at the 2026 FIFA World Cup. Player statistics were obtained from FBref and cleaned using Python. Players were filtered to include only clear FW and MF positions, with zero-playing-time and ambiguous-position records excluded. The final analysis dataset contained **13 players: 5 forwards and 8 midfielders**.

Attacking performance was measured using **goal contributions per 90 minutes (G+A/90)**. Forwards had a higher mean (**1.558**) than midfielders (**0.308**), but the Welch two-sample t-test produced **t = 1.358** and **p = 0.2418**. Since p > 0.05, the null hypothesis was not rejected, indicating **insufficient statistical evidence of a significant difference** in mean G+A/90 between the two groups.


# For Analytical Task 2
<b>Author: Shrijan Neupane (S398335)</b>

```
Analytical Task:
 Do midfielders commit more fouls per 90 minutes than
 defenders at the 2026 FIFA World Cup?

 Data source:
 FBref - Player Miscellaneous Stats, 2026 FIFA World Cup
 https://fbref.com/en/comps/1/misc/World-Cup-Stats

 Main variables:
 Player, Position, Squad, Age, 90s, Fls (fouls per 90)
```

Note on the data: FBref gave me this table in "per 90 minutes" mode,
so the Fls column is already a rate and not a count. Messi has
Fld = 2.44 and you cannot be fouled 2.44 times, which is how I worked
it out. Everything after that follows from it.

## Steps to Run Analytical Task 2
- Inside the `task2` directory, run
```bash
python src/discipline_analysis.py # wrangling and analysis in one script

# output will be available on output folder of task2 directory
```

## What Task 2 Does
Following the 4 step process:

1. **State** - the question above.
2. **Plan** - H0: the two means are equal, Ha: they are not equal.
   Two sample independent t-test, alpha = 0.05.
3. **Solve** - descriptive statistics, then a 95% confidence interval
   using `CI = x-bar +/- z* (s / sqrt(n))` with z* = 1.960, then the
   two sample t-test. Degrees of freedom use the conservative approach
    (the smaller group minus one).
4. **Conclude** - interpret the p-value.

Cleaning steps: split the country code off the Squad column, built a
Position column from the first two letters of Pos so hybrids like FWMF
become FW, dropped the two empty columns, then removed 33 players who
never played, 62 goalkeepers, and anyone with less than one full match.
The last one matters because the numbers are per 90, so a player with
9 minutes and 1 foul shows up as 20 fouls per 90. Checking with the
1.5 x IQR rule, outliers went from 32 out of 722 down to 12 out of 570.

That left 268 defenders and 302 midfielders. I took a simple random
sample of 150 from each, both well over the 30 the Central Limit
Theorem needs.

## Task 2 Results
| Group | n | Mean | Median | SD | Variance | IQR | 95% CI |
|---|---|---|---|---|---|---|---|
| Defenders | 150 | 0.96 | 0.94 | 0.69 | 0.48 | 0.93 | 0.85 to 1.08 |
| Midfielders | 150 | 1.26 | 1.17 | 0.90 | 0.80 | 0.94 | 1.11 to 1.40 |

t* = 3.16, degrees of freedom = 149, p = 0.0019.

p is below 0.05 so I reject H0. Midfielders commit about 30% more
fouls per 90 minutes than defenders, which is the opposite of what I
expected. The two confidence intervals do not overlap either.

I also re-ran the same test at stricter minutes cut offs to make sure
my cut off was not deciding the answer:

- at least 1 match: p = 0.0001
- at least 2 matches: p = 0.0034
- at least 3 matches: p = 0.0369

It stays significant every time.

Limitations: fouls are recorded by the referee so this measures what
got punished, not every foul that happened. Both distributions are
skewed rather than normal, so I would read the p-value as strong
evidence rather than an exact number.


# For Analytical Task 3
