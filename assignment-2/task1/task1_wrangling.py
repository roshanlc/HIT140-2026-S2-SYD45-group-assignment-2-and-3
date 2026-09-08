# Author: Roshan Lamichhane (S399178)
# Analytical Task 1:

#
# Analytical Question:
#
# Was there a significant difference in attacking performance
# between Argentina's forward players and midfielders at the
# 2026 FIFA World Cup?
#
# Data source:
# FBref - Argentina 2026 FIFA World Cup Standard Stats
#
# Main variables:
# Player, Position, Minutes, 90s, Goals, Assists



# This code takes in the raw csv input that I downloaded from Fbref and cleans it for easier analysis purpose.

import pandas as pd
from pathlib import Path


# ============================================================
# TASK 1 - DATA WRANGLING AND CLEANING
# ============================================================
#
# Analytical Question:
#
# Was there a significant difference in attacking performance
# between Argentina's forward players and midfielders at the
# 2026 FIFA World Cup?
#
# Data source:
# FBref - Argentina 2026 FIFA World Cup Standard Stats
#
# Main variables:
# Player, Position, Minutes, 90s, Goals, Assists
#
# ============================================================


# ============================================================
# 1. FILE LOCATIONS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent

print("BAse dir", BASE_DIR)
input_file = BASE_DIR / "data/argentina-player-stats-raw.csv"

output_dir = BASE_DIR / "output"

output_dir.mkdir(
    exist_ok=True
)

clean_file = output_dir / "argentina_clean.csv"
analysis_file = output_dir / "argentina_analysis.csv"


# ============================================================
# 2. READ RAW CSV
# ============================================================

# FBref exports the table with two header rows.
#
# Row 0 = grouped headings
# Row 1 = actual variable names
#
# Therefore, read the CSV without assigning a header.

raw = pd.read_csv(
    input_file,
    header=None
)

print("=" * 70)
print("RAW DATA")
print("=" * 70)

print("Raw dataset shape:", raw.shape)


# ============================================================
# 3. REMOVE FBREF HEADER ROWS
# ============================================================

# Actual player records begin from row 2.

df = raw.iloc[2:].copy()


# ============================================================
# 4. SELECT REQUIRED COLUMNS
# ============================================================

# Based on the FBref CSV structure:
#
# 0 = Player
# 1 = Pos
# 2 = Age
# 3 = MP
# 4 = Starts
# 5 = Min
# 6 = 90s
# 7 = Gls
# 8 = Ast
# 9 = G+A

df = df.iloc[
    :,
    [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
].copy()


# Assign clear column names.

df.columns = [
    "Player",
    "Pos",
    "Age",
    "MP",
    "Starts",
    "Min",
    "90s",
    "Gls",
    "Ast",
    "G+A"
]


# ============================================================
# 5. REMOVE EMPTY AND SUMMARY RECORDS
# ============================================================

df = df.dropna(
    subset=["Player"]
)


df = df[
    ~df["Player"].isin(
        [
            "Squad Total",
            "Opponent Total"
        ]
    )
]


# ============================================================
# 6. CLEAN POSITION VALUES
# ============================================================

df["Pos"] = (
    df["Pos"]
    .astype(str)
    .str.strip()
)


# ============================================================
# 7. CONVERT NUMERIC VARIABLES
# ============================================================

numeric_columns = [
    "Age",
    "MP",
    "Starts",
    "Min",
    "90s",
    "Gls",
    "Ast",
    "G+A"
]


for column in numeric_columns:

    df[column] = pd.to_numeric(
        df[column],
        errors="coerce"
    )


# ============================================================
# 8. REMOVE INVALID PLAYING-TIME RECORDS
# ============================================================

# G+A per 90 cannot be calculated when 90s is missing
# or equal to zero.

df = df.dropna(
    subset=["90s"]
)

df = df[
    df["90s"] > 0
]


# ============================================================
# 9. REMOVE DUPLICATE PLAYERS
# ============================================================

df = df.drop_duplicates(
    subset=["Player"]
)


# ============================================================
# 10. CREATE GOAL CONTRIBUTIONS
# ============================================================

df["goal_contributions"] = (
    df["Gls"] + df["Ast"]
)


# ============================================================
# 11. CALCULATE G+A PER 90
# ============================================================

df["ga_per90"] = (
    df["goal_contributions"] / df["90s"]
)


# ============================================================
# 12. CALCULATE SUPPORTING VARIABLES
# ============================================================

df["goals_per90"] = (
    df["Gls"] / df["90s"]
)

df["assists_per90"] = (
    df["Ast"] / df["90s"]
)


# ============================================================
# 13. ROUND CALCULATED VALUES
# ============================================================

df["ga_per90"] = df["ga_per90"].round(2)

df["goals_per90"] = df["goals_per90"].round(2)

df["assists_per90"] = df["assists_per90"].round(2)


# ============================================================
# 14. SAVE CLEAN DATASET
# ============================================================

df.to_csv(
    clean_file,
    index=False
)


# ============================================================
# 15. CREATE FW/MF ANALYSIS DATASET
# ============================================================

analysis_df = df[
    df["Pos"].isin(
        ["FW", "MF"]
    )
].copy()


# ============================================================
# 16. SAVE ANALYSIS DATASET
# ============================================================

analysis_df.to_csv(
    analysis_file,
    index=False
)


# ============================================================
# 17. DISPLAY RESULTS
# ============================================================

print("\n" + "=" * 70)
print("CLEAN DATASET")
print("=" * 70)

print(
    df.to_string(index=False)
)


print("\n" + "=" * 70)
print("FW/MF ANALYSIS DATASET")
print("=" * 70)

print(
    analysis_df.to_string(index=False)
)


print("\n" + "=" * 70)
print("NUMBER OF PLAYERS BY POSITION")
print("=" * 70)

print(
    analysis_df["Pos"].value_counts()
)


print("\n" + "=" * 70)
print("DATA WRANGLING COMPLETE")
print("=" * 70)

print(
    "Clean data saved to:",
    clean_file
)

print(
    "Analysis data saved to:",
    analysis_file
)