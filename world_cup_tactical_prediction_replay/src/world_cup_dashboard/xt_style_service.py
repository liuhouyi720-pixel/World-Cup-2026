import numpy as np
import pandas as pd
from .config import SOURCE_OUTPUTS
from .name_normalizer import normalize_team_name
from .schemas import XTStyleProfile

FILES = {
    "C": ("experiment_C_multichannel/clustered_team_seasons_multichannel.csv", "cluster_multichannel", "experiment_C_multichannel/cluster_representatives_multichannel.csv"),
    "B": ("experiment_B_smoothed/clustered_team_seasons_smoothed.csv", "cluster_smoothed", "experiment_B_smoothed/cluster_representatives_smoothed.csv"),
    "A": ("experiment_A_raw/clustered_team_seasons_raw.csv", "cluster_raw", "experiment_A_raw/cluster_representatives_raw.csv"),
}

def cluster_label(row: pd.Series) -> str:
    labels = []
    if row.get("attacking_third_share", 0) >= 0.70:
        labels.append("Threat concentrated in the attacking third")
    elif row.get("middle_third_share", 0) >= 0.28:
        labels.append("Threat more concentrated through midfield")
    if row.get("left_side_share", 0) > row.get("right_side_share", 0) + 0.06:
        labels.append("Higher left-side share")
    elif row.get("right_side_share", 0) > row.get("left_side_share", 0) + 0.06:
        labels.append("Higher right-side share")
    else:
        labels.append("Relatively balanced left/right distribution")
    labels.append("Higher carry-created share" if row.get("carry_xT_share", 0) > 0.38 else "Higher pass-created share")
    return "；".join(labels)

class XTStyleService:
    def __init__(self, preferred: str = "C") -> None:
        self.order = [preferred] + [code for code in "CBA" if code != preferred]
        self.tables: dict[str, tuple[pd.DataFrame, str]] = {}
        self.profiles: dict[str, XTStyleProfile] = {}

    def _table(self, code: str) -> tuple[pd.DataFrame, str]:
        if code not in self.tables:
            relative_path, cluster_column, _ = FILES[code]
            path = SOURCE_OUTPUTS / relative_path
            if not path.exists():
                self.tables[code] = (pd.DataFrame(), cluster_column)
            else:
                table = pd.read_csv(path).copy()
                table["canonical_team"] = table.team_name.map(normalize_team_name)
                self.tables[code] = (table, cluster_column)
        return self.tables[code]

    def profile(self, team: str) -> XTStyleProfile:
        canonical = normalize_team_name(team)
        if canonical in self.profiles:
            return self.profiles[canonical]
        for code in self.order:
            table, cluster_column = self._table(code)
            candidates = table[table.canonical_team.eq(canonical)].copy() if not table.empty else table
            if candidates.empty:
                continue
            row = candidates.sort_values(["season_name", "match_count"], ascending=False).iloc[0]
            zone_columns = [column for column in table if column.startswith("created_z")]
            spatial = {
                key: float(row.get(key, np.nan))
                for key in (
                    "defensive_third_share", "middle_third_share", "attacking_third_share",
                    "left_side_share", "center_share", "right_side_share",
                    "pass_xT_share", "carry_xT_share",
                )
            }
            cluster = int(row[cluster_column])
            representatives: list[str] = []
            representative_path = SOURCE_OUTPUTS / FILES[code][2]
            if representative_path.exists():
                representative_table = pd.read_csv(representative_path)
                representative_cluster = cluster_column if cluster_column in representative_table else representative_table.columns[0]
                representatives = representative_table[representative_table[representative_cluster].eq(cluster)].team_name.astype(str).tolist()
            profile = XTStyleProfile(
                team=canonical,
                data_available=True,
                experiment=code,
                source_competition=str(row.competition_name),
                source_season=str(row.season_name),
                cluster_id=cluster,
                cluster_label=cluster_label(row),
                centroid_distance=float(row.get("distance_to_centroid", np.nan)),
                vector=row[zone_columns].fillna(0).astype(float).tolist(),
                spatial=spatial,
                representatives=representatives,
                limitation="Historical proxy profile, not 2026 event-level data.",
            )
            self.profiles[canonical] = profile
            return profile
        profile = XTStyleProfile(team=canonical)
        self.profiles[canonical] = profile
        return profile

    def similarity(self, team_a: str, team_b: str) -> float | None:
        profile_a, profile_b = self.profile(team_a), self.profile(team_b)
        if not profile_a.vector or not profile_b.vector:
            return None
        vector_a, vector_b = np.array(profile_a.vector), np.array(profile_b.vector)
        denominator = np.linalg.norm(vector_a) * np.linalg.norm(vector_b)
        return float(vector_a @ vector_b / denominator) if denominator else None
