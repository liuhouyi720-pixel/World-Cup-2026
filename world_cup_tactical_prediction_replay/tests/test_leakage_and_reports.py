from src.world_cup_dashboard.batch_predict import engine
from src.world_cup_dashboard.form_service import FormService
from src.world_cup_dashboard.report_generator import report_markdown

def test_prediction_does_not_mutate_form():
    f=FormService();p=engine().predict({"match_id":"x","kickoff":"2026-06-11","stage":"Group","group":"A","home_team":"Spain","away_team":"France"},f);assert len(f.history)==0;assert abs(p.team_a_win_90+p.draw_90+p.team_b_win_90-1)<1e-12
def test_knockout_advance_sums_to_one():
    p=engine().predict({"match_id":"x","kickoff":"2026-07-01","stage":"Round of 32","group":"","home_team":"Spain","away_team":"France"},FormService());assert abs(p.team_a_advance+p.team_b_advance-1)<1e-12
def test_report_complete_and_grounded():
    p=engine().predict({"match_id":"x","kickoff":"2026-07-01","stage":"Final","group":"","home_team":"Spain","away_team":"France"},FormService());md=report_markdown(p);assert "xT" in md and "Data confidence" in md and "injury" not in md.lower()
