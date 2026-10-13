from pathlib import Path
import re
import unicodedata

import numpy as np
import pandas as pd

BASE = Path(__file__).resolve().parent
RAW = BASE / "raw"
N_RECENT = 5

# Exactly four predictors are shared between the two models.
SHARED = [
    "team_recent_gf",
    "team_recent_ga",
    "team_recent_points",
    "team_rest_days",
]

MODEL21_EXTRA = [
    "opponent_recent_gd",
    "opponent_recent_win_rate",
    "opponent_recent_clean_sheet_rate",
    "is_knockout",
]

MODEL22_EXTRA = [
    "opponent_recent_gf",
    "opponent_recent_ga",
    "opponent_recent_points",
    "opponent_rest_days",
]

# Known fixture country codes. Do not strip arbitrary 2- or 3-letter words:
# doing so can accidentally turn "New Zealand" into "Zealand".
COUNTRY_CODES = set("""
mx kr ca us qa br au ht de nl ci se be es sa fr iq ar at pt eng gh uz
cz ch sct tr ec tn uy nz no jo pa co ba ma za cw jp py sn cv eg hr cd dz ir
""".split())

ALIASES = {
    "bosnia herz": "bosnia and herzegovina",
    "bosnia herzegovina": "bosnia and herzegovina",
    "cabo verde": "cape verde",
    "czechia": "czech republic",
    "cote d ivoire": "ivory coast",
    "korea republic": "south korea",
    "turkiye": "turkey",
    "usa": "united states",
    "ir iran": "iran",
    "iran": "iran",
    "congo dr": "dr congo",
    "dr congo": "dr congo",
    "congo democratic republic": "dr congo",
    "congo": "congo",
}


def normalise_text(value):
    if pd.isna(value):
        return ""

    name = str(value).strip()

    # Remove only known country codes at the beginning/end.
    parts = name.split()
    if parts and parts[0].lower() in COUNTRY_CODES:
        parts = parts[1:]
    if parts and parts[-1].lower() in COUNTRY_CODES:
        parts = parts[:-1]
    name = " ".join(parts)

    name = unicodedata.normalize("NFKD", name)
    name = "".join(c for c in name if not unicodedata.combining(c))
    name = name.lower().replace("&", " and ")
    name = re.sub(r"[^a-z0-9 ]", " ", name)
    return " ".join(name.split())


def team_key(value):
    key = normalise_text(value)
    return ALIASES.get(key, key)


def load_data():
    fixture_path = RAW / "world_cup_matches.csv"
    history_path = RAW / "all_teams_matches.csv"

    if not fixture_path.exists():
        raise FileNotFoundError(f"Missing fixture file: {fixture_path}")
    if not history_path.exists():
        raise FileNotFoundError(f"Missing historical file: {history_path}")

    fixtures = pd.read_csv(fixture_path)
    history = pd.read_csv(history_path)

    required_fixture = {"Date", "Home", "Score", "Away", "Round"}
    required_history = {
        "date", "home_team", "away_team", "home_score", "away_score"
    }
    if not required_fixture.issubset(fixtures.columns):
        raise ValueError(
            f"Fixture CSV missing columns: {required_fixture - set(fixtures.columns)}"
        )
    if not required_history.issubset(history.columns):
        raise ValueError(
            f"Historical CSV missing columns: {required_history - set(history.columns)}"
        )

    fixtures["date"] = pd.to_datetime(fixtures["Date"], errors="coerce")
    history["date"] = pd.to_datetime(history["date"], errors="coerce")

    fixtures["home"] = fixtures["Home"].map(team_key)
    fixtures["away"] = fixtures["Away"].map(team_key)
    history["home_key"] = history["home_team"].map(team_key)
    history["away_key"] = history["away_team"].map(team_key)

    scores = fixtures["Score"].astype(str).str.extract(
        r"(\d+)\s*[–—-]\s*(\d+)"
    )
    fixtures["home_goals"] = pd.to_numeric(scores[0], errors="coerce")
    fixtures["away_goals"] = pd.to_numeric(scores[1], errors="coerce")

    fixtures = fixtures.dropna(
        subset=["date", "home_goals", "away_goals", "home", "away"]
    ).copy()
    history = history.dropna(
        subset=["date", "home_score", "away_score"]
    ).copy()

    fixtures = fixtures.sort_values(["date", "Time"], kind="stable").reset_index(drop=True)

    if len(fixtures) != 104:
        raise ValueError(
            f"Expected 104 fixtures after parsing scores; got {len(fixtures)}. "
            "Check the source fixture CSV and score format."
        )

    teams = set(fixtures["home"]) | set(fixtures["away"])
    if len(teams) != 48:
        raise ValueError(
            f"Expected 48 normalised teams, got {len(teams)}: {sorted(teams)}"
        )

    historical_teams = set(history["home_key"]) | set(history["away_key"])
    unmatched = sorted(teams - historical_teams)
    if unmatched:
        raise ValueError(
            "These fixture teams have no exact historical-name mapping: "
            + ", ".join(unmatched)
            + ". Add verified aliases before modelling."
        )

    return fixtures, history


def team_history_before(team, cutoff, history):
    """Return a team's five most recent matches strictly before kickoff date."""
    home = history.loc[
        (history["home_key"] == team) & (history["date"] < cutoff),
        ["date", "home_score", "away_score"],
    ].copy()
    home.columns = ["date", "gf", "ga"]

    away = history.loc[
        (history["away_key"] == team) & (history["date"] < cutoff),
        ["date", "away_score", "home_score"],
    ].copy()
    away.columns = ["date", "gf", "ga"]

    matches = pd.concat([home, away], ignore_index=True)
    return matches.sort_values("date").tail(N_RECENT).reset_index(drop=True)


def stats(matches, cutoff):
    if matches.empty:
        return {
            "gf": np.nan,
            "ga": np.nan,
            "points": np.nan,
            "gd": np.nan,
            "win_rate": np.nan,
            "clean_sheet_rate": np.nan,
            "rest_days": np.nan,
        }

    wins = matches["gf"] > matches["ga"]
    draws = matches["gf"] == matches["ga"]

    return {
        "gf": float(matches["gf"].mean()),
        "ga": float(matches["ga"].mean()),
        "points": float((wins.astype(int) * 3 + draws.astype(int)).mean()),
        "gd": float((matches["gf"] - matches["ga"]).mean()),
        "win_rate": float(wins.mean()),
        "clean_sheet_rate": float((matches["ga"] == 0).mean()),
        "rest_days": float((cutoff - matches["date"].max()).days),
    }


def features(team, opponent, cutoff, history):
    team_stats = stats(team_history_before(team, cutoff, history), cutoff)
    opp_stats = stats(team_history_before(opponent, cutoff, history), cutoff)

    return {
        "team_recent_gf": team_stats["gf"],
        "team_recent_ga": team_stats["ga"],
        "team_recent_points": team_stats["points"],
        "team_rest_days": team_stats["rest_days"],
        "opponent_recent_gd": opp_stats["gd"],
        "opponent_recent_win_rate": opp_stats["win_rate"],
        "opponent_recent_clean_sheet_rate": opp_stats["clean_sheet_rate"],
        "opponent_recent_gf": opp_stats["gf"],
        "opponent_recent_ga": opp_stats["ga"],
        "opponent_recent_points": opp_stats["points"],
        "opponent_rest_days": opp_stats["rest_days"],
    }


def main():
    fixtures, history = load_data()
    rows21 = []
    rows22 = []

    for match_id, match in fixtures.iterrows():
        cutoff = match["date"]
        home = match["home"]
        away = match["away"]

        home_f = features(home, away, cutoff, history)
        away_f = features(away, home, cutoff, history)

        round_text = str(match.get("Round", "")).lower()
        is_knockout = int("group" not in round_text)

        # LR2.1 predicts goal difference from the listed Home team's perspective.
        rows21.append({
            "match_id": match_id + 1,
            "team_recent_gf": home_f["team_recent_gf"],
            "team_recent_ga": home_f["team_recent_ga"],
            "team_recent_points": home_f["team_recent_points"],
            "team_rest_days": home_f["team_rest_days"],
            "opponent_recent_gd": home_f["opponent_recent_gd"],
            "opponent_recent_win_rate": home_f["opponent_recent_win_rate"],
            "opponent_recent_clean_sheet_rate": home_f["opponent_recent_clean_sheet_rate"],
            "is_knockout": is_knockout,
            "goal_difference": match["home_goals"] - match["away_goals"],
        })

        # LR2.2 has two rows per fixture: one for each team.
        for team, opponent, own, goals in [
            (home, away, home_f, match["home_goals"]),
            (away, home, away_f, match["away_goals"]),
        ]:
            rows22.append({
                "match_id": match_id + 1,
                "team": team,
                "team_recent_gf": own["team_recent_gf"],
                "team_recent_ga": own["team_recent_ga"],
                "team_recent_points": own["team_recent_points"],
                "team_rest_days": own["team_rest_days"],
                "opponent_recent_gf": own["opponent_recent_gf"],
                "opponent_recent_ga": own["opponent_recent_ga"],
                "opponent_recent_points": own["opponent_recent_points"],
                "opponent_rest_days": own["opponent_rest_days"],
                "goals_scored": goals,
            })

    df21 = pd.DataFrame(rows21)
    df22 = pd.DataFrame(rows22)

    predictors21 = SHARED + MODEL21_EXTRA
    predictors22 = SHARED + MODEL22_EXTRA

    assert len(df21) == 104
    assert len(df22) == 208
    assert len(predictors21) == 8 and len(predictors22) == 8
    assert len(set(predictors21) & set(predictors22)) == 4

    df21 = df21[["match_id"] + predictors21 + ["goal_difference"]]
    df22 = df22[["match_id", "team"] + predictors22 + ["goals_scored"]]

    # Do not silently impute unknown form. Save diagnostic files and stop
    # if any required predictor is missing, so aliases/data coverage can be fixed.
    missing21 = df21[predictors21].isna().any(axis=1)
    missing22 = df22[predictors22].isna().any(axis=1)

    df21.to_csv(RAW / "regression_2_1.csv", index=False)
    df22.to_csv(RAW / "regression_2_2.csv", index=False)

    print("Datasets saved.")
    print(f"LR2.1 shape: {df21.shape} -> {RAW / 'regression_2_1.csv'}")
    print(f"LR2.2 shape: {df22.shape} -> {RAW / 'regression_2_2.csv'}")
    print("\nLR2.1 missing values by column:")
    print(df21.isna().sum().to_string())
    print("\nLR2.2 missing values by column:")
    print(df22.isna().sum().to_string())

    if missing21.any():
        print("\nLR2.1 rows with missing predictors:")
        print(df21.loc[missing21].to_string(index=False))
    if missing22.any():
        print("\nLR2.2 rows with missing predictors:")
        print(df22.loc[missing22].to_string(index=False))

    if missing21.any() or missing22.any():
        raise ValueError(
            "Datasets were saved for diagnosis, but some predictors are missing. "
            "Do not train models until the missing history is investigated."
        )

    print("\nValidation passed: 104 and 208 rows, 8 predictors per model, "
          "and exactly 4 shared predictors.")


if __name__ == "__main__":
    main()
