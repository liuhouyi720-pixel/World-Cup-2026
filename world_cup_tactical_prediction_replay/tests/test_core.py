import pandas as pd
from src.world_cup_dashboard.name_normalizer import normalize_team_name
from src.world_cup_dashboard.probability_utils import normalize_probabilities,outcome_probabilities
from src.world_cup_dashboard.form_service import FormService
from src.world_cup_dashboard.group_table_engine import build_group_table
from src.world_cup_dashboard.xt_style_service import XTStyleService
from src.world_cup_dashboard.report_generator import report_markdown
from src.world_cup_dashboard.tactical_service import normalize_formation

def test_name_normalization():
    assert normalize_team_name("USA") == "United States"
    assert normalize_team_name("Korea Republic") == "South Korea"
def test_probability_normalization():
    p=normalize_probabilities(.2,.3,.4);assert abs(sum(p)-1)<1e-12;assert all(0<=x<=1 for x in p)
    assert abs(sum(outcome_probabilities(.1))-1)<1e-12
def test_chronological_form_excludes_current_match():
    f=FormService();assert f.snapshot("Spain")["played"]==0
    f.update({"home_team":"Spain","away_team":"France","home_score":2,"away_score":0});assert f.snapshot("Spain")["played"]==1
def test_group_table_ranking():
    d=pd.DataFrame([{"home_team":"A","away_team":"B","home_score":2,"away_score":0},{"home_team":"A","away_team":"C","home_score":1,"away_score":1},{"home_team":"B","away_team":"C","home_score":0,"away_score":1}]);t=build_group_table(d);assert t.iloc[0].team=="A";assert t.iloc[-1].team=="B"
def test_missing_xt_profile():
    p=XTStyleService().profile("Imaginary Team");assert not p.data_available;assert p.vector is None
def test_formation_normalization():
    assert normalize_formation(433)=="4-3-3";assert normalize_formation("4231")=="4-2-3-1"

