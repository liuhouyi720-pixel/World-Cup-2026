import json
from dataclasses import asdict

def report_markdown(p,actual=None):
    actual_line="Actual result hidden at prediction time." if actual is None else f"Actual result: {actual['home_team']} {actual['home_score']}–{actual['away_score']} {actual['away_team']}."
    weights=", ".join(f"{k} {v:.0%}" for k,v in p.final_weights.items())
    return f"""# {p.team_a} vs {p.team_b}\n\n## Prediction\n\nThe model slightly favors **{p.predicted_winner}**, although the probabilities remain close.\n\n## Probability summary\n\n{p.team_a} win {p.team_a_win_90:.1%}; draw {p.draw_90:.1%}; {p.team_b} win {p.team_b_win_90:.1%}.\n\n{actual_line}\n\n## Why\n\nFinal weights for the available components were: {weights}. Missing components are removed and the remaining weights are renormalized.\n\n## xT explained for beginners\n\nxT estimates how much a pass or carry moves a team closer to scoring. The heatmap is not a player movement map; it shows the relative distribution of attacking threat in historical samples.\n\n## Most likely scorelines\n\n{', '.join(f"{x['score']} ({x['probability']:.1%})" for x in p.top_scorelines)}\n\n## Data confidence: {p.confidence}\n\n"""+"\n".join(f"- {x}" for x in p.limitations)+"\n\n> This tool is a football analytics demonstration and is not betting advice.\n"

def save_report(p,path,actual=None):
    path.mkdir(parents=True,exist_ok=True); md=report_markdown(p,actual); (path/f"{p.match_id}.md").write_text(md,encoding="utf-8"); payload=asdict(p); payload["markdown"]=md; (path/f"{p.match_id}.json").write_text(json.dumps(payload,ensure_ascii=False,indent=2),encoding="utf-8")
