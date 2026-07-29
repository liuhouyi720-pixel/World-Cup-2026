# Argentina vs England xG Prediction

Match date: 2026-07-15

This notebook trains a local custom xG model from raw StatsBomb shot events and compares it with the StatsBomb-provided `shot.statsbomb_xg` benchmark. It uses local JSON only and does not use current 2026 event data, odds, media commentary, or confirmed lineups.

## Spain-France feedback

User-provided note: the previous Spain-France prediction was directionally right, with Spain beating France 2-0.

I do not add that single match as a training label. Instead, the notebook reinforces the lesson from the prior custom xG experiment by explicitly tracking features that helped explain shot quality: angle to goal, defensive pressure/freezeframe spacing, goalkeeper distance, shot location, body part, open goal, and play pattern.

## Custom xG headline prediction

- Argentina projected xG: 1.182
- England projected xG: 0.712
- Argentina win in 90 minutes: 47.1%
- Draw after 90 minutes: 30.6%
- England win in 90 minutes: 22.2%
- Most likely scoreline: 1-0

## StatsBomb xG benchmark

- Argentina projected xG: 1.238
- England projected xG: 0.822
- Argentina win in 90 minutes: 46.0%
- Draw after 90 minutes: 29.4%
- England win in 90 minutes: 24.6%
- Most likely scoreline: 1-0

## Model caveat

StatsBomb xG is the vendor-provided supervised xG benchmark. The custom model is educational: it is trained on available open-data shots and evaluated with a grouped match split so shots from the same match do not appear in both train and test.
