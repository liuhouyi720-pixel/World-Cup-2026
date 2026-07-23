import pandas as pd
from .config import DATA, PREDICTIONS, STAGE_ORDER
from .name_normalizer import normalize_team_name

REQUIRED_MATCH_COLUMNS = {"match_id", "kickoff", "stage", "home_team", "away_team", "home_score", "away_score"}

def load_matches() -> pd.DataFrame:
    path = DATA / "matches.csv"
    if not path.exists():
        raise FileNotFoundError(f"Missing {path}. Run scripts/import_2026_results.py to rebuild the offline cache.")
    matches = pd.read_csv(path, keep_default_na=False)
    missing = REQUIRED_MATCH_COLUMNS - set(matches.columns)
    if missing:
        raise ValueError(f"matches.csv is missing columns: {sorted(missing)}")
    matches["kickoff"] = pd.to_datetime(matches.kickoff, utc=True, errors="coerce")
    matches["home_team"] = matches.home_team.map(normalize_team_name)
    matches["away_team"] = matches.away_team.map(normalize_team_name)
    return matches.sort_values(["kickoff", "match_id"]).reset_index(drop=True)

def validate_matches(matches: pd.DataFrame) -> list[str]:
    issues: list[str] = []
    if matches.match_id.duplicated().any(): issues.append("Duplicate match IDs")
    if len(matches) != 104: issues.append(f"Expected 104 matches; found {len(matches)}")
    if matches.kickoff.isna().any(): issues.append("Invalid kickoff time")
    if matches[["home_team", "away_team"]].isna().any().any(): issues.append("Blank team name")
    if (matches.home_team == matches.away_team).any(): issues.append("A team is playing itself")
    unknown = set(matches.stage) - set(STAGE_ORDER)
    if unknown: issues.append(f"Unknown stages: {sorted(unknown)}")
    for column in ("home_score", "away_score"):
        scores = pd.to_numeric(matches[column], errors="coerce")
        if scores.isna().any() or (scores < 0).any(): issues.append(f"Invalid {column}")
    return issues

def load_predictions() -> pd.DataFrame:
    path = PREDICTIONS / "backtest_predictions.csv"
    return pd.read_csv(path) if path.exists() else pd.DataFrame()

def load_teams() -> list[str]:
    matches = load_matches()
    return sorted(set(matches.home_team) | set(matches.away_team))
