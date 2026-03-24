import streamlit as st

st.set_page_config(page_title="FinSight India", page_icon="🇮🇳", layout="wide")

st.title("🇮🇳 FinSight India")
st.write("AI-powered Stock Research")

# ── Sidebar ──────────────────────────────
with st.sidebar:
    st.title("🔍 Search")
    popular = ["TCS", "RELIANCE", "INFY", "HDFCBANK", "WIPRO", "SBIN"]
    cols = st.columns(2)
    for i, stock in enumerate(popular):
        if cols[i % 2].button(stock, use_container_width=True):
            symbol = stock
            # symbol = st.text_input("Enter NSE Symbol", value="TCS", placeholder="e.g. RELIANCE, INFY")
            run = st.button("Run Analysis", type="primary", use_container_width=True)

    st.divider()
    st.caption("Popular Stocks")

    # ── Dummy data for now ────────────────────
symbol = "TORNTPHARM"
final_score = 62.0
signal = "BUY"
confidence = 24.0
scores = {
    "Fundamental": 70,
    "Technical": 40,
    "News": 60,
    "FPI/FII": 40,
    "Relative Strength": 100,
}

st.subheader(f"📊 {symbol} — Stock Analysis")

col1, col2, col3, col4 = st.columns(4)
col1.metric("Current Price", "₹4,270")
col2.metric("Final Score", f"{final_score}/100")
col3.metric("Confidence", f"{confidence}%")

# signal with color
signal_color = "green" if signal == "BUY" else "red" if signal == "SELL" else "orange"
col4.markdown(f"### :{signal_color}[**{signal}**]")

st.divider()

# ── Score Bars ────────────────────────────
st.subheader("📈 Score Breakdown")
for name, score in scores.items():
    col_a, col_b = st.columns([1, 4])
    col_a.write(f"**{name}**")
    col_b.progress(score)

