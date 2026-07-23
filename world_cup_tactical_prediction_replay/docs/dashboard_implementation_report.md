# Implementation report

The new isolated folder contains a working Chinese-first Streamlit dashboard, reusable Python services, the offline 2026 cache, tests, documentation, launch scripts, and generated outputs. No original experiment was modified.

- Matches processed: 104 (72 group, 32 knockout)
- Reports generated: 104 Markdown and 104 JSON
- Primary xT experiment: C, with B/A fallbacks
- Tactical source: 105 matchup summaries and 8,470 team-match rows
- xT coverage: 20 of 48 teams; both-team xT matchup available in 24 of 104 matches
- Historical formation coverage: 36 of 48 teams; exact/reversed matchup available in 65 of 104 matches
- Recent tournament form available in 80 of 104 pre-match snapshots
- Backtest metrics: 44.23% three-class accuracy; 57.50% non-draw winner accuracy; log loss 1.0751; multiclass Brier 0.6510
- Simulated champion: Spain
- Leakage audit: 104 pass rows; no target or future match used
- Major assumption: transparent, manually selected integration weights
- Remaining limitations: historical proxies, incomplete national-team tactical coverage, unoptimized weights, and simplified modeled bracket routing

Reproduce with:

```powershell
python -m pip install -r requirements-dashboard.txt
python -m src.world_cup_dashboard.batch_predict --mode backtest
python -m src.world_cup_dashboard.batch_predict --mode full_simulation
python -m streamlit run app.py
```

The final product is an end-to-end football analytics demonstration combining xT spatial profiles, tactical statistics, transparent probability modeling, natural-language interpretation, and historical tournament backtesting.
