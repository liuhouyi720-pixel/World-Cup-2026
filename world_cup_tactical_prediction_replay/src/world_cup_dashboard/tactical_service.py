import pandas as pd
from .config import SOURCE_OUTPUTS

def normalize_formation(value) -> str | None:
    if value is None or pd.isna(value):
        return None
    digits = "".join(character for character in str(value).split(".")[0] if character.isdigit())
    return "-".join(digits) if len(digits) in (3, 4, 5) else None

class TacticalService:
    def __init__(self) -> None:
        summary_path = SOURCE_OUTPUTS / "formation_matchup_summary.csv"
        rows_path = SOURCE_OUTPUTS / "formation_match_rows.csv"
        self.summary = pd.read_csv(summary_path) if summary_path.exists() else pd.DataFrame()
        self.rows = pd.read_csv(rows_path) if rows_path.exists() else pd.DataFrame()
        if not self.summary.empty:
            self.summary["normalized_formation"] = self.summary.formation.map(normalize_formation)
            self.summary["normalized_opponent"] = self.summary.opponent_formation.map(normalize_formation)

    def common_formations(self, team: str) -> list[str]:
        if self.rows.empty:
            return []
        rows = self.rows[self.rows.team.eq(team)]
        if rows.empty:
            return []
        return rows.formation.map(normalize_formation).dropna().value_counts().head(3).index.tolist()

    def matchup(self, formation_a: str | None, formation_b: str | None) -> tuple[float | None, int, str]:
        if self.summary.empty or not formation_a or not formation_b:
            return None, 0, "unavailable"
        direct = self.summary[
            self.summary.normalized_formation.eq(formation_a)
            & self.summary.normalized_opponent.eq(formation_b)
        ]
        if not direct.empty:
            row = direct.iloc[0]
            return float(row.smoothed_win_rate) - 0.5, int(row.games), "exact"
        reverse = self.summary[
            self.summary.normalized_formation.eq(formation_b)
            & self.summary.normalized_opponent.eq(formation_a)
        ]
        if not reverse.empty:
            row = reverse.iloc[0]
            return 0.5 - float(row.smoothed_win_rate), int(row.games), "reversed"
        average = self.summary[self.summary.normalized_formation.eq(formation_a)]
        if not average.empty:
            return float(average.smoothed_win_rate.mean()) - 0.5, int(average.games.sum()), "formation-average"
        return None, 0, "unavailable"

