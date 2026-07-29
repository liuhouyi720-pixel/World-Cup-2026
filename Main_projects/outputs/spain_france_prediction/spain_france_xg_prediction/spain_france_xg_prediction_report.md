# Spain vs France Pre-Match xG Prediction Report

## Data used

This experiment used local StatsBomb Open Data from `archive/data`, filtered to senior men's FIFA World Cup 2018 and 2022 plus UEFA Euro 2020 and 2024. The headline model used periods 1 and 2 only and excluded penalty shootouts by removing period 5.

Spain's recent sample covers **10** matches from **2022-11-27** to **2024-07-14**. France's recent sample covers **10** matches from **2022-12-04** to **2024-07-09**.

## How machine learning helped

StatsBomb's `shot.statsbomb_xg` field is the machine-learning component in this workflow. It estimates the probability that each shot becomes a goal based on shot context. This notebook aggregates those supervised shot-level values into team-match xG, then uses a transparent pre-match model and Poisson score conversion.

## Projected xG

- Spain projected xG: **1.13**
- France projected xG: **1.10**

## 90-minute outcome probabilities

- Spain win: **36.3%**
- Draw: **28.9%**
- France win: **34.8%**
- Most likely scoreline: **1-1** (13.4%)

## Interpretation

From a data-analysis point of view, the model estimates the match from historical shot quality rather than outside commentary on current form. The result is low-confidence because it uses historical proxy tournaments, not current 2026 World Cup event data or confirmed lineups.

## Limitations

This is not a betting-grade forecast. It assumes independent Poisson scoring, neutral venue, no current lineup information, no injuries, no tactical news, and no current tournament event data. Extra-time and advancement probabilities are intentionally left out of this xG-first experiment.