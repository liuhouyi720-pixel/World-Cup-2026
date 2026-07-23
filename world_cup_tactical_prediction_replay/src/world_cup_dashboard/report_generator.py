import json
from dataclasses import asdict

def report_markdown(p,actual=None):
    actual_line="预测时隐藏真实结果。" if actual is None else f"真实结果：{actual['home_team']} {actual['home_score']}–{actual['away_score']} {actual['away_team']}。"
    weights="、".join(f"{k} {v:.0%}" for k,v in p.final_weights.items())
    return f"""# {p.team_a} vs {p.team_b}\n\n## 一句话预测\n\n模型略倾向于 **{p.predicted_winner}**，但双方概率差距有限。\n\n## 概率摘要\n\n{p.team_a} 胜 {p.team_a_win_90:.1%}；平局 {p.draw_90:.1%}；{p.team_b} 胜 {p.team_b_win_90:.1%}。\n\n{actual_line}\n\n## 为什么\n\n本场可用组件的最终权重为：{weights}。缺失组件会被移除并重新归一化。\n\n## xT 给新手的解释\n\nxT 表示一次传球或带球让球队更接近进球的程度。热图不是球员跑动热图，而是历史样本中不同区域制造进攻威胁的相对分布。\n\n## 最可能比分\n\n{', '.join(f"{x['score']} ({x['probability']:.1%})" for x in p.top_scorelines)}\n\n## 数据置信度：{p.confidence}\n\n"""+"\n".join(f"- {x}" for x in p.limitations)+"\n\n> 本工具用于足球分析演示，不适用于投注。\n"

def save_report(p,path,actual=None):
    path.mkdir(parents=True,exist_ok=True); md=report_markdown(p,actual); (path/f"{p.match_id}.md").write_text(md,encoding="utf-8"); payload=asdict(p); payload["markdown"]=md; (path/f"{p.match_id}.json").write_text(json.dumps(payload,ensure_ascii=False,indent=2),encoding="utf-8")

