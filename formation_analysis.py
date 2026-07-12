"""Formation matchup baseline for local StatsBomb-style event JSON files.

This script scans the local project for StatsBomb-style event files, extracts
starting formations, infers final scores from event data, summarizes historical
formation-vs-formation performance, and writes simple tactical reports.

The model is descriptive. It reports historical matchup performance in this
dataset and does not estimate causal formation effects.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


DATA_ROOT = "."
OUTPUT_DIR = "outputs"
MIN_GAMES = 10
SMOOTHING_ALPHA = 10

LOGGER = logging.getLogger(__name__)


MATCH_ROW_COLUMNS = [
    "match_id",
    "team",
    "opponent",
    "formation",
    "opponent_formation",
    "goals_for",
    "goals_against",
    "goal_diff",
    "result",
    "points",
    "source_file",
]

SUMMARY_COLUMNS = [
    "formation",
    "opponent_formation",
    "games",
    "wins",
    "draws",
    "losses",
    "win_rate",
    "draw_rate",
    "loss_rate",
    "points_per_game",
    "goal_diff_per_game",
    "smoothed_win_rate",
]


def load_json(path: Path) -> Any | None:
    """Load a JSON file safely, returning None when it cannot be parsed."""
    try:
        with path.open("r", encoding="utf-8-sig") as handle:
            return json.load(handle)
    except (OSError, json.JSONDecodeError) as exc:
        LOGGER.warning("Skipping unreadable JSON file %s: %s", path, exc)
        return None


def is_event_file(data: Any) -> bool:
    """Return True when data looks like a StatsBomb event list."""
    if not isinstance(data, list) or not data:
        return False

    event_like = 0
    for event in data[:25]:
        if not isinstance(event, dict):
            continue
        if get_nested(event, "type.name") and get_nested(event, "team.name"):
            event_like += 1

    return event_like > 0


def get_nested(record: dict[str, Any], path: str, default: Any = None) -> Any:
    """Read a dotted key path from nested dictionaries."""
    current: Any = record
    for key in path.split("."):
        if not isinstance(current, dict) or key not in current:
            return default
        current = current[key]
    return current


def extract_match_id(path: Path) -> str:
    """Use the event filename as the match identifier."""
    return path.stem


def load_match_metadata(data_root: str | Path = DATA_ROOT) -> dict[str, dict[str, Any]]:
    """Load optional StatsBomb match metadata for score sanity checks."""
    root = Path(data_root)
    metadata: dict[str, dict[str, Any]] = {}

    for path in sorted(root.rglob("*.json")):
        if "matches" not in {part.lower() for part in path.parts}:
            continue

        data = load_json(path)
        if not isinstance(data, list):
            continue

        for match in data:
            if not isinstance(match, dict) or match.get("match_id") is None:
                continue

            match_id = str(match["match_id"])
            metadata[match_id] = {
                "home_team": get_nested(match, "home_team.home_team_name"),
                "away_team": get_nested(match, "away_team.away_team_name"),
                "home_score": match.get("home_score"),
                "away_score": match.get("away_score"),
                "source_file": str(path),
            }

    LOGGER.info("Loaded metadata for %d matches", len(metadata))
    return metadata


def normalize_formation(value: Any) -> str | None:
    """Convert formation values such as 433 or '4-3-3' to compact strings."""
    if value is None or value == "":
        return None

    if isinstance(value, float) and value.is_integer():
        value = int(value)

    text = str(value).strip().replace("-", "").replace(" ", "")
    return text if text else None


def extract_starting_formations(events: list[dict[str, Any]]) -> list[dict[str, str]]:
    """Extract the first Starting XI formation for each team in event order."""
    formations: list[dict[str, str]] = []
    seen_teams: set[str] = set()

    for event in events:
        if get_nested(event, "type.name") != "Starting XI":
            continue

        team = get_nested(event, "team.name")
        formation = normalize_formation(get_nested(event, "tactics.formation"))

        if not team or not formation or team in seen_teams:
            continue

        formations.append({"team": team, "formation": formation})
        seen_teams.add(team)

    return formations


def extract_tactical_shifts(events: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Collect Tactical Shift events as optional match notes."""
    shifts: list[dict[str, Any]] = []
    for event in events:
        if get_nested(event, "type.name") != "Tactical Shift":
            continue
        shifts.append(
            {
                "team": get_nested(event, "team.name"),
                "formation": normalize_formation(get_nested(event, "tactics.formation")),
                "minute": event.get("minute"),
                "second": event.get("second"),
                "period": event.get("period"),
            }
        )
    return shifts


def _is_match_play_period(period: Any) -> bool:
    """Exclude penalty shootouts where StatsBomb typically uses period 5."""
    if period is None:
        return True
    try:
        return int(period) in {1, 2, 3, 4}
    except (TypeError, ValueError):
        return True


def _event_time_key(event: dict[str, Any]) -> tuple[Any, Any, Any]:
    return (event.get("period"), event.get("minute"), event.get("second"))


def infer_score(
    events: list[dict[str, Any]], teams: list[str]
) -> tuple[dict[str, int] | None, str | None]:
    """Infer final score from goal events.

    Normal goals are Shot events with shot.outcome.name == "Goal".

    StatsBomb data often stores own goals as paired "Own Goal For" and
    "Own Goal Against" events at the same timestamp. This baseline credits the
    "Own Goal For" team and ignores the paired "Against" event to avoid
    double-counting. If only an "Own Goal Against" style event is present, it
    credits the other team, which is the safest two-team assumption.
    """
    if len(teams) != 2:
        return None, "score inference requires exactly two teams"

    team_set = set(teams)
    score = {team: 0 for team in teams}
    own_goal_for_times: set[tuple[Any, Any, Any]] = set()

    for event in events:
        if not _is_match_play_period(event.get("period")):
            continue

        team = get_nested(event, "team.name")
        event_type = get_nested(event, "type.name", "")

        if team not in team_set:
            continue

        if event_type == "Shot" and get_nested(event, "shot.outcome.name") == "Goal":
            score[team] += 1
        elif event_type == "Own Goal For":
            score[team] += 1
            own_goal_for_times.add(_event_time_key(event))

    for event in events:
        if not _is_match_play_period(event.get("period")):
            continue

        event_type = get_nested(event, "type.name", "")
        has_own_goal_against_flag = bool(event.get("own_goal_against"))
        if event_type != "Own Goal Against" and not has_own_goal_against_flag:
            continue

        if _event_time_key(event) in own_goal_for_times:
            continue

        conceding_team = get_nested(event, "team.name")
        opponents = [team for team in teams if team != conceding_team]
        if len(opponents) == 1:
            score[opponents[0]] += 1
        else:
            return None, "could not assign own goal to one opponent"

    return score, None


def _result_and_points(goals_for: int, goals_against: int) -> tuple[str, int]:
    if goals_for > goals_against:
        return "W", 3
    if goals_for == goals_against:
        return "D", 1
    return "L", 0


def _validate_score_against_metadata(
    match_id: str, score: dict[str, int], match_metadata: dict[str, dict[str, Any]] | None
) -> None:
    if not match_metadata or match_id not in match_metadata:
        return

    metadata = match_metadata[match_id]
    home_team = metadata.get("home_team")
    away_team = metadata.get("away_team")
    home_score = metadata.get("home_score")
    away_score = metadata.get("away_score")

    if home_team not in score or away_team not in score:
        return

    if score[home_team] != home_score or score[away_team] != away_score:
        LOGGER.warning(
            "Event-inferred score differs from match metadata for %s: "
            "events %s %s-%s %s, metadata %s %s-%s %s",
            match_id,
            home_team,
            score[home_team],
            score[away_team],
            away_team,
            home_team,
            home_score,
            away_score,
            away_team,
        )


def build_match_rows_from_event_file(
    path: Path, match_metadata: dict[str, dict[str, Any]] | None = None
) -> tuple[list[dict[str, Any]], str | None]:
    """Build the two long-format matchup rows for one event file."""
    data = load_json(path)
    if not is_event_file(data):
        return [], "not a StatsBomb-style event list"

    events = data
    match_id = extract_match_id(path)
    formations = extract_starting_formations(events)
    if len(formations) != 2:
        return [], f"expected two valid Starting XI formations, found {len(formations)}"

    tactical_shifts = extract_tactical_shifts(events)
    if tactical_shifts:
        LOGGER.debug(
            "%s contains %d Tactical Shift events; baseline uses Starting XI only",
            match_id,
            len(tactical_shifts),
        )

    team_a = formations[0]["team"]
    team_b = formations[1]["team"]
    teams = [team_a, team_b]
    score, reason = infer_score(events, teams)
    if score is None:
        return [], reason or "could not infer final score"
    _validate_score_against_metadata(match_id, score, match_metadata)

    team_a_goals = score[team_a]
    team_b_goals = score[team_b]
    team_a_result, team_a_points = _result_and_points(team_a_goals, team_b_goals)
    team_b_result, team_b_points = _result_and_points(team_b_goals, team_a_goals)

    source_file = str(path)
    rows = [
        {
            "match_id": match_id,
            "team": team_a,
            "opponent": team_b,
            "formation": formations[0]["formation"],
            "opponent_formation": formations[1]["formation"],
            "goals_for": team_a_goals,
            "goals_against": team_b_goals,
            "goal_diff": team_a_goals - team_b_goals,
            "result": team_a_result,
            "points": team_a_points,
            "source_file": source_file,
        },
        {
            "match_id": match_id,
            "team": team_b,
            "opponent": team_a,
            "formation": formations[1]["formation"],
            "opponent_formation": formations[0]["formation"],
            "goals_for": team_b_goals,
            "goals_against": team_a_goals,
            "goal_diff": team_b_goals - team_a_goals,
            "result": team_b_result,
            "points": team_b_points,
            "source_file": source_file,
        },
    ]
    return rows, None


def _looks_like_event_json_path(path: Path) -> bool:
    """Fast local sniff to avoid loading every match, lineup, and 360 file."""
    if path.parent.name.lower() == "events":
        return True

    known_non_event_dirs = {"lineups", "matches", "three-sixty", ".vscode", ".git"}
    if any(part.lower() in known_non_event_dirs for part in path.parts):
        return False

    try:
        sample = path.read_text(encoding="utf-8-sig", errors="ignore")[:32_000]
    except OSError:
        return False

    return '"Starting XI"' in sample and '"tactics"' in sample and '"team"' in sample


def build_all_match_rows(data_root: str | Path = DATA_ROOT) -> pd.DataFrame:
    """Scan recursively for event JSON files and build all matchup rows."""
    root = Path(data_root)
    match_metadata = load_match_metadata(root)
    rows: list[dict[str, Any]] = []
    candidate_count = 0
    skipped_count = 0

    for path in sorted(root.rglob("*.json")):
        if not _looks_like_event_json_path(path):
            continue

        candidate_count += 1
        match_rows, reason = build_match_rows_from_event_file(path, match_metadata)
        if match_rows:
            rows.extend(match_rows)
        else:
            skipped_count += 1
            LOGGER.warning("Skipping %s: %s", path, reason)

    LOGGER.info(
        "Processed %d event candidates, built rows for %d matches, skipped %d candidates",
        candidate_count,
        len(rows) // 2,
        skipped_count,
    )

    return pd.DataFrame(rows, columns=MATCH_ROW_COLUMNS)


def summarize_matchups(match_rows: pd.DataFrame) -> pd.DataFrame:
    """Summarize long-format team rows by formation matchup."""
    if match_rows.empty:
        return pd.DataFrame(columns=SUMMARY_COLUMNS[:-1])

    grouped = match_rows.groupby(["formation", "opponent_formation"], as_index=False)
    summary = grouped.agg(
        games=("match_id", "count"),
        wins=("result", lambda values: int((values == "W").sum())),
        draws=("result", lambda values: int((values == "D").sum())),
        losses=("result", lambda values: int((values == "L").sum())),
        total_points=("points", "sum"),
        total_goal_diff=("goal_diff", "sum"),
    )

    summary["win_rate"] = np.where(summary["games"] > 0, summary["wins"] / summary["games"], 0)
    summary["draw_rate"] = np.where(summary["games"] > 0, summary["draws"] / summary["games"], 0)
    summary["loss_rate"] = np.where(summary["games"] > 0, summary["losses"] / summary["games"], 0)
    summary["points_per_game"] = np.where(
        summary["games"] > 0, summary["total_points"] / summary["games"], 0
    )
    summary["goal_diff_per_game"] = np.where(
        summary["games"] > 0, summary["total_goal_diff"] / summary["games"], 0
    )

    return summary.drop(columns=["total_points", "total_goal_diff"])


def add_smoothed_metrics(summary: pd.DataFrame, alpha: float = SMOOTHING_ALPHA) -> pd.DataFrame:
    """Add smoothed win rate using the global win rate as the prior."""
    if summary.empty:
        result = summary.copy()
        result["smoothed_win_rate"] = pd.Series(dtype=float)
        return result

    result = summary.copy()
    total_games = result["games"].sum()
    global_win_rate = result["wins"].sum() / total_games if total_games else 0.0
    result["smoothed_win_rate"] = (
        result["wins"] + alpha * global_win_rate
    ) / (result["games"] + alpha)
    return result


def top_favorable_matchups(summary: pd.DataFrame, top_n: int = 5) -> pd.DataFrame:
    """Return the top favorable opponent formations for each formation."""
    if summary.empty:
        return pd.DataFrame(columns=SUMMARY_COLUMNS)

    sorted_summary = summary.sort_values(
        ["formation", "points_per_game", "win_rate", "goal_diff_per_game", "games"],
        ascending=[True, False, False, False, False],
    )
    return sorted_summary.groupby("formation", as_index=False).head(top_n).reset_index(drop=True)


def top_unfavorable_matchups(summary: pd.DataFrame, top_n: int = 5) -> pd.DataFrame:
    """Return the top unfavorable opponent formations for each formation."""
    if summary.empty:
        return pd.DataFrame(columns=SUMMARY_COLUMNS)

    sorted_summary = summary.sort_values(
        ["formation", "points_per_game", "win_rate", "goal_diff_per_game", "games"],
        ascending=[True, True, True, True, False],
    )
    return sorted_summary.groupby("formation", as_index=False).head(top_n).reset_index(drop=True)


RULE_LIBRARY: dict[tuple[str, str], list[str]] = {
    ("433", "442"): [
        "Use the three-player midfield to create central overloads.",
        "Be careful against two-striker pressure on center backs.",
        "Wingers should pin the opponent fullbacks.",
        "The defensive midfielder must protect second balls and counterattacks.",
    ],
    ("442", "433"): [
        "Screen passes into the opponent defensive midfielder.",
        "Use the two strikers to press split center backs and force wide buildup.",
        "Wide midfielders must track fullbacks before breaking forward.",
        "Look for early crosses when the opponent fullbacks are advanced.",
    ],
    ("433", "352"): [
        "Attack the space behind the wing-backs.",
        "Use wide wingers to stretch the back three.",
        "Prevent central overloads from the opponent two forwards and midfield three.",
        "Switch play quickly before the far-side wing-back can recover.",
    ],
    ("352", "433"): [
        "Use the front two to occupy both center backs and create layoff options.",
        "Keep wing-backs ready to defend wide isolations against wingers.",
        "Protect the half-spaces when the opponent eights run beyond midfield.",
        "Use the extra center back to step into midfield when pressure is light.",
    ],
    ("4231", "433"): [
        "Use the number 10 between the opponent midfield and defensive lines.",
        "Keep the double pivot compact against the opponent midfield three.",
        "Fullbacks should choose forward moments carefully to avoid winger counters.",
        "Press the opponent defensive midfielder with the striker and number 10.",
    ],
    ("433", "4231"): [
        "Ask one central midfielder to manage the opponent number 10 zone.",
        "Use the midfield three to circulate around the double pivot.",
        "Wingers can isolate fullbacks when the opponent wide midfielders tuck in.",
        "Counterpress immediately because the opponent has central transition outlets.",
    ],
    ("442", "352"): [
        "Shift quickly to protect wide channels against wing-backs.",
        "Use two strikers to prevent the back three from building freely.",
        "Central midfielders must avoid being outnumbered by the opponent three.",
        "Attack early into channels outside the outside center backs.",
    ],
    ("352", "442"): [
        "Use the spare center back to carry the ball into midfield.",
        "Wing-backs can pin the opponent wide midfielders deep.",
        "The midfield three should create passing triangles around the opponent two.",
        "Track both strikers tightly when defending direct play.",
    ],
}


def _generic_suggestions(our_formation: str, opponent_formation: str) -> list[str]:
    suggestions = [
        "Keep rest defense balanced before committing numbers forward.",
        "Use early possession phases to identify where the opponent leaves space.",
        "Adjust pressing triggers based on the opponent buildup shape.",
    ]

    if our_formation[:1] == "4" and opponent_formation[:1] == "3":
        suggestions.append("Test the space outside the opponent outside center backs.")
    elif our_formation[:1] == "3" and opponent_formation[:1] == "4":
        suggestions.append("Use the spare center back carefully without losing wide coverage.")
    else:
        suggestions.append("Focus on compact distances between lines and quick switches of play.")

    return suggestions


def _format_metric(value: Any, decimals: int = 2) -> str:
    if value is None or pd.isna(value):
        return "n/a"
    return f"{float(value):.{decimals}f}"


def generate_strategy(
    our_formation: str, opponent_formation: str, matchup_summary: pd.DataFrame
) -> str:
    """Generate a rule-based descriptive tactical report."""
    our_formation = normalize_formation(our_formation) or str(our_formation)
    opponent_formation = normalize_formation(opponent_formation) or str(opponent_formation)

    row = None
    if not matchup_summary.empty:
        formation_values = matchup_summary["formation"].map(normalize_formation)
        opponent_values = matchup_summary["opponent_formation"].map(normalize_formation)
        matches = matchup_summary[
            (formation_values == our_formation)
            & (opponent_values == opponent_formation)
        ]
        if not matches.empty:
            row = matches.iloc[0]

    games = int(row["games"]) if row is not None else 0
    win_rate = row["win_rate"] if row is not None else None
    points_per_game = row["points_per_game"] if row is not None else None
    goal_diff_per_game = row["goal_diff_per_game"] if row is not None else None

    if games < MIN_GAMES:
        interpretation = "unknown due to insufficient data"
    elif points_per_game >= 1.6 and goal_diff_per_game >= 0:
        interpretation = "favorable"
    elif points_per_game <= 1.1 and goal_diff_per_game < 0:
        interpretation = "unfavorable"
    else:
        interpretation = "balanced"

    suggestions = RULE_LIBRARY.get(
        (our_formation, opponent_formation),
        _generic_suggestions(our_formation, opponent_formation),
    )

    lines = [
        f"Strategy report: {our_formation} vs {opponent_formation}",
        "",
        "Historical matchup performance in this dataset is descriptive, not causal.",
        f"Our formation: {our_formation}",
        f"Opponent formation: {opponent_formation}",
        f"Historical games: {games}",
        f"Win rate: {_format_metric(win_rate)}",
        f"Points per game: {_format_metric(points_per_game)}",
        f"Goal difference per game: {_format_metric(goal_diff_per_game)}",
        f"Interpretation: {interpretation}",
        "",
        "Simple tactical suggestions:",
    ]
    lines.extend(f"- {suggestion}" for suggestion in suggestions)
    return "\n".join(lines)


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

    output_dir = Path(OUTPUT_DIR)
    output_dir.mkdir(parents=True, exist_ok=True)

    LOGGER.info("Scanning local JSON files under %s", Path(DATA_ROOT).resolve())
    match_rows = build_all_match_rows(DATA_ROOT)

    rows_path = output_dir / "formation_match_rows.csv"
    match_rows.to_csv(rows_path, index=False)
    LOGGER.info("Saved %d matchup rows to %s", len(match_rows), rows_path)

    summary = summarize_matchups(match_rows)
    summary = add_smoothed_metrics(summary, SMOOTHING_ALPHA)
    filtered_summary = summary[summary["games"] >= MIN_GAMES].copy()

    summary_path = output_dir / "formation_matchup_summary.csv"
    filtered_summary.to_csv(summary_path, index=False)
    LOGGER.info(
        "Saved %d formation matchup summary rows to %s with MIN_GAMES=%d",
        len(filtered_summary),
        summary_path,
        MIN_GAMES,
    )

    favorable = top_favorable_matchups(filtered_summary)
    unfavorable = top_unfavorable_matchups(filtered_summary)

    favorable_path = output_dir / "top_favorable_matchups.csv"
    unfavorable_path = output_dir / "top_unfavorable_matchups.csv"
    favorable.to_csv(favorable_path, index=False)
    unfavorable.to_csv(unfavorable_path, index=False)
    LOGGER.info("Saved top favorable matchups to %s", favorable_path)
    LOGGER.info("Saved top unfavorable matchups to %s", unfavorable_path)

    report = generate_strategy("433", "442", summary)
    report_path = output_dir / "example_strategy_report_433_vs_442.txt"
    report_path.write_text(report, encoding="utf-8")
    LOGGER.info("Saved example strategy report to %s", report_path)


if __name__ == "__main__":
    main()
