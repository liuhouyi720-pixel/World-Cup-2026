# Spain vs France Prediction Interpretation

## 1. Data used

The selected Spain historical proxy sample is **UEFA Euro 2024**. The selected France historical proxy sample is **UEFA Euro 2024**.

The xT experiments successfully loaded were **A, B, C**. The primary xT experiment was **Experiment C**. The tactical statistics file used was **outputs\formation_matchup_summary.csv**. Strength priors used this source note: **Calculated from available historical proxy xT components; weights renormalized over available components.**.

## 2. xT style assignments

Spain's primary-experiment cluster is **4**. France's primary-experiment cluster is **4**.

Spain representative cluster teams: Arsenal (Premier League, 2015/2016); Real Madrid (La Liga, 2015/2016); Liverpool (Premier League, 2015/2016); Bayer Leverkusen (1. Bundesliga, 2023/2024); Tottenham Hotspur (Premier League, 2015/2016)

France representative cluster teams: Arsenal (Premier League, 2015/2016); Real Madrid (La Liga, 2015/2016); Liverpool (Premier League, 2015/2016); Bayer Leverkusen (1. Bundesliga, 2023/2024); Tottenham Hotspur (Premier League, 2015/2016)

Spain distance to centroid: 13.41146868199235. France distance to centroid: 19.110723062525658.

## 3. Spatial tactical comparison

Primary xT cosine similarity: **0.816**. Primary xT Euclidean distance: **0.126**.

Largest Spain-positive differences: received_z095 (0.0653), created_z045 (0.0268), created_z030 (0.0242)

Largest France-positive differences: created_z062 (-0.0474), received_z159 (-0.0258), received_z173 (-0.0201)

Only calculated differences from the selected historical proxy rows are described here. The heatmaps saved in the output directory should be used for spatial interpretation.

## 4. Tactical and formation matchup

The scenario source was **Local tactical model formation frequencies**. The baseline scenario used for the one-row final summary is **Spain 4-3-3 vs France 4-2-3-1**.

Among the tested historical scenarios, the highest model-estimated Spain advancement probability came from **Spain 4-3-3 vs France 4-2-3-1**. The highest model-estimated France advancement probability came from **Spain 4-2-3-1 vs France 4-3-3**.

Tactical sample-size limitations are reflected in the scenario confidence notes and the uncertainty table.

## 5. Prediction

The integrated demonstration model suggests:

- Spain 90-minute win probability: **37.1%**
- Draw after 90 minutes: **30.5%**
- France 90-minute win probability: **32.4%**
- Spain advancement probability: **53.7%**
- France advancement probability: **46.3%**
- Predicted advancing team: **Spain**

Based on the available historical proxy data, the model gives a slight advantage to **Spain**. This result is sensitive to the selected formations and fallback assumptions.

## 6. Limitations

No current World Cup event-level data was used. Historical team profiles may not represent the 2026 teams. xT clusters describe attacking threat distribution rather than complete tactics. Defensive pressing, injuries, lineups, player quality, goalkeeper performance, set pieces, and current form may be missing. Formation statistics may have small samples. The final integration weights are transparent demonstration choices rather than optimized parameters. These probabilities should not be used as betting advice.