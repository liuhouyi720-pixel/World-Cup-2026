from dataclasses import asdict, dataclass, field
from typing import Any

@dataclass
class XTStyleProfile:
    team: str
    data_available: bool = False
    experiment: str | None = None
    source_competition: str | None = None
    source_season: str | None = None
    cluster_id: int | None = None
    cluster_label: str | None = None
    centroid_distance: float | None = None
    vector: list[float] | None = None
    spatial: dict[str, float] = field(default_factory=dict)
    representatives: list[str] = field(default_factory=list)
    limitation: str = "No compatible historical xT profile is available."

    @property
    def feature_vector(self) -> list[float] | None:
        return self.vector

    @property
    def representative_teams(self) -> list[str]:
        return self.representatives

@dataclass
class MatchPrediction:
    match_id: str
    timestamp: str
    mode: str
    stage: str
    group: str | None
    team_a: str
    team_b: str
    team_a_win_90: float
    draw_90: float
    team_b_win_90: float
    team_a_advance: float | None
    team_b_advance: float | None
    predicted_score_a: int
    predicted_score_b: int
    predicted_winner: str
    components: dict[str, float | None]
    final_weights: dict[str, float]
    availability: dict[str, bool]
    confidence: str
    limitations: list[str]
    top_scorelines: list[dict[str, Any]]

    @property
    def prediction_timestamp(self) -> str:
        return self.timestamp

    def as_record(self) -> dict[str, Any]:
        result = asdict(self)
        for key in ("components", "final_weights", "availability", "top_scorelines"):
            result[key] = str(result[key])
        result["limitations"] = " | ".join(result["limitations"])
        return result

    to_dict = as_record
