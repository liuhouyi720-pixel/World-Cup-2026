# 2026 World Cup Tactical Prediction Replay

`2026世界杯战术预测回放` is an offline-first Streamlit application that completes the existing football analytics project as a chronological historical replay. It combines historical xT spatial profiles, formation-matchup statistics, a small transparent strength proxy, tournament form available before kickoff, natural-language reports, evaluation, and a separate full-tournament simulation.

## What is included

- Seven Chinese-first views: overview, prediction replay, match report, team comparison, tournament simulator, evaluation, and methodology.
- 104 cached 2026 World Cup results and one prediction/report per match.
- Historical backtest mode with form updated only after a prediction is recorded.
- Full simulation mode whose knockout teams come from predicted group tables.
- Experiment C → B → A xT fallback, explicit missing-data cards, renormalized weights, and no fabricated heatmaps.
- CSV, JSON, and Markdown downloads.

## Setup and run

```powershell
cd "D:\UIUC\Projects\World Cup 2026\world_cup_tactical_prediction_replay"
python -m pip install -r requirements-dashboard.txt
# Only needed if the committed offline cache is missing:
python scripts/import_2026_results.py
python -m src.world_cup_dashboard.batch_predict --mode backtest
python -m src.world_cup_dashboard.batch_predict --mode full_simulation
python -m streamlit run app.py
```

On Windows, `run_dashboard.bat` launches the app. On macOS/Linux, use `sh run_dashboard.sh`.

## Inputs and outputs

The application reuses `../outputs/experiment_A_raw`, `experiment_B_smoothed`, `experiment_C_multichannel`, `formation_matchup_summary.csv`, and `formation_match_rows.csv`. Tournament inputs are cached in `data/world_cup_2026`; the running app does not require internet access.

Generated files are under `outputs/world_cup_dashboard`: backtest CSV, 104 JSON and Markdown reports, leakage audit, metrics, calibration table, and full-simulation JSON.

## Architecture

`app.py` is presentation only. Services under `src/world_cup_dashboard` isolate loading, name normalization, xT, tactics, strength, chronological form, probability mapping, group tables, bracket progression, report generation, visualization, exports, and evaluation. The original notebooks and experiments are read-only inputs.

## Common errors

- `No module named streamlit`: run the requirements install command above.
- Missing `matches.csv`: restore the committed cache or run `python scripts/import_2026_results.py` once while online.
- Empty heatmap: the selected team has no compatible national-team xT proxy; this is expected and lowers confidence.
- Slow first page load: Experiment C contains 417 columns; subsequent access is cached.

## Screenshot checklist

Capture the overview, one expert match report with heatmaps, the full-simulation group tables, and the evaluation page after launching locally.

This is an end-to-end football analytics demonstration, not a scientifically validated betting model.
