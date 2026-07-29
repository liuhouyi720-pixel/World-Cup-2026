# Argentina vs Spain xT/KMeans Prediction

Match date: 2026-07-19

This notebook is a companion to the earlier tactical prediction notebooks. It uses local xT/KMeans team-season outputs and local formation summaries only. It does not use current 2026 event data, lineups, odds, or media commentary.

## Earlier-prediction validation

User-provided note: the two earlier predictions were correct; Spain beat France 2-0, and the earlier Argentina-England call was also correct.

I treat that as a light model-calibration lesson rather than a new supervised label. The reinforced version gives a little more weight to the two factors that were most useful in the previous explanation: aggregate xT/team-strength and formation matchup. The xT zones highlighted last time (`received_z095`, `created_z045`, `created_z030`) are kept as diagnostics.

## Main reinforced prediction

- Argentina win in 90 minutes: 21.8%
- Draw after 90 minutes: 25.9%
- Spain win in 90 minutes: 52.3%
- Most likely 90-minute result bucket: Spain win

## Data notes

Argentina selected row: Copa America 2024 with 6 matches.
Spain selected row: UEFA Euro 2024 with 7 matches.

Because this is a cross-confederation match, the local proxy data naturally compares Argentina's latest available senior men's tournament row against Spain's latest available senior men's tournament row. This is useful for an educational experiment, but it is not betting-grade.
