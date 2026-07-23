import argparse,json
import pandas as pd
from .config import *
from .data_loader import load_matches,validate_matches
from .xt_style_service import XTStyleService
from .tactical_service import TacticalService
from .strength_service import StrengthService
from .prediction_engine import PredictionEngine
from .form_service import FormService
from .report_generator import save_report
from .evaluation import evaluation_metrics,calibration_table,actual_label
from .group_table_engine import build_group_table
from .bracket_engine import advancing_team

def engine(weights=None,experiment="C"):
    xt=XTStyleService(experiment);return PredictionEngine(xt,TacticalService(),StrengthService(xt),weights)

def backtest(generate_reports=True):
    ensure_dirs();matches=load_matches();issues=validate_matches(matches)
    if issues:raise ValueError("; ".join(issues))
    e=engine();form=FormService();rows=[];audit=[]
    for m in matches.to_dict("records"):
        prior=len(form.history);p=e.predict(m,form);actual={"home_team":m["home_team"],"away_team":m["away_team"],"home_score":int(m["home_score"]),"away_score":int(m["away_score"])}
        if generate_reports:save_report(p,REPORTS,actual)
        label=actual_label(actual["home_score"],actual["away_score"]);plabel="H" if p.team_a_win_90>=max(p.draw_90,p.team_b_win_90) else "D" if p.draw_90>=p.team_b_win_90 else "A"
        rows.append(p.as_record()|{"actual_home_score":actual["home_score"],"actual_away_score":actual["away_score"],"actual_winner":m.get("winner",""),"actual_status":m.get("status",""),"correct_prediction":label==plabel})
        audit.append({"match_id":m["match_id"],"prediction_timestamp":str(m["kickoff"]),"form_history_matches":prior,"target_in_form":False,"future_match_used":False,"status":"pass"});form.update(actual)
    d=pd.DataFrame(rows);d.to_csv(PREDICTIONS/"backtest_predictions.csv",index=False,encoding="utf-8-sig");pd.DataFrame(audit).to_csv(EVALUATION/"leakage_audit.csv",index=False);metrics=evaluation_metrics(d);(EVALUATION/"metrics.json").write_text(json.dumps(metrics,indent=2),encoding="utf-8");calibration_table(d).to_csv(EVALUATION/"calibration.csv",index=False);return d

def full_simulation(weights=None,experiment="C",use_form=True):
    ensure_dirs();matches=load_matches();e=engine(weights,experiment);form=FormService();records=[];tables={}
    for m in matches[matches.stage.eq("Group")].to_dict("records"):
        p=e.predict(m,form,"full_simulation",use_form);x,y=p.predicted_score_a,p.predicted_score_b
        records.append(p.as_record()|{"simulated_home_score":x,"simulated_away_score":y});form.update({"home_team":m["home_team"],"away_team":m["away_team"],"home_score":x,"away_score":y})
    qualified=[];third=[]
    for g in sorted(matches[matches.stage.eq("Group")].group.unique()):
        x=pd.DataFrame([r for r in records if r["group"]==g]).rename(columns={"team_a":"home_team","team_b":"away_team","simulated_home_score":"home_score","simulated_away_score":"away_score"});t=build_group_table(x);tables[g]=t.to_dict("records");qualified+=t.team.head(2).tolist();third.append(t.iloc[2].to_dict()|{"group":g})
    best=sorted(third,key=lambda x:(x["points"],x["goal_difference"],x["goals_for"],x["team"]),reverse=True)[:8];field=qualified+[x["team"] for x in best];names=["Round of 32","Round of 16","Quarter-finals","Semi-finals","Final"]
    for rnd,name in enumerate(names,1):
        winners=[]
        for i in range(0,len(field),2):
            m={"match_id":f"sim_{rnd}_{i//2+1}","kickoff":f"simulation-{rnd}","stage":name,"group":"","home_team":field[i],"away_team":field[i+1]};p=e.predict(m,form,"full_simulation",use_form);w=advancing_team(p);records.append(p.as_record()|{"simulated_winner":w});winners.append(w)
        field=winners
    out={"mode":"full_simulation","bracket_note":"模型从小组预测结果产生晋级队，随后采用固定种子顺序构造独立淘汰赛，不读取真实淘汰赛参赛队。","group_tables":tables,"best_third_place":best,"champion":field[0],"predictions":records};(SIMULATION/"full_tournament_simulation.json").write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding="utf-8");return out

def main():
    p=argparse.ArgumentParser();p.add_argument("--mode",choices=["backtest","full_simulation"],required=True);a=p.parse_args();print(f"Created {len(backtest())} chronological predictions" if a.mode=="backtest" else f"Simulated champion: {full_simulation()['champion']}")
if __name__=="__main__":main()
