# Argentina vs England xT/KMeans Prediction

Match date: 2026-07-15

This notebook is a companion to the Spain-France tactical prediction notebook. It uses local xT/KMeans team-season outputs and local formation summaries only. It does not use current 2026 event data, lineups, odds, or media commentary.

## Spain-France feedback

User-provided note: the previous Spain-France prediction was directionally right, with Spain beating France 2-0.

I treat that as a light model-calibration lesson rather than a new supervised label. The reinforced version gives a little more weight to the two factors that were most useful in the previous explanation: aggregate xT/team-strength and formation matchup. The xT zones highlighted last time (`received_z095`, `created_z045`, `created_z030`) are kept as diagnostics.

## Main reinforced prediction

- Argentina win in 90 minutes: 32.2%
- Draw after 90 minutes: 28.2%
- England win in 90 minutes: 39.6%
- Most likely 90-minute result bucket: England win

## Data notes

Argentina selected row: Copa America 2024 with 6 matches.
England selected row: UEFA Euro 2024 with 7 matches.

Because this is a cross-confederation match, the local proxy data naturally compares Argentina's latest available senior men's tournament row against England's latest available senior men's tournament row. This is useful for an educational experiment, but it is not betting-grade.
