# Data dictionary

## `matches.csv`

`match_id` unique source identifier; `kickoff` timezone-aware start; `stage`; `group`; `home_team`; `away_team`; 90/120-minute published `home_score` and `away_score`; `winner` including shootout winner when supplied; `status` (FT/AET/Pens); `source_url`; and `result_note`.

## Backtest predictions

Identity: `match_id`, `timestamp`, `mode`, `stage`, `group`, `team_a`, `team_b`. Probabilities: `team_a_win_90`, `draw_90`, `team_b_win_90`, optional advancement probabilities. Interpretation: predicted score/winner, `components`, `final_weights`, `availability`, `confidence`, `limitations`, and `top_scorelines`. Evaluation: actual scores/winner/status and `correct_prediction`.

## xT profile

Team, experiment, source competition/season, experiment-local cluster, model-derived description, centroid distance, 192-zone created-xT vector, third and channel shares, availability, and limitation.

## Simulation JSON

Mode and bracket note, group tables, best-third ranking, model champion, and every model-generated group/knockout prediction.

## Evaluation

`metrics.json` stores match count, three-class accuracy, non-draw winner accuracy, log loss, multiclass Brier score, and knockout count. `leakage_audit.csv` records prediction timestamp, prior history count, target-in-form flag, future-use flag, and pass status.

