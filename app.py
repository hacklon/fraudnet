import streamlit as st
import plotly.graph_objects as go
from agent import investigate

st.set_page_config(
    page_title="FraudNet | Investigation Center",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Polished dark analyst-console styling.
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=Manrope:wght@400;500;600;700;800&display=swap');
:root { --bg:#0b1020; --panel:#111a2e; --panel2:#151f35; --line:#25324a; --muted:#8fa2bf; --text:#eaf0fb; --cyan:#58d6e8; --purple:#9c8cff; }
html, body, [class*="css"] { font-family: 'Manrope', sans-serif; }
.stApp { background: radial-gradient(ellipse at 20% 0%, #172342 0%, #0b1020 48%); color:var(--text); }
.block-container { max-width: 1500px; padding-top: 1.5rem; padding-bottom: 3rem; }
[data-testid="stSidebar"] { background:#0d1527; border-right:1px solid var(--line); }
[data-testid="stSidebar"] * { color:var(--text); }
h1,h2,h3 { letter-spacing:-.035em; }
.hero { padding: 1.2rem 1.4rem; border:1px solid #293958; border-radius:22px; background:linear-gradient(120deg,rgba(27,44,75,.92),rgba(17,26,46,.85)); margin-bottom:1.1rem; }
.eyebrow { text-transform:uppercase; letter-spacing:.18em; font-size:.72rem; font-weight:800; color:var(--cyan); }
.hero-title { font-size:2.1rem; font-weight:800; line-height:1.15; margin:.45rem 0; }
.hero-copy { color:#a9bad4; font-size:.94rem; max-width:800px; }
.panel { background:linear-gradient(180deg,rgba(21,31,53,.96),rgba(15,24,42,.96)); border:1px solid var(--line); border-radius:18px; padding:1rem 1.1rem; height:100%; }
.panel-label { color:var(--muted); text-transform:uppercase; letter-spacing:.12em; font-size:.69rem; font-weight:800; }
.metric-value { font-size:1.9rem; font-weight:800; letter-spacing:-.04em; margin:.25rem 0; }
.metric-note { color:var(--muted); font-size:.78rem; }
.pill { display:inline-block; border:1px solid #344565; color:#c8d7ee; background:#18243c; border-radius:999px; padding:.25rem .6rem; font-size:.72rem; font-weight:700; }
.pill-high { border-color:#7f3349; color:#ff9aae; background:#351927; }
.section-head { display:flex; align-items:center; gap:.55rem; margin:1.2rem 0 .6rem; font-size:1.13rem; font-weight:800; }
.small-muted { color:var(--muted); font-size:.83rem; }
.evidence { border:1px solid var(--line); background:#111a2e; border-radius:12px; padding:.8rem .9rem; margin:.45rem 0; color:#dce6f7; }
.evidence-num { color:var(--cyan); font-family:'DM Mono',monospace; font-size:.75rem; margin-right:.5rem; }
div.stButton > button { border-radius:12px; border:1px solid #5d6be6; background:linear-gradient(120deg,#635bdb,#357fd3); color:white; font-weight:800; min-height:2.8rem; }
div.stButton > button:hover { border-color:#79e4f1; color:white; box-shadow:0 0 0 3px rgba(88,214,232,.12); }
div[data-testid="stDataFrame"] { border:1px solid var(--line); border-radius:12px; overflow:hidden; }
.stProgress > div > div > div { background:linear-gradient(90deg,#4b91e8,#58d6e8); }
hr { border-color:var(--line); }
[data-testid="stMetric"] { background:#111a2e; border:1px solid var(--line); border-radius:15px; padding:1rem; }
[data-testid="stMetricLabel"] { color:var(--muted); }
[data-testid="stMetricValue"] { color:var(--text); }
</style>
""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("## 🛡️ FraudNet")
    st.markdown('<span class="pill">GRAPH INTELLIGENCE</span>', unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("### Investigation")
    account_id = st.text_input("Target account", value="R0M00", placeholder="e.g. R0M00")
    run = st.button("⌕  Run investigation", type="primary", use_container_width=True)
    st.markdown("---")
    st.markdown("**Graph source**")
    st.markdown('<span class="pill">FalkorDB · fraudnet</span>', unsafe_allow_html=True)
    st.caption("Synthetic investigation environment")
    st.markdown("---")
    st.caption("Prototype risk score is a transparent heuristic, not a calibrated probability or proof of fraud.")

st.markdown("""
<div class="hero">
  <div class="eyebrow">Financial intelligence · Graph investigation</div>
  <div class="hero-title">Investigation command center</div>
  <div class="hero-copy">Trace connected entities, inspect transaction pathways, and understand why an account was prioritized — with evidence retrieved from FalkorDB.</div>
</div>
""", unsafe_allow_html=True)

if run:
    try:
        with st.spinner("Traversing graph relationships and assembling evidence…"):
            st.session_state["result"] = investigate(account_id.strip())
            st.session_state["searched_account"] = account_id.strip()
    except Exception as exc:
        st.error("Investigation failed. Check the FalkorDB connection and graph.")
        st.code(f"{type(exc).__name__}: {exc}")

result = st.session_state.get("result")
if not result:
    st.markdown("""
    <div class="panel">
      <div class="eyebrow">Ready for analysis</div>
      <h3>Start with an account</h3>
      <p class="small-muted">Enter an account ID in the left panel and run an investigation. The agent will query shared devices, shared IPs, transfers, and potential mule-to-cashout paths.</p>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

if result.get("error"):
    st.error(result["error"])
    st.stop()

score = int(result["risk_score"])
level = result["risk_level"]
level_class = "pill-high" if level == "HIGH" else "pill"
st.markdown(f"""
<div style="display:flex;justify-content:space-between;align-items:center;margin:.5rem 0 1rem;gap:1rem;flex-wrap:wrap">
  <div>
    <div class="eyebrow">Target under review</div>
    <div style="font-size:1.65rem;font-weight:800;letter-spacing:-.04em">{result['account_id']}</div>
    <div class="small-muted">Investigation generated from live graph queries</div>
  </div>
  <div><span class="pill {level_class}">{level} PRIORITY</span> &nbsp; <span class="pill">SYNTHETIC DATA</span></div>
</div>
""", unsafe_allow_html=True)

m1, m2, m3, m4 = st.columns(4)
m1.metric("Risk score", f"{score}/100", help="Rule-based prioritization score, not a fraud probability.")
m2.metric("Account age", f"{result['age_days']} days")
m3.metric("Shared devices", len(result["shared_devices"]))
m4.metric("Mule → cashout paths", len(result["transfer_flow"]))
st.progress(score / 100)
st.markdown('<div class="small-muted">Risk score indicates review priority only. It is not proof of wrongdoing.</div>', unsafe_allow_html=True)

left, right = st.columns([1.05, 1.25], gap="large")
with left:
    st.markdown('<div class="section-head">◈ Why this account was flagged</div>', unsafe_allow_html=True)
    for i, reason in enumerate(result["reasons"], 1):
        st.markdown(f'<div class="evidence"><span class="evidence-num">EVIDENCE {i:02d}</span>{reason}</div>', unsafe_allow_html=True)
    for warning in result["warnings"]:
        st.warning(warning)
with right:
    st.markdown('<div class="section-head">↗ Investigation snapshot</div>', unsafe_allow_html=True)
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.markdown(f"**Graph queried:** `{result.get('graph_name', 'fraudnet')}`")
    st.write(f"Found **{len(result['shared_devices'])}** shared-device connection(s), **{len(result['shared_ips'])}** shared-IP connection(s), **{len(result['outgoing_transfers'])}** outgoing transaction(s), and **{len(result['transfer_flow'])}** matching transfer path(s).")
    st.markdown('<span class="pill">Evidence-first workflow</span> <span class="pill">Human review recommended</span>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown("---")
st.markdown('<div class="section-head">⇢ Money movement</div>', unsafe_allow_html=True)
st.markdown('<div class="small-muted">Sankey links show individual observed transfer amounts. They do not prove the same funds were traced end-to-end.</div>', unsafe_allow_html=True)
flows = result["transfer_flow"]
if flows:
    labels, sources, targets, values, hover = [], [], [], [], []
    def node_index(label):
        if label not in labels:
            labels.append(label)
        return labels.index(label)
    for flow in flows:
        s, m, c = node_index(flow["source"]), node_index(flow["mule"]), node_index(flow["cashout"])
        sources.extend([s, m]); targets.extend([m, c])
        values.extend([max(float(flow["to_mule_amount"] or 0), .01), max(float(flow["to_cashout_amount"] or 0), .01)])
        hover.extend([
            f"{flow['source']} → {flow['mule']}<br>Amount: {flow['to_mule_amount']}<br>Day: {flow['first_day']}",
            f"{flow['mule']} → {flow['cashout']}<br>Amount: {flow['to_cashout_amount']}<br>Day: {flow['cashout_day']}",
        ])
    fig = go.Figure(go.Sankey(
        arrangement="snap",
        node=dict(label=labels, pad=24, thickness=22, line=dict(width=1, color="#435575")),
        link=dict(source=sources, target=targets, value=values, customdata=hover, hovertemplate="%{customdata}<extra></extra>"),
    ))
    fig.update_layout(
        height=410, margin=dict(l=12, r=12, t=15, b=10),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#eaf0fb", size=12, family="Manrope"),
    )
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("No account → mule → cashout path found for this account.")

st.markdown("---")
st.markdown('<div class="section-head">⌘ Connected evidence</div>', unsafe_allow_html=True)
tab1, tab2, tab3 = st.tabs(["◉ Shared devices", "◎ Shared IP addresses", "⇄ Outgoing transfers"])
with tab1:
    st.dataframe(result["shared_devices"], use_container_width=True, hide_index=True)
with tab2:
    st.dataframe(result["shared_ips"], use_container_width=True, hide_index=True)
with tab3:
    st.dataframe(result["outgoing_transfers"], use_container_width=True, hide_index=True)

with st.expander("How the agent investigates"):
    st.markdown("""
    1. Looks up the target account in FalkorDB.
    2. Traverses `USES` and `LOGGED_FROM` relationships to find shared infrastructure.
    3. Reads outgoing `SENT` relationships and searches for account → mule → cashout paths.
    4. Applies transparent heuristic rules to prioritize investigation.
    5. Presents evidence and warnings about benign shared infrastructure.

    This version uses deterministic rules, not a trained model or an LLM. Shared devices and IPs are not proof of fraud.
    """)
