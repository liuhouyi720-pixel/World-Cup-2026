from __future__ import annotations
import ast,json
from pathlib import Path
import pandas as pd
import streamlit as st

from src.world_cup_dashboard.config import EVALUATION, REPORTS, SIMULATION
from src.world_cup_dashboard.data_loader import load_matches,load_predictions
from src.world_cup_dashboard.xt_style_service import XTStyleService
from src.world_cup_dashboard.tactical_service import TacticalService
from src.world_cup_dashboard.visualization import xt_heatmap,difference_heatmap
from src.world_cup_dashboard.form_service import FormService

st.set_page_config(page_title="2026世界杯战术预测回放",page_icon="⚽",layout="wide")
st.markdown("""<style>.stApp{background:#07131f;color:#eef6ff}.block-container{padding-top:1.2rem}.hero{padding:1.4rem;border:1px solid #27445b;border-radius:18px;background:linear-gradient(135deg,#102b3d,#0b1d2b)}.tag{color:#54e3a6;font-weight:700}.muted{color:#9cb1c3}.card{padding:1rem;border:1px solid #29475e;border-radius:14px;background:#0d2231}</style>""",unsafe_allow_html=True)

@st.cache_data
def data(): return load_matches(),load_predictions()
@st.cache_resource
def services(): return XTStyleService(),TacticalService()

matches,predictions=data();xt,tactical=services()
if predictions.empty:
    st.error("尚未生成预测。请运行 `python -m src.world_cup_dashboard.batch_predict --mode backtest`。");st.stop()

st.sidebar.markdown("## ⚽ 2026 战术回放")
page=st.sidebar.radio("页面",["赛事总览","逐场预测回放","单场比赛报告","球队风格对比","世界杯重新模拟","模型表现评估","模型原理与局限"])
st.sidebar.caption("历史逐场回放 ≠ 从小组赛重新模拟。前者使用真实参赛对阵做回测；后者只使用模型上一轮产生的晋级队。")

def pct(v): return f"{float(v):.1%}"
def actual_result(row): return f"{int(row.actual_home_score)}–{int(row.actual_away_score)}"
def metric_json():
    p=EVALUATION/"metrics.json";return json.loads(p.read_text()) if p.exists() else {}
def simulation_json():
    p=SIMULATION/"full_tournament_simulation.json";return json.loads(p.read_text(encoding="utf-8")) if p.exists() else {}

def overview():
    metrics=metric_json();sim=simulation_json()
    st.markdown('<div class="hero"><span class="tag">HISTORICAL REPLAY · OFFLINE</span><h1>2026世界杯战术预测回放</h1><p class="muted">xT 空间风格 × 阵型对位 × 实力先验 × 严格按开球时间更新的赛事状态</p></div>',unsafe_allow_html=True)
    a,b,c,d=st.columns(4);a.metric("真实冠军","西班牙");b.metric("模型模拟冠军",sim.get("champion","尚未运行"));c.metric("已回放比赛",metrics.get("matches",len(predictions)));d.metric("三分类准确率",pct(metrics.get("three_class_accuracy",0)))
    st.subheader("12 个小组")
    cols=st.columns(4)
    group_matches=matches[matches.stage.eq("Group")]
    for i,(g,x) in enumerate(group_matches.groupby("group")):
        with cols[i%4]: st.markdown(f"**{g} 组**  \n"+" · ".join(sorted(set(x.home_team)|set(x.away_team))))
    st.subheader("最有把握的预测与最大失误")
    x=predictions.copy();x["max_probability"]=x[["team_a_win_90","draw_90","team_b_win_90"]].max(axis=1)
    display=x.sort_values("max_probability",ascending=False).head(8)[["team_a","team_b","stage","max_probability","correct_prediction"]]
    st.dataframe(display,column_config={"max_probability":st.column_config.ProgressColumn("最高概率",format="percent",min_value=0,max_value=1),"correct_prediction":"正确"},width="stretch",hide_index=True)

def replay():
    st.title("逐场预测回放");st.caption("每一行都在该场开球前生成；真实结果只在预测保存后用于评价和更新后续状态。")
    c1,c2,c3=st.columns(3);stage=c1.multiselect("阶段",sorted(predictions.stage.unique()),default=[]);team=c2.selectbox("球队",["全部"]+sorted(set(predictions.team_a)|set(predictions.team_b)));correct=c3.selectbox("预测表现",["全部","正确","错误"])
    x=predictions.copy()
    if stage:x=x[x.stage.isin(stage)]
    if team!="全部":x=x[(x.team_a==team)|(x.team_b==team)]
    if correct!="全部":x=x[x.correct_prediction.astype(str).str.lower().eq("true" if correct=="正确" else "false")]
    hide=st.toggle("预测时隐藏真实结果",value=True)
    for r in x.head(40).itertuples():
        with st.container(border=True):
            a,b,c=st.columns([2,3,2]);a.markdown(f"**{r.team_a} vs {r.team_b}**  \n{r.stage}");b.progress(float(r.team_a_win_90),text=f"{r.team_a} {pct(r.team_a_win_90)} · 平 {pct(r.draw_90)} · {r.team_b} {pct(r.team_b_win_90)}");c.markdown("真实结果已隐藏" if hide else f"真实比分 **{actual_result(r)}**  \n预测{'正确' if str(r.correct_prediction).lower()=='true' else '错误'}")

def selected_prediction():
    labels={f"{r.team_a} vs {r.team_b} · {r.stage} · {r.match_id}":r.match_id for r in predictions.itertuples()};label=st.selectbox("选择比赛",list(labels));return predictions[predictions.match_id.eq(labels[label])].iloc[0]

def report():
    st.title("单场比赛报告");r=selected_prediction();mode=st.radio("显示模式",["新手模式","专业模式"],horizontal=True)
    st.header(f"{r.team_a}  vs  {r.team_b}");a,b,c,d=st.columns(4);a.metric(f"{r.team_a} 90分钟胜",pct(r.team_a_win_90));b.metric("平局",pct(r.draw_90));c.metric(f"{r.team_b} 90分钟胜",pct(r.team_b_win_90));d.metric("预测比分",f"{int(r.predicted_score_a)}–{int(r.predicted_score_b)}")
    md_path=REPORTS/f"{r.match_id}.md";md=md_path.read_text(encoding="utf-8") if md_path.exists() else "报告文件缺失"
    st.markdown(md)
    if mode=="专业模式":
        st.subheader("模型组件与重归一化权重")
        for col in ("components","final_weights","availability"):
            if col in r and isinstance(r[col],str):
                try:st.json(ast.literal_eval(r[col]))
                except:st.code(r[col])
        pa,pb=xt.profile(r.team_a),xt.profile(r.team_b);ca,cb=st.columns(2)
        with ca:
            fig=xt_heatmap(pa);st.pyplot(fig) if fig else st.info(f"{r.team_a} 无兼容 xT 档案")
        with cb:
            fig=xt_heatmap(pb);st.pyplot(fig) if fig else st.info(f"{r.team_b} 无兼容 xT 档案")
        fig=difference_heatmap(pa,pb)
        if fig:st.pyplot(fig)
        st.caption("方向沿用原实验的 12×16 网格；当前审计未发现旋转代码。若原 notebook 的坐标约定改变，应重新确认方向。")
    st.download_button("下载 Markdown 报告",md,file_name=f"{r.match_id}.md")

def comparison():
    st.title("球队风格对比");teams=sorted(set(matches.home_team)|set(matches.away_team));a,b=st.columns(2);ta=a.selectbox("球队 A",teams,index=teams.index("Spain") if "Spain" in teams else 0);tb=b.selectbox("球队 B",teams,index=teams.index("Argentina") if "Argentina" in teams else 1);pa,pb=xt.profile(ta),xt.profile(tb)
    for col,p in zip(st.columns(2),(pa,pb)):
        with col:
            st.subheader(p.team)
            if p.data_available:
                st.write(f"实验 {p.experiment} · {p.source_competition} {p.source_season} · 聚类 {p.cluster_id}");st.info(p.cluster_label);fig=xt_heatmap(p);st.pyplot(fig)
                st.dataframe(pd.DataFrame([p.spatial]).T.rename(columns={0:"占比"}),width="stretch")
            else:st.warning("历史 xT 档案不可用；不会生成伪热图。")
    sim=xt.similarity(ta,tb);st.metric("xT 空间余弦相似度",f"{sim:.3f}" if sim is not None else "不可用")
    csv=pd.DataFrame([{"team":p.team,"experiment":p.experiment,"competition":p.source_competition,"season":p.source_season,"cluster":p.cluster_id,"description":p.cluster_label} for p in (pa,pb)]).to_csv(index=False).encode("utf-8-sig");st.download_button("下载对比 CSV",csv,"team_comparison.csv")

def simulator():
    st.title("世界杯重新模拟");st.warning("此模式从模型预测的小组积分榜产生晋级队，淘汰赛不读取真实参赛队。")
    sim=simulation_json()
    if not sim:st.info("先运行 `python -m src.world_cup_dashboard.batch_predict --mode full_simulation`。");return
    st.metric("确定性模拟冠军",sim["champion"]);st.caption(sim.get("bracket_note",""))
    tabs=st.tabs([f"{g}组" for g in sim["group_tables"]])
    for tab,(g,rows) in zip(tabs,sim["group_tables"].items()):
        with tab:st.dataframe(pd.DataFrame(rows),width="stretch",hide_index=True)
    st.subheader("最佳第三名");st.dataframe(pd.DataFrame(sim["best_third_place"]),width="stretch",hide_index=True)
    st.download_button("下载模拟 JSON",json.dumps(sim,ensure_ascii=False,indent=2),"full_tournament_simulation.json")

def evaluation():
    st.title("模型表现评估");m=metric_json();cols=st.columns(4);cols[0].metric("三分类准确率",pct(m.get("three_class_accuracy",0)));cols[1].metric("非平局胜方准确率",pct(m.get("winner_accuracy",0)));cols[2].metric("Log loss",f"{m.get('log_loss',0):.3f}");cols[3].metric("Brier score",f"{m.get('brier_score',0):.3f}")
    x=predictions.copy();x["correct"]=x.correct_prediction.astype(str).str.lower().eq("true");st.subheader("分阶段准确率");st.bar_chart(x.groupby("stage").correct.mean())
    cal=EVALUATION/"calibration.csv"
    if cal.exists():
        c=pd.read_csv(cal);st.subheader("校准");st.line_chart(c.set_index("predicted_probability")["observed_accuracy"]);st.dataframe(c,width="stretch",hide_index=True)
    st.subheader("混淆矩阵")
    actual=x.apply(lambda r:"主胜" if r.actual_home_score>r.actual_away_score else "客胜" if r.actual_home_score<r.actual_away_score else "平",axis=1);pred=x[["team_a_win_90","draw_90","team_b_win_90"]].idxmax(axis=1).map({"team_a_win_90":"主胜","draw_90":"平","team_b_win_90":"客胜"});st.dataframe(pd.crosstab(actual,pred,rownames=["真实"],colnames=["预测"]),width="stretch")
    st.download_button("下载评价 CSV",x.to_csv(index=False).encode("utf-8-sig"),"evaluation_predictions.csv")

def methodology():
    st.title("模型原理与局限")
    st.markdown("""### 给新手\n\n**xT** 衡量传球或带球让球队更接近进球的程度。**聚类**只把历史威胁分布相似的样本放在一起，不代表球队强弱排名。阵型统计表示历史测试场景，不代表本场确认阵型。\n\n**历史回测**会在每场开球前冻结信息，先预测，再揭晓结果，最后才更新后续比赛的状态。这样可以避免把未来结果偷偷带回过去。\n\n### 技术结构\n\n`xT 风格 + 阵型对位 + 实力代理 + 截至开球前的本届赛事表现 → 可解释概率`。默认演示权重为 45% / 20% / 20% / 15%；缺失组件被移除后按比例重归一化。三分类概率由受限优势分数映射，比分由独立 Poisson 近似产生。\n\n### 已知局限\n\n- 没有完整的 2026 赛事级 StatsBomb 事件数据，xT 使用历史国家队代理档案。\n- 教练、球员、伤病、首发、压迫、防守结构和定位球没有被完整建模。\n- 阵型对位样本可能较小；无法找到时不编造统计。\n- 融合权重是透明演示选择，不是统计优化结果。\n- 全赛事模拟采用固定种子顺序构造模型淘汰赛，目的是保证晋级队完全由模型产生。\n- 本项目用于分析展示，不适用于投注。\n""")

{"赛事总览":overview,"逐场预测回放":replay,"单场比赛报告":report,"球队风格对比":comparison,"世界杯重新模拟":simulator,"模型表现评估":evaluation,"模型原理与局限":methodology}[page]()
