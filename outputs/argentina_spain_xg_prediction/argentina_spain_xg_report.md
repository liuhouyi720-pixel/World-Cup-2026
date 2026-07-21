# Argentina vs Spain xG Prediction

Match date: 2026-07-19

This notebook trains a local custom xG model from raw StatsBomb shot events and compares it with the StatsBomb-provided `shot.statsbomb_xg` benchmark. It uses local JSON only and does not use current 2026 event data, odds, media commentary, or confirmed lineups.

## Earlier-prediction validation

User-provided note: the two earlier predictions were correct; Spain beat France 2-0, and the earlier Argentina-England call was also correct.

I do not add either earlier result as a training label. Instead, the notebook retains the feature diagnostics from the prior custom xG experiments by explicitly tracking features that helped explain shot quality: angle to goal, defensive pressure/freezeframe spacing, goalkeeper distance, shot location, body part, open goal, and play pattern.

## Custom xG headline prediction

- Argentina projected xG: 1.073
- Spain projected xG: 0.951
- Argentina win in 90 minutes: 37.9%
- Draw after 90 minutes: 30.5%
- Spain win in 90 minutes: 31.6%
- Most likely scoreline: 1-0

## StatsBomb xG benchmark

- Argentina projected xG: 1.214
- Spain projected xG: 0.963
- Argentina win in 90 minutes: 41.8%
- Draw after 90 minutes: 29.0%
- Spain win in 90 minutes: 29.2%
- Most likely scoreline: 1-0

## Model caveat

StatsBomb xG is the vendor-provided supervised xG benchmark. The custom model is educational: it is trained on available open-data shots and evaluated with a grouped match split so shots from the same match do not appear in both train and test.
