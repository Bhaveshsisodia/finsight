import streamlit as st
import sys
import os
import plotly.graph_objects as go
import pandas as pd

# ── Path setup ───────────────────────────────────────────────────────────────
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

# ── Streamlit version compat ─────────────────────────────────────────────────
_rerun = getattr(st, "rerun", None) or getattr(st, "experimental_rerun", None)

# ── Page Config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="FinSight India",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
/* ── Google Font ── */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

/* ── Background ── */
.stApp {
    background: linear-gradient(135deg, #0a0e1a 0%, #0d1b2a 50%, #0a1628 100%);
    color: #e2e8f0;
}

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0f172a 0%, #1e293b 100%);
    border-right: 1px solid #1e3a5f;
}

/* ── Hide default header ── */
header[data-testid="stHeader"] { display: none; }

/* ── Hero banner ── */
.hero-banner {
    background: linear-gradient(135deg, #0f3460 0%, #16213e 50%, #0a2540 100%);
    border: 1px solid #1e4d7a;
    border-radius: 16px;
    padding: 24px 32px;
    margin-bottom: 24px;
    display: flex;
    align-items: center;
    gap: 16px;
}
.hero-title {
    font-size: 2.2rem;
    font-weight: 800;
    background: linear-gradient(90deg, #60a5fa, #38bdf8, #34d399);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin: 0;
}
.hero-sub {
    font-size: 0.95rem;
    color: #94a3b8;
    margin: 4px 0 0 0;
}

/* ── Metric cards ── */
.metric-card {
    background: linear-gradient(135deg, #1e293b, #0f172a);
    border: 1px solid #1e3a5f;
    border-radius: 12px;
    padding: 20px 24px;
    text-align: center;
    transition: transform 0.2s, border-color 0.2s;
}
.metric-card:hover {
    transform: translateY(-2px);
    border-color: #3b82f6;
}
.metric-label {
    font-size: 0.75rem;
    font-weight: 600;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: #64748b;
    margin-bottom: 8px;
}
.metric-value {
    font-size: 1.9rem;
    font-weight: 800;
    color: #f1f5f9;
}
.metric-sub {
    font-size: 0.8rem;
    color: #64748b;
    margin-top: 4px;
}

/* ── Signal chips ── */
.signal-buy   { color: #34d399; font-size:1.9rem; font-weight:800; }
.signal-sell  { color: #f87171; font-size:1.9rem; font-weight:800; }
.signal-hold  { color: #fbbf24; font-size:1.9rem; font-weight:800; }

/* ── Section headers ── */
.section-header {
    font-size: 1.1rem;
    font-weight: 700;
    color: #60a5fa;
    border-left: 3px solid #3b82f6;
    padding-left: 12px;
    margin: 20px 0 12px 0;
}

/* ── Analysis card ── */
.analysis-card {
    background: #1e293b;
    border: 1px solid #334155;
    border-radius: 10px;
    padding: 16px 20px;
    margin-bottom: 12px;
}
.analysis-card h4 {
    font-size: 0.8rem;
    font-weight: 600;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: #64748b;
    margin: 0 0 6px 0;
}
.analysis-card p {
    font-size: 0.95rem;
    color: #cbd5e1;
    margin: 0;
    line-height: 1.6;
}

/* ── Badge ── */
.badge {
    display: inline-block;
    padding: 3px 10px;
    border-radius: 20px;
    font-size: 0.78rem;
    font-weight: 600;
    margin-right: 6px;
}
.badge-green  { background:#064e3b; color:#34d399; }
.badge-red    { background:#450a0a; color:#f87171; }
.badge-yellow { background:#451a03; color:#fbbf24; }
.badge-blue   { background:#1e3a5f; color:#60a5fa; }
.badge-gray   { background:#1e293b; color:#94a3b8; }

/* ── Score bars ── */
.score-bar-wrapper {
    margin-bottom: 14px;
}
.score-bar-label {
    display: flex;
    justify-content: space-between;
    font-size: 0.85rem;
    color: #94a3b8;
    margin-bottom: 4px;
}
.score-bar-bg {
    background: #1e293b;
    border-radius: 8px;
    height: 10px;
    overflow: hidden;
}
.score-bar-fill {
    height: 100%;
    border-radius: 8px;
    transition: width 0.8s ease;
}

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {
    background: #1e293b;
    border-radius: 10px;
    padding: 4px;
    gap: 4px;
    border: 1px solid #334155;
}
.stTabs [data-baseweb="tab"] {
    background: transparent;
    border-radius: 8px;
    color: #64748b;
    font-weight: 500;
    padding: 8px 16px;
    border: none;
}
.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, #1d4ed8, #2563eb) !important;
    color: #fff !important;
}

/* ── Report box ── */
.report-box {
    background: #0f172a;
    border: 1px solid #1e3a5f;
    border-radius: 12px;
    padding: 24px;
    font-size: 0.9rem;
    color: #cbd5e1;
    line-height: 1.8;
    white-space: pre-wrap;
}

/* ── Sidebar buttons ── */
.stButton > button {
    background: linear-gradient(135deg, #1d4ed8, #2563eb);
    color: white;
    border: none;
    border-radius: 8px;
    font-weight: 600;
    transition: all 0.2s;
}
.stButton > button:hover {
    background: linear-gradient(135deg, #2563eb, #3b82f6);
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(59,130,246,0.4);
}

/* ── Input ── */
.stTextInput > div > div > input {
    background: #1e293b;
    border: 1px solid #334155;
    color: #f1f5f9;
    border-radius: 8px;
}
.stTextInput > div > div > input:focus {
    border-color: #3b82f6;
    box-shadow: 0 0 0 2px rgba(59,130,246,0.25);
}

/* ── Spinner ── */
.stSpinner > div { border-top-color: #3b82f6 !important; }

/* ── Divider ── */
hr { border-color: #1e3a5f !important; }

/* ── Table ── */
.stDataFrame { border-radius: 10px; overflow: hidden; }

/* ── Warning/error ── */
.stAlert { border-radius: 10px; }
</style>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════════════════════════════

def badge(text: str, variant: str = "blue") -> str:
    return f'<span class="badge badge-{variant}">{text}</span>'

def score_color(score: int) -> str:
    if score >= 65:
        return "#34d399"
    elif score >= 45:
        return "#fbbf24"
    else:
        return "#f87171"

def render_score_bar(name: str, score: int):
    color = score_color(score)
    st.markdown(f"""
    <div class="score-bar-wrapper">
        <div class="score-bar-label">
            <span>{name}</span>
            <span style="font-weight:700;color:{color}">{score}/100</span>
        </div>
        <div class="score-bar-bg">
            <div class="score-bar-fill" style="width:{score}%;background:{color};"></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def render_kv(label: str, value, variant: str = "blue"):
    st.markdown(f"""
    <div class="analysis-card">
        <h4>{label}</h4>
        <p>{badge(str(value), variant)}</p>
    </div>
    """, unsafe_allow_html=True)

def render_summary_card(text: str):
    st.markdown(f"""
    <div class="analysis-card">
        <h4>AI Summary</h4>
        <p>{text}</p>
    </div>
    """, unsafe_allow_html=True)

def render_key_points(points: list):
    if not points:
        return
    items = "".join(f"<li style='margin-bottom:6px;color:#cbd5e1;'>{p}</li>" for p in points)
    st.markdown(f"""
    <div class="analysis-card">
        <h4>Key Points</h4>
        <ul style="margin:0;padding-left:20px;">{items}</ul>
    </div>
    """, unsafe_allow_html=True)

def radar_chart(scores: dict) -> go.Figure:
    cats = list(scores.keys())
    vals = list(scores.values())
    cats_closed = cats + [cats[0]]
    vals_closed = vals + [vals[0]]

    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=vals_closed, theta=cats_closed, fill='toself',
        fillcolor='rgba(59,130,246,0.18)',
        line=dict(color='#3b82f6', width=2),
        marker=dict(color='#60a5fa', size=7),
        name='Score'
    ))
    fig.update_layout(
        polar=dict(
            bgcolor='rgba(0,0,0,0)',
            angularaxis=dict(linecolor='#334155', gridcolor='#1e293b', color='#94a3b8', tickfont=dict(size=12, color='#94a3b8')),
            radialaxis=dict(range=[0, 100], gridcolor='#1e293b', linecolor='#1e293b',
                            tickfont=dict(size=10, color='#475569'), showline=False)
        ),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=40, r=40, t=30, b=30),
        showlegend=False,
        height=320,
    )
    return fig


# ═══════════════════════════════════════════════════════════════════════════════
# RUN ANALYSIS
# ═══════════════════════════════════════════════════════════════════════════════

def run_analysis(symbol: str) -> dict:
    from graph.workflow import app as workflow_app
    result = workflow_app.invoke({"symbol": symbol.upper().strip()})
    return result


# ═══════════════════════════════════════════════════════════════════════════════
# SESSION STATE
# ═══════════════════════════════════════════════════════════════════════════════

if "result" not in st.session_state:
    st.session_state.result = None
if "symbol" not in st.session_state:
    st.session_state.symbol = ""
if "error" not in st.session_state:
    st.session_state.error = None


# ═══════════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ═══════════════════════════════════════════════════════════════════════════════

with st.sidebar:
    st.markdown("""
    <div style="text-align:center;padding:20px 0 16px 0;">
        <div style="font-size:2.5rem;">📈</div>
        <div style="font-size:1.2rem;font-weight:800;background:linear-gradient(90deg,#60a5fa,#38bdf8);-webkit-background-clip:text;-webkit-text-fill-color:transparent;">FinSight India</div>
        <div style="font-size:0.75rem;color:#475569;margin-top:4px;">AI-Powered Stock Research</div>
    </div>
    """, unsafe_allow_html=True)

    st.divider()

    symbol_input = st.text_input(
        "🔍 NSE Symbol",
        value=st.session_state.symbol,
        placeholder="e.g. RELIANCE, TCS, INFY",
        key="symbol_input_field"
    )

    run_clicked = st.button("🚀 Run Analysis", use_container_width=True, type="primary")

    st.divider()
    st.markdown('<p style="font-size:0.75rem;color:#475569;font-weight:600;letter-spacing:0.08em;text-transform:uppercase;">⚡ Quick Picks</p>', unsafe_allow_html=True)

    popular = [
        ("🏦", "HDFCBANK"), ("💻", "TCS"), ("🛢️", "RELIANCE"),
        ("💡", "INFY"), ("🏗️", "LTIM"), ("🏪", "WIPRO"),
        ("🏦", "SBIN"), ("💊", "SUNPHARMA"),
    ]
    cols = st.columns(2)
    for i, (icon, s) in enumerate(popular):
        if cols[i % 2].button(f"{icon} {s}", use_container_width=True, key=f"qp_{s}"):
            st.session_state.symbol = s
            symbol_input = s
            # auto-trigger analysis
            with st.spinner(f"Analyzing {s}…"):
                try:
                    st.session_state.result = run_analysis(s)
                    st.session_state.error = None
                except Exception as e:
                    st.session_state.result = None
                    st.session_state.error = str(e)
            _rerun()

    st.divider()
    st.markdown('<p style="font-size:0.7rem;color:#334155;text-align:center;">Data via NSE India · Analysis by AI</p>', unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
# HANDLE RUN
# ═══════════════════════════════════════════════════════════════════════════════

if run_clicked and symbol_input.strip():
    sym = symbol_input.strip().upper()
    st.session_state.symbol = sym
    with st.spinner(f"🔍 Running deep analysis on **{sym}** — this may take 30–60 seconds…"):
        try:
            st.session_state.result = run_analysis(sym)
            st.session_state.error = None
        except Exception as e:
            st.session_state.result = None
            st.session_state.error = str(e)


# ═══════════════════════════════════════════════════════════════════════════════
# HERO BANNER
# ═══════════════════════════════════════════════════════════════════════════════

st.markdown("""
<div class="hero-banner">
    <div style="font-size:3rem;">📈</div>
    <div>
        <p class="hero-title">FinSight India</p>
        <p class="hero-sub">Multi-dimensional AI stock research · Fundamental · Technical · News · FII/DII · Relative Strength</p>
    </div>
</div>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
# ERROR STATE
# ═══════════════════════════════════════════════════════════════════════════════

if st.session_state.error:
    st.error(f"⚠️ Analysis failed: {st.session_state.error}")


# ═══════════════════════════════════════════════════════════════════════════════
# EMPTY STATE
# ═══════════════════════════════════════════════════════════════════════════════

if st.session_state.result is None and not st.session_state.error:
    st.markdown("""
    <div style="text-align:center;padding:80px 20px;">
        <div style="font-size:5rem;margin-bottom:20px;">🔍</div>
        <h2 style="color:#475569;font-weight:700;margin-bottom:12px;">Search a Stock to Begin</h2>
        <p style="color:#334155;font-size:1rem;max-width:500px;margin:0 auto;">
            Enter an NSE symbol in the sidebar (e.g. <strong style="color:#60a5fa">RELIANCE</strong>, <strong style="color:#60a5fa">TCS</strong>)
            and click <strong style="color:#34d399">Run Analysis</strong> to get an AI-powered research report.
        </p>
    </div>
    """, unsafe_allow_html=True)
    st.stop()


# ═══════════════════════════════════════════════════════════════════════════════
# RESULTS
# ═══════════════════════════════════════════════════════════════════════════════

r = st.session_state.result
if r is None:
    st.stop()

symbol          = st.session_state.symbol
final_score     = round(r.get("final_score", 0), 1)
signal          = r.get("signal", "HOLD")
confidence      = round(r.get("confidence", 0), 1)
fund_analysis   = r.get("fundamental_analysis", {}) or {}
tech_analysis   = r.get("technical_analysis", {}) or {}
news_analysis   = r.get("news_analysis", {}) or {}
fpi_analysis    = r.get("fpi_analysis", {}) or {}
rel_analysis    = r.get("relative_analysis", {}) or {}
fpi_raw         = r.get("fpi_raw", {}) or {}
report          = r.get("report", "")

scores = {
    "Fundamental":       r.get("fundamental_score", 50),
    "Technical":         r.get("technical_score", 50),
    "News":              r.get("news_score", 50),
    "FPI/FII":           r.get("fpi_score", 50),
    "Relative Strength": r.get("relative_score", 50),
}

signal_class = {"BUY": "signal-buy", "SELL": "signal-sell"}.get(signal, "signal-hold")

# ── Symbol header ─────────────────────────────────────────────────────────────
st.markdown(f"""
<div style="display:flex;align-items:center;gap:12px;margin-bottom:20px;">
    <div style="font-size:1.6rem;font-weight:800;color:#f1f5f9;">📊 {symbol}</div>
    <div style="font-size:0.85rem;color:#475569;background:#1e293b;padding:4px 12px;border-radius:20px;border:1px solid #334155;">NSE Listed</div>
</div>
""", unsafe_allow_html=True)

# ── Metric cards ──────────────────────────────────────────────────────────────
c1, c2, c3, c4 = st.columns(4)

with c1:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Final Score</div>
        <div class="metric-value" style="color:{score_color(int(final_score))}">{final_score}</div>
        <div class="metric-sub">out of 100</div>
    </div>
    """, unsafe_allow_html=True)

with c2:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Signal</div>
        <div class="{signal_class}">{signal}</div>
        <div class="metric-sub">Recommendation</div>
    </div>
    """, unsafe_allow_html=True)

with c3:
    conf_color = score_color(int(confidence))
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Confidence</div>
        <div class="metric-value" style="color:{conf_color}">{confidence}%</div>
        <div class="metric-sub">Signal strength</div>
    </div>
    """, unsafe_allow_html=True)

with c4:
    tech_trend = tech_analysis.get("trend", "—")
    trend_var  = "green" if "Bull" in str(tech_trend) else "red" if "Bear" in str(tech_trend) else "yellow"
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Technical Trend</div>
        <div class="metric-value" style="font-size:1.3rem;">{tech_trend}</div>
        <div class="metric-sub">Price action</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<div style='height:24px'></div>", unsafe_allow_html=True)

# ── Score overview ─────────────────────────────────────────────────────────────
left_col, right_col = st.columns([1, 1])

with left_col:
    st.markdown('<div class="section-header">📊 Score Breakdown</div>', unsafe_allow_html=True)
    for name, score in scores.items():
        render_score_bar(name, score)

with right_col:
    st.markdown('<div class="section-header">🕸️ Dimension Radar</div>', unsafe_allow_html=True)
    st.plotly_chart(radar_chart(scores), use_container_width=True, config={"displayModeBar": False})

st.divider()

# ═══════════════════════════════════════════════════════════════════════════════
# DETAIL TABS
# ═══════════════════════════════════════════════════════════════════════════════

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 Fundamental",
    "📈 Technical",
    "📰 News Sentiment",
    "🏛️ FII / DII",
    "⚡ Relative Strength",
])

# ── TAB 1: FUNDAMENTAL ───────────────────────────────────────────────────────
with tab1:
    st.markdown('<div class="section-header">Fundamental Analysis</div>', unsafe_allow_html=True)
    fa = fund_analysis

    kv_cols = st.columns(4)
    items = [
        ("Profitability",  fa.get("profitability", "—"),  "green"),
        ("Growth",         fa.get("growth", "—"),          "blue"),
        ("Valuation",      fa.get("valuation", "—"),       "yellow"),
        ("Risk",           fa.get("risk", "—"),            "red" if fa.get("risk","—")=="High" else "yellow"),
    ]
    for col, (lbl, val, var) in zip(kv_cols, items):
        with col:
            st.markdown(f"""
            <div class="analysis-card" style="text-align:center;">
                <h4>{lbl}</h4>
                <p>{badge(val, var)}</p>
            </div>
            """, unsafe_allow_html=True)

    render_summary_card(fa.get("summary", "No summary available."))

    with st.expander("📄 Raw Fundamental Data"):
        raw = r.get("fundamental_data", "")
        st.code(str(raw)[:3000] if raw else "No raw data", language="text")


# ── TAB 2: TECHNICAL ─────────────────────────────────────────────────────────
with tab2:
    st.markdown('<div class="section-header">Technical Analysis</div>', unsafe_allow_html=True)
    ta = tech_analysis

    t_cols = st.columns(3)
    trend_var = "green" if "Bull" in str(ta.get("trend","")) else "red" if "Bear" in str(ta.get("trend","")) else "yellow"
    with t_cols[0]:
        st.markdown(f"""
        <div class="analysis-card" style="text-align:center;">
            <h4>Trend</h4>
            <p>{badge(ta.get("trend","—"), trend_var)}</p>
        </div>
        """, unsafe_allow_html=True)
    with t_cols[1]:
        st.markdown(f"""
        <div class="analysis-card" style="text-align:center;">
            <h4>Technical Score</h4>
            <p style="font-size:1.4rem;font-weight:800;color:{score_color(scores['Technical'])}">{scores['Technical']}/100</p>
        </div>
        """, unsafe_allow_html=True)
    with t_cols[2]:
        st.markdown(f"""
        <div class="analysis-card" style="text-align:center;">
            <h4>Momentum</h4>
            <p>{badge(ta.get("momentum","—") if "momentum" in ta else "—", "blue")}</p>
        </div>
        """, unsafe_allow_html=True)

    render_key_points(ta.get("signals", []))
    render_summary_card(ta.get("summary", "No summary available."))

    with st.expander("📄 Raw Technical Data"):
        raw = r.get("technical_data", "")
        st.code(str(raw)[:3000] if raw else "No raw data", language="text")


# ── TAB 3: NEWS ──────────────────────────────────────────────────────────────
with tab3:
    st.markdown('<div class="section-header">News Sentiment Analysis</div>', unsafe_allow_html=True)
    na = news_analysis

    n_cols = st.columns(3)
    sentiment_str = na.get("sentiment", "Neutral")
    sentiment_var = "green" if "Bull" in str(sentiment_str) else "red" if "Bear" in str(sentiment_str) else "yellow"
    conf_str = na.get("confidence", "—")
    conf_var  = "green" if conf_str == "High" else "yellow" if conf_str == "Medium" else "gray"

    with n_cols[0]:
        st.markdown(f"""
        <div class="analysis-card" style="text-align:center;">
            <h4>Sentiment</h4>
            <p>{badge(sentiment_str, sentiment_var)}</p>
        </div>
        """, unsafe_allow_html=True)
    with n_cols[1]:
        st.markdown(f"""
        <div class="analysis-card" style="text-align:center;">
            <h4>News Score</h4>
            <p style="font-size:1.4rem;font-weight:800;color:{score_color(scores['News'])}">{scores['News']}/100</p>
        </div>
        """, unsafe_allow_html=True)
    with n_cols[2]:
        st.markdown(f"""
        <div class="analysis-card" style="text-align:center;">
            <h4>Confidence</h4>
            <p>{badge(conf_str, conf_var)}</p>
        </div>
        """, unsafe_allow_html=True)

    render_key_points(na.get("key_points", []))
    render_summary_card(na.get("summary", "No summary available."))

    with st.expander("📄 Raw News Data"):
        raw = r.get("news_data", "")
        st.code(str(raw)[:3000] if raw else "No raw data", language="text")


# ── TAB 4: FII/DII ───────────────────────────────────────────────────────────
with tab4:
    st.markdown('<div class="section-header">FII / DII Activity</div>', unsafe_allow_html=True)
    fa_data  = fpi_analysis
    daily    = fpi_raw.get("daily", {}) or {}
    sector_c = fpi_raw.get("sector", {}) or {}

    fpi_cols = st.columns(4)
    sentiment_s = fa_data.get("sentiment","Neutral")
    s_var = "green" if "Bull" in sentiment_s else "red" if "Bear" in sentiment_s else "yellow"
    confl = fa_data.get("confluence","—")
    c_var = "green" if confl=="Aligned" else "yellow"

    with fpi_cols[0]:
        st.markdown(f'<div class="analysis-card" style="text-align:center;"><h4>Sentiment</h4><p>{badge(sentiment_s, s_var)}</p></div>', unsafe_allow_html=True)
    with fpi_cols[1]:
        st.markdown(f'<div class="analysis-card" style="text-align:center;"><h4>Confluence</h4><p>{badge(confl, c_var)}</p></div>', unsafe_allow_html=True)
    with fpi_cols[2]:
        fii_sig = fa_data.get("fii_daily_signal","—")
        fii_v   = "green" if "Buyer" in fii_sig else "red"
        st.markdown(f'<div class="analysis-card" style="text-align:center;"><h4>FII Daily</h4><p>{badge(fii_sig, fii_v)}</p></div>', unsafe_allow_html=True)
    with fpi_cols[3]:
        dii_sig = fa_data.get("dii_daily_signal","—")
        dii_v   = "green" if "Buyer" in dii_sig else "red"
        st.markdown(f'<div class="analysis-card" style="text-align:center;"><h4>DII Daily</h4><p>{badge(dii_sig, dii_v)}</p></div>', unsafe_allow_html=True)

    # Daily numbers table
    if daily:
        fii_d = daily.get("fii", {})
        dii_d = daily.get("dii", {})
        daily_df = pd.DataFrame({
            "Category": ["FII", "DII"],
            "Buy (₹ Cr)":  [f"₹{fii_d.get('buy_cr',0):,.1f}", f"₹{dii_d.get('buy_cr',0):,.1f}"],
            "Sell (₹ Cr)": [f"₹{fii_d.get('sell_cr',0):,.1f}", f"₹{dii_d.get('sell_cr',0):,.1f}"],
            "Net (₹ Cr)":  [f"₹{fii_d.get('net_cr',0):,.1f}", f"₹{dii_d.get('net_cr',0):,.1f}"],
            "Signal":      [fii_d.get("signal","—"), dii_d.get("signal","—")],
        })
        st.markdown('<div class="section-header">Daily FII / DII Numbers</div>', unsafe_allow_html=True)
        st.dataframe(daily_df, use_container_width=True, hide_index=True)

    # Sector context
    buying_sectors  = sector_c.get("buying_sectors", [])
    selling_sectors = sector_c.get("selling_sectors", [])
    if buying_sectors or selling_sectors:
        bs_col, ss_col = st.columns(2)
        with bs_col:
            st.markdown('<div class="section-header" style="color:#34d399;border-left-color:#34d399;">🟢 Buying Sectors (FPI)</div>', unsafe_allow_html=True)
            if buying_sectors:
                buy_df = pd.DataFrame([
                    {"Sector": s["sector"], "Net (₹ Cr)": f"₹{s['net_inr']:,.1f}", "Signal": s.get("signal",""), "Momentum": s.get("momentum","")}
                    for s in buying_sectors
                ])
                st.dataframe(buy_df, use_container_width=True, hide_index=True)
        with ss_col:
            st.markdown('<div class="section-header" style="color:#f87171;border-left-color:#f87171;">🔴 Selling Sectors (FPI)</div>', unsafe_allow_html=True)
            if selling_sectors:
                sell_df = pd.DataFrame([
                    {"Sector": s["sector"], "Net (₹ Cr)": f"₹{s['net_inr']:,.1f}", "Signal": s.get("signal",""), "Momentum": s.get("momentum","")}
                    for s in selling_sectors
                ])
                st.dataframe(sell_df, use_container_width=True, hide_index=True)

    # Sector impact
    si = fa_data.get("sector_impact", {})
    if si:
        st.markdown('<div class="section-header">🎯 Sector Impact on This Stock</div>', unsafe_allow_html=True)
        si_cols = st.columns(3)
        with si_cols[0]:
            st.markdown(f'<div class="analysis-card" style="text-align:center;"><h4>Sector</h4><p>{badge(si.get("sector_name","—"), "blue")}</p></div>', unsafe_allow_html=True)
        with si_cols[1]:
            sec_sig = si.get("sector_signal","—")
            sec_v   = "green" if "Buy" in sec_sig else "red" if "Sell" in sec_sig else "yellow"
            st.markdown(f'<div class="analysis-card" style="text-align:center;"><h4>Sector Signal</h4><p>{badge(sec_sig, sec_v)}</p></div>', unsafe_allow_html=True)
        with si_cols[2]:
            st.markdown(f'<div class="analysis-card" style="text-align:center;"><h4>Implication</h4><p style="font-size:0.85rem;color:#94a3b8;">{si.get("implication","—")}</p></div>', unsafe_allow_html=True)

    render_key_points(fa_data.get("key_points", []))
    render_summary_card(fa_data.get("summary", "No summary available."))


# ── TAB 5: RELATIVE STRENGTH ─────────────────────────────────────────────────
with tab5:
    st.markdown('<div class="section-header">Relative Strength vs Benchmarks</div>', unsafe_allow_html=True)
    ra = rel_analysis

    r_cols = st.columns(3)
    momentum_str = ra.get("momentum","—")
    mom_var = "green" if "Strong" in momentum_str else "yellow" if "Moderate" in momentum_str else "red"
    market_view_str = ra.get("market_view","—")
    mv_var = "green" if "Outperform" in market_view_str else "red" if "Under" in market_view_str else "yellow"
    r_conf_str = ra.get("confidence","—")
    r_conf_var = "green" if r_conf_str=="High" else "yellow" if r_conf_str=="Medium" else "gray"

    with r_cols[0]:
        st.markdown(f'<div class="analysis-card" style="text-align:center;"><h4>Momentum</h4><p>{badge(momentum_str, mom_var)}</p></div>', unsafe_allow_html=True)
    with r_cols[1]:
        st.markdown(f'<div class="analysis-card" style="text-align:center;"><h4>Market View</h4><p>{badge(market_view_str, mv_var)}</p></div>', unsafe_allow_html=True)
    with r_cols[2]:
        st.markdown(f'<div class="analysis-card" style="text-align:center;"><h4>Confidence</h4><p>{badge(r_conf_str, r_conf_var)}</p></div>', unsafe_allow_html=True)

    render_key_points(ra.get("signals", []))
    render_summary_card(ra.get("summary", "No summary available."))

    with st.expander("📄 Raw Relative Strength Data"):
        raw = r.get("relative_data", "")
        st.code(str(raw)[:3000] if raw else "No raw data", language="text")


st.divider()

# ═══════════════════════════════════════════════════════════════════════════════
# FINAL REPORT
# ═══════════════════════════════════════════════════════════════════════════════

st.markdown('<div class="section-header">🤖 AI Research Report</div>', unsafe_allow_html=True)
with st.expander(f"📋 Full Report — {symbol}", expanded=True):
    if report:
        st.markdown(f'<div class="report-box">{report}</div>', unsafe_allow_html=True)
    else:
        st.info("Report not available.")

st.markdown("""
<div style="text-align:center;padding:40px 0 20px 0;color:#334155;font-size:0.75rem;">
    FinSight India · AI-Powered Research · Not investment advice · Data from NSE
</div>
""", unsafe_allow_html=True)
