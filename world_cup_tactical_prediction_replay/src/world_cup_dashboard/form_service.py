EMPTY = {"played":0,"wins":0,"draws":0,"losses":0,"goals_for":0,"goals_against":0,"goal_difference":0,"points_per_match":None,"clean_sheets":0,"sequence":"—"}

class FormService:
    def __init__(self): self.history = []
    def snapshot(self, team):
        rows = [r for r in self.history if team in (r["home_team"],r["away_team"])]
        if not rows: return dict(EMPTY)
        out = dict(EMPTY); out["played"] = len(rows); pts = 0; seq = []
        for r in rows[-5:]:
            home = r["home_team"] == team; gf = r["home_score"] if home else r["away_score"]; ga = r["away_score"] if home else r["home_score"]
            out["goals_for"] += gf; out["goals_against"] += ga; out["clean_sheets"] += ga == 0
            key = "wins" if gf > ga else "draws" if gf == ga else "losses"; out[key] += 1; result = key[0].upper(); seq.append(result); pts += 3 if key=="wins" else 1 if key=="draws" else 0
        out["goal_difference"] = out["goals_for"]-out["goals_against"]; out["points_per_match"] = pts/len(rows); out["sequence"] = "-".join(seq); return out
    def advantage(self,a,b):
        x,y=self.snapshot(a),self.snapshot(b)
        if not x["played"] and not y["played"]: return None
        px=x["points_per_match"] if x["points_per_match"] is not None else 1.; py=y["points_per_match"] if y["points_per_match"] is not None else 1.
        return max(-.15,min(.15,(px-py)*.08+(x["goal_difference"]-y["goal_difference"])*.015))
    def update(self,match): self.history.append({k:match[k] for k in ("home_team","away_team","home_score","away_score")})

