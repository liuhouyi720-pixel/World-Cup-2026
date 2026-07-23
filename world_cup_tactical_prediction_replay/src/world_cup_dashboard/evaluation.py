import numpy as np
import pandas as pd

def actual_label(a,b):return "H" if a>b else "A" if b>a else "D"
def evaluation_metrics(d):
    if d.empty:return {"matches":0}
    actual=[actual_label(int(r.actual_home_score),int(r.actual_away_score)) for r in d.itertuples()]; pred=d[["team_a_win_90","draw_90","team_b_win_90"]].idxmax(axis=1).map({"team_a_win_90":"H","draw_90":"D","team_b_win_90":"A"}).tolist(); probs=d[["team_a_win_90","draw_90","team_b_win_90"]].to_numpy(float); idx={"H":0,"D":1,"A":2}; y=np.array([idx[x] for x in actual]); one=np.zeros_like(probs);one[np.arange(len(y)),y]=1
    return {"matches":len(d),"three_class_accuracy":float(np.mean(np.array(actual)==np.array(pred))),"winner_accuracy":float(np.mean([x==y for x,y in zip(actual,pred) if x!="D"])),"log_loss":float(-np.log(np.clip(probs[np.arange(len(y)),y],1e-12,1)).mean()),"brier_score":float(((probs-one)**2).sum(axis=1).mean()),"knockout_matches":int((d.stage!="Group").sum())}

def calibration_table(d):
    rows=[]
    for r in d.itertuples():
        p=[r.team_a_win_90,r.draw_90,r.team_b_win_90]; y={"H":0,"D":1,"A":2}[actual_label(int(r.actual_home_score),int(r.actual_away_score))];rows.append((max(p),int(np.argmax(p)==y)))
    x=pd.DataFrame(rows,columns=["confidence","correct"]);x["bin"]=pd.cut(x.confidence,np.linspace(0,1,6),include_lowest=True);return x.groupby("bin",observed=True).agg(predicted_probability=("confidence","mean"),observed_accuracy=("correct","mean"),matches=("correct","size")).reset_index()

