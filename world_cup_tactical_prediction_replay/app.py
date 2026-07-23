from __future__ import annotations

import ast
import json

import pandas as pd
import streamlit as st

from src.world_cup_dashboard.config import EVALUATION, REPORTS, SIMULATION
from src.world_cup_dashboard.data_loader import load_matches, load_predictions
from src.world_cup_dashboard.tactical_service import TacticalService
from src.world_cup_dashboard.visualization import difference_heatmap, xt_heatmap
from src.world_cup_dashboard.xt_style_service import XTStyleService

st.set_page_config(page_title="2026 World Cup Tactical Prediction Replay", page_icon="⚽", layout="wide")
st.markdown(
    """<style>
    .stApp{background:#07131f;color:#eef6ff}.block-container{padding-top:1.2rem}
    .hero{padding:1.4rem;border:1px solid #27445b;border-radius:18px;background:linear-gradient(135deg,#102b3d,#0b1d2b)}
    .tag{color:#54e3a6;font-weight:700}.muted{color:#9cb1c3}
    </style>""",
    unsafe_allow_html=True,
)

@st.cache_data
def load_dashboard_data():
    return load_matches(), load_predictions()

@st.cache_resource
def services():
    return XTStyleService(), TacticalService()

matches, predictions = load_dashboard_data()
xt, tactical = services()
if predictions.empty:
    st.error("Predictions have not been generated. Run `python -m src.world_cup_dashboard.batch_predict --mode backtest`.")
    st.stop()

PAGES = [
    "Tournament Overview", "Prediction Replay", "Match Report", "Team Comparison",
    "Tournament Simulator", "Model Evaluation", "Methodology & Limitations",
]

st.sidebar.markdown("## ⚽ 2026 Tactical Replay")
page = st.sidebar.radio("Page", PAGES)
st.sidebar.caption(
    "Historical Replay uses real matchups for backtesting. Tournament Simulator creates its own qualifiers and knockout path."
)

def pct(value):
    return f"{float(value):.1%}"

def actual_result(row):
    return f"{int(row.actual_home_score)}–{int(row.actual_away_score)}"

def metric_json():
    path = EVALUATION / "metrics.json"
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}

def simulation_json():
    path = SIMULATION / "full_tournament_simulation.json"
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}

def overview():
    metrics, simulation = metric_json(), simulation_json()
    st.markdown(
        '<div class="hero"><span class="tag">HISTORICAL REPLAY · OFFLINE</span>'
        '<h1>2026 World Cup Tactical Prediction Replay</h1>'
        '<p class="muted">xT spatial style × formation matchup × strength prior × strictly chronological tournament form</p></div>',
        unsafe_allow_html=True,
    )
    champion, simulated, count, accuracy = st.columns(4)
    champion.metric("Actual champion", "Spain")
    simulated.metric("Simulated champion", simulation.get("champion", "Not generated"))
    count.metric("Matches replayed", metrics.get("matches", len(predictions)))
    accuracy.metric("Three-class accuracy", pct(metrics.get("three_class_accuracy", 0)))
    st.subheader("Groups")
    columns = st.columns(4)
    for index, (group, rows) in enumerate(matches[matches.stage.eq("Group")].groupby("group")):
        with columns[index % 4]:
            st.markdown(f"**Group {group}**  \n" + " · ".join(sorted(set(rows.home_team) | set(rows.away_team))))
    st.subheader("Most confident predictions")
    display = predictions.copy()
    display["max_probability"] = display[["team_a_win_90", "draw_90", "team_b_win_90"]].max(axis=1)
    display = display.sort_values("max_probability", ascending=False).head(8)[
        ["team_a", "team_b", "stage", "max_probability", "correct_prediction"]
    ]
    st.dataframe(
        display,
        column_config={
            "max_probability": st.column_config.ProgressColumn("Highest probability", format="percent", min_value=0, max_value=1),
            "correct_prediction": "Correct",
        },
        width="stretch",
        hide_index=True,
    )

def replay():
    st.title("Prediction Replay")
    st.caption("Each prediction was generated before kickoff. Actual results were revealed only afterward for evaluation and subsequent form updates.")
    stage_column, team_column, result_column = st.columns(3)
    selected_stages = stage_column.multiselect("Stage", sorted(predictions.stage.unique()))
    selected_team = team_column.selectbox("Team", ["All teams"] + sorted(set(predictions.team_a) | set(predictions.team_b)))
    correctness = result_column.selectbox("Prediction result", ["All", "Correct", "Incorrect"])
    filtered = predictions.copy()
    if selected_stages:
        filtered = filtered[filtered.stage.isin(selected_stages)]
    if selected_team != "All teams":
        filtered = filtered[(filtered.team_a == selected_team) | (filtered.team_b == selected_team)]
    if correctness != "All":
        filtered = filtered[filtered.correct_prediction.astype(str).str.lower().eq("true" if correctness == "Correct" else "false")]
    hide_results = st.toggle("Hide actual result until reveal", value=True)
    for row in filtered.head(40).itertuples():
        with st.container(border=True):
            title, probability, outcome = st.columns([2, 3, 2])
            title.markdown(f"**{row.team_a} vs {row.team_b}**  \n{row.stage}")
            probability.progress(
                float(row.team_a_win_90),
                text=f"{row.team_a} {pct(row.team_a_win_90)} · Draw {pct(row.draw_90)} · {row.team_b} {pct(row.team_b_win_90)}",
            )
            outcome.markdown(
                "Actual result hidden" if hide_results else f"Actual score **{actual_result(row)}**  \nPrediction {'correct' if str(row.correct_prediction).lower() == 'true' else 'incorrect'}"
            )

def selected_prediction():
    labels = {f"{row.team_a} vs {row.team_b} · {row.stage} · {row.match_id}": row.match_id for row in predictions.itertuples()}
    label = st.selectbox("Select match", list(labels))
    return predictions[predictions.match_id.eq(labels[label])].iloc[0]

def report():
    st.title("Match Report")
    row = selected_prediction()
    mode = st.radio("Display mode", ["Beginner", "Expert"], horizontal=True)
    st.header(f"{row.team_a} vs {row.team_b}")
    team_a, draw, team_b, score = st.columns(4)
    team_a.metric(f"{row.team_a} 90-minute win", pct(row.team_a_win_90))
    draw.metric("Draw", pct(row.draw_90))
    team_b.metric(f"{row.team_b} 90-minute win", pct(row.team_b_win_90))
    score.metric("Predicted score", f"{int(row.predicted_score_a)}–{int(row.predicted_score_b)}")
    report_path = REPORTS / f"{row.match_id}.md"
    markdown = report_path.read_text(encoding="utf-8") if report_path.exists() else "Report file is missing."
    st.markdown(markdown)
    if mode == "Expert":
        st.subheader("Model components and renormalized weights")
        for column in ("components", "final_weights", "availability"):
            if column in row and isinstance(row[column], str):
                try:
                    st.json(ast.literal_eval(row[column]))
                except (SyntaxError, ValueError):
                    st.code(row[column])
        profile_a, profile_b = xt.profile(row.team_a), xt.profile(row.team_b)
        column_a, column_b = st.columns(2)
        with column_a:
            figure = xt_heatmap(profile_a)
            st.pyplot(figure) if figure else st.info(f"No compatible xT profile for {row.team_a}.")
        with column_b:
            figure = xt_heatmap(profile_b)
            st.pyplot(figure) if figure else st.info(f"No compatible xT profile for {row.team_b}.")
        figure = difference_heatmap(profile_a, profile_b)
        if figure:
            st.pyplot(figure)
        st.caption("The original 12×16 experiment grid is used without rotation or transposition. Reconfirm orientation if the notebook coordinate convention changes.")
    st.download_button("Download Markdown report", markdown, file_name=f"{row.match_id}.md")

def comparison():
    st.title("Team Style Comparison")
    teams = sorted(set(matches.home_team) | set(matches.away_team))
    column_a, column_b = st.columns(2)
    team_a = column_a.selectbox("Team A", teams, index=teams.index("Spain") if "Spain" in teams else 0)
    team_b = column_b.selectbox("Team B", teams, index=teams.index("Argentina") if "Argentina" in teams else 1)
    profile_a, profile_b = xt.profile(team_a), xt.profile(team_b)
    for column, profile in zip(st.columns(2), (profile_a, profile_b)):
        with column:
            st.subheader(profile.team)
            if profile.data_available:
                st.write(f"Experiment {profile.experiment} · {profile.source_competition} {profile.source_season} · Cluster {profile.cluster_id}")
                st.info(profile.cluster_label)
                st.pyplot(xt_heatmap(profile))
                st.dataframe(pd.DataFrame([profile.spatial]).T.rename(columns={0: "Share"}), width="stretch")
            else:
                st.warning("No historical xT profile is available; no synthetic heatmap is shown.")
    similarity = xt.similarity(team_a, team_b)
    st.metric("xT spatial cosine similarity", f"{similarity:.3f}" if similarity is not None else "Unavailable")
    export = pd.DataFrame([
        {"team": profile.team, "experiment": profile.experiment, "competition": profile.source_competition, "season": profile.source_season, "cluster": profile.cluster_id, "description": profile.cluster_label}
        for profile in (profile_a, profile_b)
    ]).to_csv(index=False).encode("utf-8-sig")
    st.download_button("Download comparison CSV", export, "team_comparison.csv")

def simulator():
    st.title("World Cup Tournament Simulator")
    st.warning("This mode creates qualifiers from model-predicted group tables. It does not use the actual knockout participants.")
    simulation = simulation_json()
    if not simulation:
        st.info("Run `python -m src.world_cup_dashboard.batch_predict --mode full_simulation` first.")
        return
    st.metric("Deterministic simulated champion", simulation["champion"])
    st.caption(simulation.get("bracket_note", ""))
    tabs = st.tabs([f"Group {group}" for group in simulation["group_tables"]])
    for tab, (_, rows) in zip(tabs, simulation["group_tables"].items()):
        with tab:
            st.dataframe(pd.DataFrame(rows), width="stretch", hide_index=True)
    st.subheader("Best third-place teams")
    st.dataframe(pd.DataFrame(simulation["best_third_place"]), width="stretch", hide_index=True)
    st.download_button("Download simulation JSON", json.dumps(simulation, ensure_ascii=False, indent=2), "full_tournament_simulation.json")

def evaluation():
    st.title("Model Evaluation")
    metrics = metric_json()
    accuracy, winner, log_loss, brier = st.columns(4)
    accuracy.metric("Three-class accuracy", pct(metrics.get("three_class_accuracy", 0)))
    winner.metric("Non-draw winner accuracy", pct(metrics.get("winner_accuracy", 0)))
    log_loss.metric("Log loss", f"{metrics.get('log_loss', 0):.3f}")
    brier.metric("Brier score", f"{metrics.get('brier_score', 0):.3f}")
    evaluation_data = predictions.copy()
    evaluation_data["correct"] = evaluation_data.correct_prediction.astype(str).str.lower().eq("true")
    st.subheader("Accuracy by stage")
    st.bar_chart(evaluation_data.groupby("stage").correct.mean())
    calibration = EVALUATION / "calibration.csv"
    if calibration.exists():
        calibration_data = pd.read_csv(calibration)
        st.subheader("Calibration")
        st.line_chart(calibration_data.set_index("predicted_probability")["observed_accuracy"])
        st.dataframe(calibration_data, width="stretch", hide_index=True)
    st.subheader("Confusion matrix")
    actual = evaluation_data.apply(lambda item: "Home win" if item.actual_home_score > item.actual_away_score else "Away win" if item.actual_home_score < item.actual_away_score else "Draw", axis=1)
    predicted = evaluation_data[["team_a_win_90", "draw_90", "team_b_win_90"]].idxmax(axis=1).map({"team_a_win_90": "Home win", "draw_90": "Draw", "team_b_win_90": "Away win"})
    st.dataframe(pd.crosstab(actual, predicted, rownames=["Actual"], colnames=["Predicted"]), width="stretch")
    st.download_button("Download evaluation CSV", evaluation_data.to_csv(index=False).encode("utf-8-sig"), "evaluation_predictions.csv")

def methodology():
    st.title("Methodology & Limitations")
    st.markdown("""### For beginners

**xT** estimates how much a pass or carry moves a team closer to scoring. **Clustering** groups similar historical threat distributions; it is not a ranking of team quality. Formation statistics are historical test scenarios, not confirmed lineups.

**Historical backtesting** freezes information before kickoff, creates a prediction, reveals the result, and only then updates later tournament form. This prevents future-data leakage.

### Technical structure

`xT style + formation matchup + strength proxy + pre-kickoff tournament form → interpretable probabilities`.
The demonstration weights are 45% / 20% / 20% / 15%. Missing components are removed and the remaining weights are renormalized. A bounded advantage score produces 1X2 probabilities; an independent Poisson approximation produces illustrative scorelines.

### Known limitations

- No complete 2026 event-level StatsBomb data is available locally; xT uses historical national-team proxy profiles.
- Coaches, players, injuries, lineups, pressing, defensive structure, and set pieces are not fully modeled.
- Formation-matchup samples can be small. When no suitable sample exists, the system does not invent one.
- The integration weights are transparent demonstration choices, not statistically optimized estimates.
- The full simulation uses fixed seed order for its model knockout bracket to guarantee that participants are model-generated.
- This project is an analysis demonstration, not betting advice.
""")

{
    "Tournament Overview": overview,
    "Prediction Replay": replay,
    "Match Report": report,
    "Team Comparison": comparison,
    "Tournament Simulator": simulator,
    "Model Evaluation": evaluation,
    "Methodology & Limitations": methodology,
}[page]()

