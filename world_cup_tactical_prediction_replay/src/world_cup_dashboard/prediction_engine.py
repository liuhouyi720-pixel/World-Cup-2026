import numpy as np
from .config import DEFAULT_WEIGHTS
from .probability_utils import outcome_probabilities, scorelines
from .schemas import MatchPrediction

class PredictionEngine:
    def __init__(self,xt,tactical,strength,weights=None): self.xt=xt; self.tactical=tactical; self.strength=strength; self.weights=weights or dict(DEFAULT_WEIGHTS)
    def predict(self,m,form,mode="backtest",use_form=True):
        a,b=m["home_team"],m["away_team"]; sa,_=self.strength.score(a); sb,_=self.strength.score(b); pa,pb=self.xt.profile(a),self.xt.profile(b)
        fa,fb=self.tactical.common_formations(a),self.tactical.common_formations(b); tactical,sample,_=self.tactical.matchup(fa[0] if fa else None,fb[0] if fb else None)
        xt=None
        if pa.data_available and pb.data_available: xt=float(np.clip(((pa.spatial["attacking_third_share"]-pb.spatial["attacking_third_share"])+.35*(pa.spatial["center_share"]-pb.spatial["center_share"]))* .3,-.15,.15))
        recent=form.advantage(a,b) if use_form else None; c={"strength":float(np.clip(sa-sb,-.25,.25)),"xt_style":xt,"tactical_matchup":tactical,"recent_form":recent}
        active={k:self.weights[k] for k,v in c.items() if v is not None}; total=sum(active.values()); w={k:v/total for k,v in active.items()}; adv=sum(c[k]*w[k] for k in w)
        p1,pd,p2=outcome_probabilities(adv); knockout=m["stage"]!="Group"; tops=scorelines(adv); s=list(map(int,tops[0]["score"].split('-'))); winner=a if p1>=p2 else b
        available={k:v is not None for k,v in c.items()}; limits=["Historical proxy data, not 2026 event-level data."]
        if xt is None: limits.append("An xT profile is missing; its weight was removed and the remaining weights were renormalized.")
        if tactical is None: limits.append("Formation-matchup data is unavailable; its weight was removed and the remaining weights were renormalized.")
        if recent is None: limits.append("No pre-match tournament form was available yet.")
        if sample and sample<15: limits.append(f"Formation-matchup sample is small ({sample} matches).")
        conf="Low" if len(limits)>2 or abs(adv)<.04 else "Moderate"
        return MatchPrediction(str(m["match_id"]),str(m["kickoff"]),mode,m["stage"],m.get("group") or None,a,b,p1,pd,p2,p1+pd*.5 if knockout else None,p2+pd*.5 if knockout else None,s[0],s[1],winner,c,w,available,conf,limits,tops)
