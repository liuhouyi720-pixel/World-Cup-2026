# Team-Season xT Tactical Clustering Experiments

## Project Goal

This project uses StatsBomb event data and Expected Threat values to build
team-season spatial feature matrices for unsupervised clustering of football
tactical styles.

The unit of observation is:

`one team in one season`

The main modeling goal is to identify whether teams can be grouped by where and
how they create possession threat.

The project does not treat clusters as ground-truth tactical labels. Instead,
clusters are analytical hypotheses that must be interpreted through centroid
heatmaps, representative team-seasons, and football domain knowledge.

---

## Data Pipeline Overview

The project follows this pipeline:

1. Load local StatsBomb event data.
2. Train one global xT model using selected matches.
3. Calculate action-level xT values for successful passes and carries.
4. Aggregate action-level xT into team-season spatial matrices.
5. Normalize matrices to emphasize spatial style instead of total attacking
   volume.
6. Run unsupervised clustering experiments.
7. Compare cluster interpretability across feature representations.

A key principle is that the project uses one global xT model rather than
training separate xT models for each team-season. This keeps all team-season
matrices on a shared value scale.

---

## Why Use Numerical xT Matrices Instead of Heatmap Images?

The machine learning inputs are numerical matrices, not PNG heatmaps.

Rendered heatmap images are not ideal as model inputs because they can introduce
irrelevant noise from:

- colormaps
- image resolution
- axes and labels
- interpolation
- compression artifacts
- figure styling

The underlying numerical matrix is cleaner and more interpretable. Each feature
corresponds directly to a pitch zone.

Heatmaps are used only for visualization and interpretation.

---

## Core Feature Concept

Each team-season can be represented by a 16 x 12 pitch grid:

`16 length bins x 12 width bins = 192 zones`

The zone convention is:

`zone = y_bin * 16 + x_bin`

When visualized, a 192-dimensional vector is reshaped into:

`12 rows x 16 columns`

The main baseline feature is:

`team-season + start_zone -> sum positive_xT`

where:

`positive_xT = max(xT_value, 0)`

This focuses on positive threat creation and avoids having backward or
lower-threat actions cancel out positive actions.

---

## Experiment A: Raw xT Matrix Clustering

Notebook:

`07A_clustering_raw_xt_matrix.ipynb`

Input:

`outputs/team_season_features_raw_created_xt_distribution.csv`

Output folder:

`outputs/experiment_A_raw/`

### Purpose

Experiment A is the baseline clustering experiment.

It uses the raw 16 x 12 positive xT created distribution by start zone. Each
team-season is represented by 192 spatial features.

The main tactical question is:

`Do raw xT spatial distributions naturally separate team-seasons by where they create threat?`

### Strengths

- Highly interpretable.
- Each feature corresponds directly to one pitch zone.
- Preserves local spatial detail.
- Good baseline for all later experiments.

### Limitations

- Sensitive to single-season noise.
- Individual zones can be affected by sparse events.
- It captures where teams create xT, but not necessarily how they create it.

### Main Outputs

- `outputs/experiment_A_raw/clustered_team_seasons_raw.csv`
- `outputs/experiment_A_raw/cluster_summary_raw.csv`
- `outputs/experiment_A_raw/cluster_representatives_raw.csv`
- `outputs/experiment_A_raw/cluster_centroids_raw.csv`
- `outputs/experiment_A_raw/cluster_centroid_heatmaps_raw.png`
- `outputs/experiment_A_raw/experiment_summary_raw.csv`

### Key Interpretation Tool

The most important interpretation output is:

`cluster_centroid_heatmaps_raw.png`

This shows the average raw xT creation profile of each cluster.

---

## Experiment B: Smoothed xT Matrix Clustering

Notebook:

`07B_clustering_smoothed_xt_matrix.ipynb`

Input:

`outputs/team_season_features_smoothed_created_xt_distribution.csv`

Output folder:

`outputs/experiment_B_smoothed/`

### Purpose

Experiment B tests whether spatial smoothing improves clustering robustness.

It uses Gaussian-smoothed 16 x 12 positive xT created distributions. Each
team-season is still represented by 192 spatial features, but isolated
zone-level spikes are softened.

The main tactical question is:

`Does smoothing the team-season xT spatial distribution produce more stable and interpretable tactical clusters than the raw matrix?`

### Strengths

- Reduces single-zone noise.
- Better captures continuous spatial tendencies.
- Useful robustness check against Experiment A.

### Limitations

- Too much smoothing may blur real tactical differences.
- Still uses only one channel: created xT by start zone.
- Does not separate passing, carrying, and receiving patterns.

### Main Outputs

- `outputs/experiment_B_smoothed/clustered_team_seasons_smoothed.csv`
- `outputs/experiment_B_smoothed/cluster_summary_smoothed.csv`
- `outputs/experiment_B_smoothed/cluster_representatives_smoothed.csv`
- `outputs/experiment_B_smoothed/cluster_centroids_smoothed.csv`
- `outputs/experiment_B_smoothed/cluster_centroid_heatmaps_smoothed.png`
- `outputs/experiment_B_smoothed/experiment_summary_smoothed.csv`

### Optional Comparison With Experiment A

Experiment B can optionally read:

`outputs/experiment_A_raw/clustered_team_seasons_raw.csv`

and compare Experiment A and B using:

- Adjusted Rand Index
- Normalized Mutual Information
- cluster overlap tables

These comparisons help determine whether smoothing preserves or changes the main
clustering structure.

---

## Experiment C: Multi-channel xT Feature Clustering

Notebook:

`07C_clustering_multichannel_xt_features.ipynb`

Input:

`outputs/team_season_features_multichannel_xt_distribution.csv`

Output folder:

`outputs/experiment_C_multichannel/`

### Purpose

Experiment C tests whether richer tactical feature channels produce more
meaningful clusters.

Instead of using only created xT by start zone, it uses multiple spatial
channels when available:

- created positive xT by start zone
- received positive xT by end zone
- pass-created positive xT by start zone
- carry-created positive xT by start zone
- action count distribution by start zone

The main tactical question is:

`Does adding received xT, pass-created xT, carry-created xT, and action count distribution produce more meaningful team-season tactical clusters than a single xT created matrix?`

### Strengths

- Captures more tactical dimensions.
- Separates where threat is created from where threat is received.
- Separates pass-based and carry-based creation.
- Can reveal richer playing style differences.

### Limitations

- Higher-dimensional feature space.
- Requires stronger dimensionality reduction.
- More complex to interpret.
- May produce clusters that differ from A and B because it uses more
  information.

### Main Outputs

- `outputs/experiment_C_multichannel/clustered_team_seasons_multichannel.csv`
- `outputs/experiment_C_multichannel/cluster_summary_multichannel.csv`
- `outputs/experiment_C_multichannel/cluster_representatives_multichannel.csv`
- `outputs/experiment_C_multichannel/cluster_centroids_multichannel.csv`
- `outputs/experiment_C_multichannel/cluster_channel_summary_multichannel.csv`
- `outputs/experiment_C_multichannel/experiment_summary_multichannel.csv`

### Key Interpretation Outputs

Experiment C produces channel-specific centroid heatmaps, such as:

- `cluster_centroids_created_multichannel.png`
- `cluster_centroids_received_multichannel.png`
- `cluster_centroids_pass_created_multichannel.png`
- `cluster_centroids_carry_created_multichannel.png`
- `cluster_centroids_action_count_multichannel.png`

These heatmaps are essential for understanding what each cluster means.

---

## Shared Modeling Workflow

Each experiment follows the same general workflow:

1. Load processed team-season feature CSV.
2. Select feature columns.
3. Filter low-quality samples.
4. Standardize features with StandardScaler.
5. Reduce dimensionality with PCA.
6. Evaluate KMeans cluster numbers from k = 3 to k = 10.
7. Fit final KMeans model with default k = 5.
8. Save cluster labels.
9. Generate cluster summaries.
10. Generate centroid heatmaps.
11. Find representative team-seasons.
12. Save experiment summary.

---

## Why PCA Is Used

The xT feature space is high-dimensional:

- Experiment A: 192 features
- Experiment B: 192 features
- Experiment C: potentially 960 features if all five channels are available

PCA reduces these features into lower-dimensional spatial patterns before
clustering.

PCA also helps reduce noise and makes KMeans more stable.

---

## Why KMeans Is Used

KMeans is used as the baseline clustering algorithm because:

- It is simple.
- It is interpretable.
- It works well with PCA-reduced numerical features.
- Cluster centroids can be reshaped into pitch heatmaps.

However, KMeans assumes relatively compact clusters. Future work may compare it
with:

- Gaussian Mixture Models
- Agglomerative Clustering
- HDBSCAN
- UMAP + clustering

---

## Cluster Interpretation Rules

Clusters should not be treated as ground-truth tactical labels.

The project should avoid strong labels such as:

- counterattack
- high press
- long ball
- low block

unless the features directly support those claims.

xT spatial features mainly describe possession threat creation. They do not
directly measure:

- pressing
- defensive intensity
- defensive block height
- transition defense
- counterpressing

Safer cluster descriptions include:

- high attacking-third xT concentration
- wide-side xT creation profile
- central xT creation profile
- deep-origin xT creation profile
- pass-dominant creation profile
- carry-dominant creation profile
- balanced spatial distribution

---

## How to Compare Experiments A, B, and C

The three experiments should be compared using both statistical metrics and
football interpretation.

### Statistical Comparison

Use:

- silhouette score
- Calinski-Harabasz score
- Davies-Bouldin score
- Adjusted Rand Index between experiments
- Normalized Mutual Information between experiments

### Interpretability Comparison

Check:

- Are centroid heatmaps clear?
- Are representative team-seasons coherent?
- Do clusters correspond to recognizable spatial patterns?
- Are clusters dominated by league, season, or team strength?
- Does the feature representation capture tactical differences rather than only
  attacking volume?

---

## Recommended Interpretation Order

1. Start with Experiment A.
   - Understand the raw spatial xT baseline.
2. Compare Experiment B with Experiment A.
   - Check whether smoothing reduces noise or changes the cluster structure.
3. Compare Experiment C with A and B.
   - Check whether richer multi-channel features produce more meaningful
     tactical distinctions.
4. Use centroid heatmaps and representative team-seasons to manually assign
   tentative descriptions.

---

## Main Output Files

### Experiment A

`outputs/experiment_A_raw/clustered_team_seasons_raw.csv`

This gives the cluster label for each team-season using raw xT matrix features.

### Experiment B

`outputs/experiment_B_smoothed/clustered_team_seasons_smoothed.csv`

This gives the cluster label for each team-season using smoothed xT matrix
features.

### Experiment C

`outputs/experiment_C_multichannel/clustered_team_seasons_multichannel.csv`

This gives the cluster label for each team-season using multi-channel xT
features.

---

## Suggested Next Step

After running all three experiments, create a comparison notebook:

`08_compare_clustering_experiments.ipynb`

This notebook should compare:

- experiment summary metrics
- ARI / NMI across experiments
- cluster representative teams
- centroid heatmaps
- whether A, B, and C tell a consistent tactical story

---

## Summary

Experiment A answers:

`What clusters emerge from raw xT creation locations?`

Experiment B answers:

`Are those clusters robust after spatial smoothing?`

Experiment C answers:

`Do richer xT channels reveal more meaningful tactical differences?`

Together, these experiments create a structured workflow for turning event-level
football data into interpretable team-season tactical clusters.
