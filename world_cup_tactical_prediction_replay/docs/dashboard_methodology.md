# Methodology

For each historical match, the pipeline freezes all state at kickoff, computes four independent component scores, renormalizes weights over available components, saves the prediction, then reveals the result and updates form. This ordering is also asserted in the leakage audit.

The xT service selects the most recent compatible national-team sample from Experiment C, then B, then A. Clusters are never compared across experiments. Neutral Chinese descriptions are derived from attacking-third, side, and pass/carry shares and are labelled model-derived descriptions.

Formation notation is normalized (`433` → `4-3-3`). Tactical lookup uses exact then reversed matchup; otherwise the component is unavailable. The strength prior is deliberately weak and based on a historical attacking-third proxy when present, otherwise the global neutral mean. Form uses only previous tournament matches and caps its effect.

Available component scores are combined with demonstration weights 0.45 strength, 0.20 xT, 0.20 tactics, and 0.15 form. A bounded logistic mapping produces 90-minute home/draw/away probabilities; missing components are removed and weights sum to one. Knockout advancement divides draw probability equally. A small independent-Poisson model supplies illustrative scorelines.

Historical backtest uses actual participants but never future results. Full simulation predicts all group games, ranks tables by points, goal difference, goals for, then team name as a deterministic final fallback, selects 24 top-two teams and eight best thirds, and uses only those model qualifiers in its knockout bracket.

