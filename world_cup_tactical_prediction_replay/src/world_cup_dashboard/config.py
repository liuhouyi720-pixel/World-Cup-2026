from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE_ROOT = ROOT.parent
DATA = ROOT / "data" / "world_cup_2026"
OUT = ROOT / "outputs" / "world_cup_dashboard"
PREDICTIONS = OUT / "predictions"
REPORTS = OUT / "reports"
EVALUATION = OUT / "evaluation"
SIMULATION = OUT / "simulation"
SOURCE_OUTPUTS = SOURCE_ROOT / "outputs"

# Descriptive aliases retained for service compatibility.
PACKAGE_ROOT = ROOT
PROJECT_ROOT = SOURCE_ROOT
SOURCE_REPOSITORY = SOURCE_ROOT
DATA_DIR = DATA
OUTPUT_DIR = OUT
PREDICTIONS_DIR = PREDICTIONS
REPORTS_DIR = REPORTS
EVALUATION_DIR = EVALUATION
SIMULATION_DIR = SIMULATION
EXPERIMENT_DIR = SOURCE_OUTPUTS

DEFAULT_WEIGHTS = {
    "strength": 0.45,
    "xt_style": 0.20,
    "tactical_matchup": 0.20,
    "recent_form": 0.15,
}
NEUTRAL_SITE = True
ENABLE_LLM_REPORTS = False
STAGE_ORDER = {
    "Group": 1,
    "Round of 32": 2,
    "Round of 16": 3,
    "Quarter-finals": 4,
    "Semi-finals": 5,
    "Third place": 6,
    "Final": 7,
}

def ensure_dirs() -> None:
    for path in (PREDICTIONS, REPORTS, EVALUATION, SIMULATION):
        path.mkdir(parents=True, exist_ok=True)

ensure_output_dirs = ensure_dirs

