# Project Structure and Artifact Catalog

This guide explains where each part of the repository belongs, what it consumes,
and what it produces. It documents the existing project without changing its
analysis or adding new functionality.

## Recommended Review Path

1. Read the root [`README.md`](../README.md) for the project narrative and
   headline results.
2. Inspect [`06_build_team_season_xt_matrices.ipynb`](../06_build_team_season_xt_matrices.ipynb)
   for the most complete data-engineering workflow.
3. Compare notebooks
   [`07A_clustering_raw_xt_matrix.ipynb`](../07A_clustering_raw_xt_matrix.ipynb),
   [`07B_clustering_smoothed_xt_matrix.ipynb`](../07B_clustering_smoothed_xt_matrix.ipynb),
   and
   [`07C_clustering_multichannel_xt_features.ipynb`](../07C_clustering_multichannel_xt_features.ipynb)
   for the controlled feature-representation experiments.
4. Review [`formation_analysis.py`](../formation_analysis.py) for reusable,
   defensive Python code.
5. Open
   [`10_predict_spain_vs_france_world_cup_semifinal.ipynb`](../10_predict_spain_vs_france_world_cup_semifinal.ipynb)
   or the saved report under
   [`outputs/spain_france_prediction/`](../outputs/spain_france_prediction/)
   for an end-to-end communication example.
6. Read
   [`world-cup-2026-experiment-report.docx`](world-cup-2026-experiment-report.docx)
   for the formal experiment record.

## Versioned Source Areas

| Path | Responsibility | Main inputs | Main outputs |
| --- | --- | --- | --- |
| `05_team_xt_surface_visualization.ipynb` | Validate and visualize team xT surfaces | Generated team-zone tables | Spatial summaries and PNG surfaces |
| `06_build_team_season_xt_matrices.ipynb` | Scan JSON, train the global xT model, and build team-season features | `archive/data/` | Combined feature CSVs, build log, validation plots |
| `07A_clustering_raw_xt_matrix.ipynb` | Raw created-xT clustering baseline | Combined feature CSV | Experiment A labels, metrics, centroids, representatives |
| `07B_clustering_smoothed_xt_matrix.ipynb` | Smoothing comparison | Combined feature CSV and Experiment A labels | Experiment B results and A/B comparison |
| `07C_clustering_multichannel_xt_features.ipynb` | Created/received xT feature extension | Combined feature CSV and prior labels | Experiment C results and cross-experiment comparisons |
| `formation_analysis.py` | Extract and summarize formation matchups | StatsBomb-style match and event JSON | Match rows, matchup summaries, tactical text report |
| `notebooks/` | Focused formation-analysis interfaces | `formation_analysis.py` and local data | Tables and example strategy report |
| `10_...` through `16_...ipynb` | Historical match prediction case studies | xT clusters, formation summaries, raw shot events | Probabilities, plots, and Markdown reports |
| `Learning/` | Exploratory learning work | Local football data | Notebook-specific analysis and visualization |
| `outputs/` | Reproducible result artifacts | Notebook and script runs | CSV tables, PNG figures, Markdown reports, logs |
| `docs/` | Human-facing project documentation | Repository evidence | Structure guide and experiment report |

## Data Areas

| Path | Contents | Version-control treatment |
| --- | --- | --- |
| `archive/data/` | StatsBomb competitions, matches, events, lineups, and selected 360 JSON | Local source dataset; JSON is ignored |
| `Reference and articles/` | Local academic and technical reading material | PDF files are ignored |
| `formations analysis/outputs/` | Generated formation summary CSVs | CSV files are ignored and rebuildable |
| `world_cup_tactical_prediction_replay/` | Local cached/generated replay artifacts | Not part of the tracked source workflow |

The repository keeps generated CSV files out of Git while retaining selected
plots and written reports that help a reviewer inspect the results quickly.

## Main Data Contracts

### Raw event input

The pipeline expects StatsBomb-style JSON:

- competition and season metadata
- match metadata
- event lists keyed by match ID
- lineups
- optional 360 data

### Team-season clustering table

The completed build produced 922 team-season rows and 413 total columns. The
table contains:

- team, competition, season, and match-count metadata
- raw created xT features
- normalized created xT features
- received xT features
- pass-created and carry-created xT features
- action-count distributions
- spatial summary measures

Quality filtering reduces the clustering sample to 288 rows.

### Clustering result contract

Each experiment directory records:

- the filtered sample and assigned cluster
- metric scores for candidate `k` values
- PCA variance information
- cluster centroids
- cluster summaries
- representative team-seasons
- naming-support and top-zone tables
- interpretation plots
- a one-row experiment summary

### Prediction report contract

Prediction output folders generally contain:

- projected score or advancement probabilities
- scoreline heatmaps
- xT or xG comparison figures
- feature importance and calibration plots where applicable
- a Markdown report describing data, assumptions, results, and limitations

## Naming Conventions

- Numbered notebooks indicate the intended workflow order.
- Experiment suffixes identify the feature representation:
  `raw`, `smoothed`, or `multichannel`.
- Output folders group artifacts by experiment or match case study.
- `created_zNNN` and `received_zNNN` identify spatial zones in the flattened
  16 x 12 pitch grid.

## Reproducibility Notes

- Paths are repository-relative in the main pipeline.
- The build log records file counts, errors, event counts, timestamps, and
  generated paths.
- Numeric matrices—not rendered images—are used as clustering features.
- Generated CSVs are excluded from version control and should be regenerated
  from the tracked notebooks plus local raw data.
- Prediction reports rely on historical proxies and should not be generalized
  to live 2026 conditions.
