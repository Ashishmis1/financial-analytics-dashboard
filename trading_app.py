import streamlit as st

st.set_page_config(
    page_title="Financial Data Analytics",
    page_icon="📊",
    layout="wide"
)

st.title("Financial Data Analytics Dashboard 📊")
st.header("Comprehensive Performance, Risk, and Diagnostic Analysis for Indian & Global Equities.")

col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.image("app.jpg", use_container_width=True)

st.markdown("---")

st.markdown("### 📊 Core Analytical Capabilities:")

st.markdown("#### 1️⃣ Diagnostic Stock Analysis")
st.write(
    "Extract live market data via API, calculate key business KPIs (Market Cap, P/E Ratio, ROE), "
    "and generate automated plain-English analyst insights — including trend signals, momentum analysis, "
    "52-week context, and a Fundamental Health Verdict (Strong / Neutral / Weak). "
    "Supports NSE/BSE Indian stocks (e.g. RELIANCE.NS, TCS.NS) and global tickers."
)

st.markdown("#### 2️⃣ Comparative Market Benchmarking")
st.write(
    "Run an automated ETL (Extract → Transform → Load) pipeline to pull stock and index data via API, "
    "store it in a SQLite database, and compare cumulative returns against major benchmarks "
    "like Nifty 50 (^NSEI) or BSE Sensex (^BSESN). "
    "Answers the key analyst question: 'Is this stock performing well, or just riding the market wave?'"
)

st.markdown("#### 3️⃣ Sector Peer Comparison")
st.write(
    "Compare up to 3 stocks within the same sector side-by-side — normalised returns, volatility, "
    "and a plain-English verdict on which stock delivered the best risk-adjusted performance. "
    "Example: TCS vs Infosys vs Wipro — which IT stock was the smarter bet in 2025?"
)

st.markdown("---")
st.caption("Data sourced from Yahoo Finance API. For educational and portfolio demonstration purposes only. Not financial advice.")