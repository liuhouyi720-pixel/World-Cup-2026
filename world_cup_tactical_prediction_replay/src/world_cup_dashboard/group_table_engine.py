import pandas as pd

def build_group_table(matches):
    d={}
    for r in matches.to_dict("records"):
        for t in (r["home_team"],r["away_team"]): d.setdefault(t,{"team":t,"played":0,"wins":0,"draws":0,"losses":0,"goals_for":0,"goals_against":0,"goal_difference":0,"points":0})
        a,b=d[r["home_team"]],d[r["away_team"]]; x,y=int(r["home_score"]),int(r["away_score"])
        a["played"]+=1;b["played"]+=1;a["goals_for"]+=x;a["goals_against"]+=y;b["goals_for"]+=y;b["goals_against"]+=x
        if x>y:a["wins"]+=1;a["points"]+=3;b["losses"]+=1
        elif x<y:b["wins"]+=1;b["points"]+=3;a["losses"]+=1
        else:a["draws"]+=1;b["draws"]+=1;a["points"]+=1;b["points"]+=1
    out=pd.DataFrame(d.values())
    if out.empty:return out
    out["goal_difference"]=out.goals_for-out.goals_against
    return out.sort_values(["points","goal_difference","goals_for","team"],ascending=[False,False,False,True]).reset_index(drop=True)

