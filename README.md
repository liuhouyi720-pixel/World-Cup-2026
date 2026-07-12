# Formation Matchup Baseline

This project includes a simple tactical analysis baseline for local
StatsBomb-style event JSON data. The baseline extracts each team's starting
formation, infers the match score from event data, builds formation-vs-formation
matchup tables, and generates rule-based tactical suggestions.

The analysis is descriptive. It reports historical matchup performance in this
dataset and does not claim that one formation causally counters another.

## Data Assumptions

- Event data is stored locally somewhere inside this project folder.
- The script recursively scans for JSON files that look like StatsBomb event
  files. It does not use the StatsBomb API, internet access, or remote data.
- A valid event file is expected to be a list of event dictionaries with fields
  such as `type.name`, `team.name`, `tactics.formation`, `shot.outcome.name`,
  `minute`, `second`, and `period`.
- The first version uses only `Starting XI` formations for matchup analysis.
  `Tactical Shift` events are detected and logged as notes, but they are not
  used in the summary metrics.
- Scores are inferred from event data by counting `Shot` events where
  `shot.outcome.name == "Goal"` and by handling StatsBomb-style own-goal events.
  When paired `Own Goal For` and `Own Goal Against` events are present, the
  script credits the `Own Goal For` team and ignores the paired `Against` event
  to avoid double-counting.
- If local StatsBomb match metadata is available under a `matches` directory,
  the script loads it as a sanity check against the event-inferred score. The
  event data remains the primary score source for this baseline.

## How To Run

From the project root:

```bash
pip install -r requirements.txt
```

```bash
python formation_analysis.py
```

Basic configuration is at the top of `formation_analysis.py`:

```python
DATA_ROOT = "."
OUTPUT_DIR = "outputs"
MIN_GAMES = 10
SMOOTHING_ALPHA = 10
```

## Output Files

The script writes:

- `outputs/formation_match_rows.csv`: long-format team-match rows, with two rows
  per match.
- `outputs/formation_matchup_summary.csv`: formation-vs-opponent-formation
  summary after applying the `MIN_GAMES` filter.
- `outputs/top_favorable_matchups.csv`: top five historically favorable
  opponent formations for each formation in the filtered summary.
- `outputs/top_unfavorable_matchups.csv`: top five historically unfavorable
  opponent formations for each formation in the filtered summary.
- `outputs/example_strategy_report_433_vs_442.txt`: one readable example
  strategy report.

The optional notebook `notebooks/formation_matchup_analysis.ipynb` loads these
generated outputs and shows common formations, matchup summaries, top 433
matchups, and an example strategy report.

## Metrics

- `games`: number of team-match rows for the formation matchup.
- `wins`, `draws`, `losses`: results from the perspective of `formation` against
  `opponent_formation`.
- `win_rate`, `draw_rate`, `loss_rate`: result counts divided by games.
- `points_per_game`: average points using 3 for a win, 1 for a draw, and 0 for a
  loss.
- `goal_diff_per_game`: average goals for minus goals against.
- `smoothed_win_rate`: small-sample-adjusted win rate:

```text
(wins + alpha * global_win_rate) / (games + alpha)
```

The default `alpha` is 10.

## Limitations

- This baseline uses starting formations only.
- Formation matchup results are descriptive, not causal.
- Results can be biased by team strength, league, season, home advantage, red
  cards, and player quality.
- Event-data-inferred scores may not perfectly handle every edge case,
  especially own goals or penalty shootouts.
- A future version should add team strength controls, home/away controls,
  competition/season controls, and tactical behavior features such as PPDA, long
  pass rate, cross rate, pressing height, and direct speed.
