# FIFA World Cup 2026: Regression Analysis
# Assignment - 3 Details



## Group (SYD 45) Members - Assingment 3
| Name  | Student ID |
| -- |--- |
| Roshan Lamichhane| S399178|





## Project overview

This project develops and evaluates two linear regression models for
FIFA World Cup 2026 fixtures using information available before each
match.

-   **LR2.1 --- Goal difference:** predicts the goal difference between
    the listed home and away teams. The dataset contains **104 rows**,
    one for each match.
-   **LR2.2 --- Team goals scored:** predicts the number of goals scored
    by an individual team in a match. The dataset contains **208 rows**,
    with two team-match observations per match.

Each model uses exactly **eight explanatory variables**. No more than
four explanatory variables are shared between the models. Predictors are
designed to use pre-match information to avoid using information from
the match being predicted.

## Repository contents

The repository is expected to contain the following project files
(filenames may differ if the project has been reorganised):

``` text
.
├── README.md
├── requirements.txt
└── code/
    ├── build_datasets.py
    ├── model_nested.py
    ├── final_audit.py
    ├── raw/
    │   ├── world_cup_matches.csv
    │   ├── all_teams_matches.csv
    │   ├── regression_2_1.csv
    │   └── regression_2_2.csv
    └── nested_model_results/
        ├── model comparison outputs (.csv)
        └── actual-versus-predicted plots (.png)
```

Include any additional files that the scripts require. Keep only the
final, relevant outputs in the repository and do not upload virtual
environments, credentials, browser profiles, or unrelated files.

## Data

### Match fixtures

`world_cup_matches.csv` contains the 104 fixtures used to construct the
match-level and team-match datasets. **Add and verify the original
source URL for this file before submitting.** Do not cite a source that
was not actually used.

### Historical international results

`all_teams_matches.csv` contains historical international match results
used to derive pre-match team-form information. The project notes
identify this source:

-   [International results dataset --- martj42 on
    GitHub](https://github.com/martj42/international_results)

Record the actual download URL and access date in your final submission
if required by the course.

### Prepared datasets

-   `regression_2_1.csv`: 104 observations, one per match; target is
    home-team goals minus away-team goals.
-   `regression_2_2.csv`: 208 observations, one per team in each match;
    target is goals scored by that team.

Recent-form features are derived from matches played before the fixture
date. Team names are standardised to support matching between the
fixture and historical datasets. The final audit should be run to verify
row counts, predictor counts, missing values, shared predictors, and the
two-row-per-match structure of LR2.2.

## Predictors

### LR2.1

The eight predictors are:

1.  `team_recent_gf`
2.  `team_recent_ga`
3.  `team_recent_points`
4.  `team_rest_days`
5.  `opponent_recent_gd`
6.  `opponent_recent_win_rate`
7.  `opponent_recent_clean_sheet_rate`
8.  `is_knockout`

The target is `goal_difference`, calculated as home-team goals minus
away-team goals.

### LR2.2

The eight predictors are:

1.  `team_recent_gf`
2.  `team_recent_ga`
3.  `team_recent_points`
4.  `team_rest_days`
5.  `opponent_recent_gf`
6.  `opponent_recent_ga`
7.  `opponent_recent_points`
8.  `opponent_rest_days`

The target is `goals_scored` for the team represented by that row.

The four shared predictors are `team_recent_gf`, `team_recent_ga`,
`team_recent_points`, and `team_rest_days`.

## Modelling and evaluation

The modelling workflow compares:

-   Ordinary Least Squares (OLS)
-   Ridge Regression
-   Lasso Regression
-   A mean-prediction baseline

The modelling pipeline uses median imputation and standardisation. Ridge
and Lasso regularisation parameters are tuned using cross-validation.

-   **LR2.1:** five-fold shuffled cross-validation.
-   **LR2.2:** five-fold `GroupKFold`, grouping rows by match ID so both
    teams from the same match remain in the same fold.

Performance is evaluated using Mean Absolute Error (MAE), Root Mean
Squared Error (RMSE), and the coefficient of determination (R²). Lower
MAE and RMSE indicate better predictive accuracy; higher R² indicates
more variance explained relative to the evaluation baseline. The report
should describe these results as predictive associations, not causal
effects.

## Reproducing the analysis

Use Python 3. Install the dependencies listed in `requirements.txt`:

``` bash
python -m pip install -r requirements.txt
```

From the directory containing the scripts, run the dataset preparation,
modelling, and audit scripts:

``` bash
python build_datasets.py
python model_nested.py
python final_audit.py
```

If the scripts are inside `code/` and you run commands from the
repository root, use:

``` bash
python code/build_datasets.py
python code/model_nested.py
python code/final_audit.py
```

The commands assume that script paths and data paths are configured for
the directory from which they are run. Test the workflow from a fresh
clone before submission and update these instructions if your final
repository structure differs.

## Outputs

The analysis produces prepared regression datasets, model-comparison
results, and actual-versus-predicted plots. Ensure the committed outputs
correspond to the final scripts and datasets and match the values
reported in the assignment report.

## Limitations

-   The models use a limited set of pre-match predictors; important
    factors may not be represented.
-   Linear regression can produce fractional or implausible goal
    predictions and may underpredict unusually large goal differences or
    goal totals.
-   LR2.1 uses shuffled rather than chronological cross-validation, so
    it does not exactly reproduce forecasting into a later time period.
-   Results should be interpreted as estimates from the selected data
    and validation approach, not as guarantees of match outcomes.

## Team and submission information

-   **Unit/course:** \[Add unit code and name\]
-   **Assessment:** Assessment 3 --- Objective 2
-   **Group members:** \[Add names as required\]
-   **Repository URL:** \[Add repository URL\]

Before submission, verify all source citations, run `final_audit.py`,
check that the report metrics match the final model outputs, and follow
the course requirements for repository access and AI-use disclosure.
