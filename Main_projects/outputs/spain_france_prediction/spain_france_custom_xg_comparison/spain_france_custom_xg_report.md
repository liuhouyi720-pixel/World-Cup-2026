# Custom xG vs StatsBomb xG: Spain-France Comparison

## Data and model

This notebook trained a custom supervised xG model from local StatsBomb shot events in FIFA World Cup 2018/2022 and UEFA Euro 2020/2024. Period 5 shootout shots were excluded. The model used pre-shot features only: location, distance, angle, period, time, shot type, body part, technique, play pattern, boolean shot context flags, and freeze-frame counts.

StatsBomb's `shot.statsbomb_xg` was not used as a training feature. It was kept only as a benchmark.

## Test-set evaluation

- Custom model log loss: **0.250**
- StatsBomb xG log loss on the same test shots: **0.236**
- Custom model Brier score: **0.072**
- StatsBomb xG Brier score: **0.067**
- Custom model ROC AUC: **0.828**
- StatsBomb xG ROC AUC: **0.844**

## Spain-France projected xG

- StatsBomb xG projection: Spain **1.13**, France **1.10**
- Custom xG projection: Spain **1.10**, France **1.01**

## 90-minute outcome probabilities

StatsBomb xG workflow:

- Spain win: **36.3%**
- Draw: **28.9%**
- France win: **34.8%**
- Most likely scoreline: **1-1**

Custom xG workflow:

- Spain win: **37.5%**
- Draw: **29.8%**
- France win: **32.7%**
- Most likely scoreline: **1-1**

## Interpretation

The custom model lets us test whether a locally trained xG estimate changes the final match view. Differences should be interpreted cautiously because this training set is much smaller than a professional xG model's data and uses a compact feature set. The comparison is useful as a learning experiment, not as a betting-grade forecast.