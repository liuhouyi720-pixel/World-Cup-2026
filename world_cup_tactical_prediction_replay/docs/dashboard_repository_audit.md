# Dashboard repository audit

Audit date: 2026-07-22. The dashboard was created in a new folder and does not overwrite the source experiments.

## Discovered reusable artifacts

| Area | Reused file | Important columns |
| --- | --- | --- |
| xT grid | `../outputs/global_xt_grid_12x16.csv` and `global_xt_zone_values.csv` | zone coordinates and xT values |
| Experiment A | `clustered_team_seasons_raw.csv`, summaries, representatives, centroids | `team_name`, competition/season, `cluster_raw`, 192 zones |
| Experiment B | `clustered_team_seasons_smoothed.csv`, summaries, representatives, centroids | `team_name`, `cluster_smoothed`, spatial shares |
| Experiment C | `clustered_team_seasons_multichannel.csv`, summaries, representatives, channel summaries, centroids | 288 rows × 417 columns; created/received zones, `cluster_multichannel`, spatial and pass/carry shares |
| Formations | `formation_matchup_summary.csv` | 105 matchup rows; games, W/D/L rates, goal difference, smoothed win rate |
| Tactical rows | `formation_match_rows.csv` | 8,470 team-match rows; teams, formations, scores, result |
| Metadata | `match_metadata.csv` | 3,961 historical matches; competition, season, date, teams |
| Proofs of concept | Spain–France, Argentina–England, Argentina–Spain output folders and notebooks | transparent probabilities, xG and xT reports, tactical scenarios |

No reusable serialized KMeans/PCA/Scaler PKL or joblib artifact was found. The dashboard therefore reads saved cluster assignments and spatial vectors and does not pretend to refit the original clustering pipeline.

## Tournament data

No complete 2026 schedule/results file existed locally. A 104-match completed-results cache was created from The Stats Zone, with TheStatsAPI's 104-fixture CSV retained for schedule provenance. The source URLs and access date are documented in `data/world_cup_2026/DATA_SOURCES.md`. The application does not make live requests.

## Coverage and fallbacks

Experiment C is primary, then B, then A. Compatible profiles exist mainly for historical World Cup, Euro, Copa América, and AFCON participants; missing teams show an unavailable card. Formation data is club-heavy, so many national-team exact scenarios are unavailable. Neutral strength is used when no historical xT proxy exists. These gaps lower confidence and trigger weight renormalization.

## Orientation decision

The original experiment stores 192 zones as a 12×16 grid. The dashboard preserves the stored order and labels attacking direction, without transposition or rotation. Because the notebook is the ultimate coordinate authority, the UI includes an orientation caveat.

