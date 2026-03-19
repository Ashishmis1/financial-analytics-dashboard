import streamlit as st
import pandas as pd
import yfinance as yf
import datetime
import pandas_ta as pta

from pages.utils.plotly_figure import candlestick, RSI, MACD, close_chart, Moving_average


def format_indian_currency(number):
    """
    Converts a raw number (in rupees) into a human-readable Indian format.
    e.g. 18739768600000 → ₹ 18.74 Lakh Cr
    This is how CNBC India and Bloomberg India display market caps.
    """
    if not number or number == 0:
        return "N/A"
    crore = number / 10_000_000  
    if crore >= 1_00_000:        
        return f"₹ {crore / 1_00_000:.2f} Lakh Cr"
    elif crore >= 1_000:
        return f"₹ {crore / 1_000:.2f} Thousand Cr"
    elif crore >= 1:
        return f"₹ {crore:.2f} Cr"
    else:
        return f"₹ {number:,.0f}"


st.set_page_config(page_title="Diagnostic Analysis", page_icon="📈", layout="wide")
st.title("📈 Diagnostic Stock Analysis")
st.caption("Extract → Analyse → Interpret. Automated KPIs and plain-English insights for Indian & global stocks.")


col1, col2, col3 = st.columns(3)
today = datetime.date.today()

with col1:
    ticker = st.text_input("Stock Ticker (Use .NS for NSE stocks)", "RELIANCE.NS")
with col2:
    start_date = st.date_input("Start Date", datetime.date(today.year - 1, today.month, today.day))
with col3:
    end_date = st.date_input("End Date", datetime.date(today.year, today.month, today.day))

st.subheader(f"Analyzing: {ticker}")


try:
    stock = yf.Ticker(ticker)
    data = stock.history(start=start_date, end=end_date)
    info = stock.info
    if data.empty:
        st.error("❌ No data found. Please check the ticker symbol. For NSE stocks, add .NS (e.g. TCS.NS)")
        st.stop()
except Exception as e:
    st.error(f"Error fetching data: {e}")
    st.stop()


with st.expander("🔍 Company Overview"):
    st.write(info.get('longBusinessSummary', 'Summary not available.'))
    st.write(f"**Sector:** {info.get('sector', 'N/A')} | **Industry:** {info.get('industry', 'N/A')}")

st.markdown("---")


st.markdown("### 📊 Key Financial Metrics")
st.caption("These are the core numbers every analyst checks before forming a view on a stock.")

col1, col2, col3, col4 = st.columns(4)

market_cap   = info.get("marketCap", 0)
revenue      = info.get("totalRevenue", 0)
pe_ratio     = info.get("trailingPE", None)
roe          = info.get("returnOnEquity", None)
debt_equity  = info.get("debtToEquity", None)
profit_margin = info.get("profitMargins", None)

col1.metric(
    "Market Cap",
    format_indian_currency(market_cap),
    help="Total market value of the company. Market Cap = Share Price × Total Shares."
)
col2.metric(
    "Total Revenue",
    format_indian_currency(revenue),
    help="Total income earned by the company from its business operations."
)
col3.metric(
    "P/E Ratio",
    f"{round(pe_ratio, 2)}" if pe_ratio else "N/A",
    help="Price-to-Earnings Ratio. Shows how much investors pay per ₹1 of profit. Lower = cheaper. Above 40 is generally expensive."
)
col4.metric(
    "Return on Equity (ROE)",
    f"{round(roe * 100, 2)}%" if roe else "N/A",
    help="How efficiently the company uses shareholder money to generate profit. Above 15% is considered strong."
)

st.markdown("---")

st.markdown("### 🛡️ Fundamental Health Verdict")
st.caption(
    "Think of this like a health checkup for a company. We check 4 key vitals — "
    "valuation (P/E), profitability (ROE), debt level (Debt/Equity), and profit margin. "
    "A doctor doesn't just look at one number; neither should an analyst."
)

score = 0
green_flags = []
red_flags = []


if pe_ratio and 0 < pe_ratio < 30:
    score += 1
    green_flags.append("✅ **Attractive Valuation** — P/E below 30 means the stock is not overpriced relative to its earnings.")
elif pe_ratio and pe_ratio >= 30:
    red_flags.append(f"🔴 **Expensive Valuation** — P/E of {round(pe_ratio,1)} is high. Investors are paying a premium, which increases risk.")
else:
    red_flags.append("⚠️ **P/E Not Available** — Could be a loss-making company or data unavailable.")


if roe and roe > 0.15:
    score += 1
    green_flags.append(f"✅ **Strong Profitability** — ROE of {round(roe*100,1)}% means the company generates good returns on shareholder money. (Benchmark: >15%)")
elif roe and roe > 0:
    red_flags.append(f"🟡 **Moderate Profitability** — ROE of {round(roe*100,1)}% is positive but below the 15% benchmark. Room for improvement.")
else:
    red_flags.append("🔴 **Weak/Negative ROE** — Company may not be generating returns for shareholders.")


if debt_equity is not None:
    if debt_equity < 50:
        score += 1
        green_flags.append(f"✅ **Low Debt** — Debt/Equity of {round(debt_equity,1)} means the company is not heavily borrowed. Financially stable.")
    elif debt_equity < 150:
        red_flags.append(f"🟡 **Moderate Debt** — Debt/Equity of {round(debt_equity,1)}. Manageable but worth monitoring.")
    else:
        red_flags.append(f"🔴 **High Debt** — Debt/Equity of {round(debt_equity,1)} is high. Company carries significant financial risk.")
else:
    red_flags.append("⚠️ **Debt/Equity Not Available.**")


if profit_margin and profit_margin > 0.10:
    score += 1
    green_flags.append(f"✅ **Healthy Profit Margins** — {round(profit_margin*100,1)}% margin means the company keeps good profit per ₹100 of revenue. (Benchmark: >10%)")
elif profit_margin and profit_margin > 0:
    red_flags.append(f"🟡 **Thin Margins** — {round(profit_margin*100,1)}% profit margin. Low buffer against rising costs.")
else:
    red_flags.append("🔴 **Negative/No Profit Margin** — Company may be operating at a loss.")


if score >= 3:
    verdict_color = "success"
    verdict_text  = "🟢 FUNDAMENTALLY STRONG"
    verdict_explain = "This company passes 3 or more of our 4 financial health checks. Strong fundamentals generally reduce investment risk."
elif score == 2:
    verdict_color = "warning"
    verdict_text  = "🟡 NEUTRAL — WATCH CAREFULLY"
    verdict_explain = "Mixed signals. Some positives, some concerns. Not an automatic buy or sell — needs closer monitoring."
else:
    verdict_color = "error"
    verdict_text  = "🔴 FUNDAMENTALLY WEAK / HIGH RISK"
    verdict_explain = "Fails most fundamental checks. High risk investment. Approach with caution."

col_v1, col_v2 = st.columns([1, 2])
with col_v1:
    if verdict_color == "success":
        st.success(f"**VERDICT: {verdict_text}**\n\n{verdict_explain}")
    elif verdict_color == "warning":
        st.warning(f"**VERDICT: {verdict_text}**\n\n{verdict_explain}")
    else:
        st.error(f"**VERDICT: {verdict_text}**\n\n{verdict_explain}")

with col_v2:
    if green_flags:
        st.markdown("**Green Flags:**")
        for flag in green_flags:
            st.markdown(flag)
    if red_flags:
        st.markdown("**Red Flags / Watch Points:**")
        for flag in red_flags:
            st.markdown(flag)

st.markdown("---")


st.markdown("### 🤖 Automated Analyst Insights")
st.caption(
    "This section answers the two questions every good analyst must answer: "
    "**'So what does this data mean?'** and **'Now what should we do about it?'** "
    "Written in plain English — no finance jargon required."
)

with st.spinner("Generating business signals based on current technical indicators..."):

   
    current_price  = float(data['Close'].iloc[-1])
    sma_50         = float(data['Close'].rolling(window=50).mean().iloc[-1]) if len(data) >= 50 else current_price
    sma_200        = float(data['Close'].rolling(window=200).mean().iloc[-1]) if len(data) >= 200 else None

    week_52_high   = float(data['High'].max())
    week_52_low    = float(data['Low'].min())
    pct_from_high  = ((current_price - week_52_high) / week_52_high) * 100
    pct_from_low   = ((current_price - week_52_low) / week_52_low) * 100

    data['RSI']    = pta.rsi(data['Close'])
    rsi_today      = float(data['RSI'].iloc[-1]) if not pd.isna(data['RSI'].iloc[-1]) else 50.0

    avg_vol_10     = float(data['Volume'].tail(10).mean())
    avg_vol_3m     = float(data['Volume'].tail(63).mean())
    vol_vs_avg     = ((avg_vol_10 - avg_vol_3m) / avg_vol_3m) * 100 if avg_vol_3m > 0 else 0

    currency_symbol = "₹" if ".NS" in ticker or ".BO" in ticker else "$"

   
    trend_direction = "above" if current_price > sma_50 else "below"
    trend_signal    = "bullish 🟢" if current_price > sma_50 else "bearish 🔴"
    st.markdown(
        f"- **Trend Analysis:** {ticker} is currently trading at "
        f"**{currency_symbol}{current_price:,.2f}**. "
        f"It is trading **{trend_direction}** its 50-day moving average "
        f"({currency_symbol}{sma_50:,.2f}), indicating a short-term **{trend_signal}** trend. "
        f"*(The 50-day moving average is simply the average price over the last 50 trading days — "
        f"it smooths out daily noise and shows the underlying direction.)*"
    )

  
    if pct_from_high < -20:
        week52_note = (
            f"  *(A stock far below its 52-week high can indicate either a buying opportunity "
            f"or a fundamentally deteriorating business — always check fundamentals before concluding.)*"
        )
    elif pct_from_high < -5:
        week52_note = "  *(Mild pullback from peak — could be a healthy correction or early warning sign.)*"
    else:
        week52_note = "  *(Trading near its annual peak — strong price momentum.)*"

    st.markdown(
        f"- **52-Week Context:** The stock is **{abs(pct_from_high):.1f}% below** its 52-week high "
        f"of {currency_symbol}{week_52_high:,.2f} and **{pct_from_low:.1f}% above** its 52-week low "
        f"of {currency_symbol}{week_52_low:,.2f}. "
        + week52_note
    )

    
    if rsi_today > 70:
        rsi_label   = "Overbought 🔴"
        rsi_explain = "Too many buyers have pushed the price up quickly. Often signals a short-term pullback ahead."
        rsi_action  = "Caution — avoid buying at current levels. Wait for RSI to cool below 70."
    elif rsi_today < 30:
        rsi_label   = "Oversold 🟢"
        rsi_explain = "Sellers have pushed the price down sharply. Often signals a potential bounce or recovery."
        rsi_action  = "Potential entry opportunity — but confirm with fundamentals before buying."
    else:
        rsi_label   = "Neutral Zone ⚪"
        rsi_explain = "No extreme buying or selling pressure detected. Price momentum is balanced."
        rsi_action  = "Monitor for RSI breaking above 70 (overbought) or below 30 (oversold) for a clearer signal."

    st.markdown(
        f"- **Momentum (RSI):** Current RSI is **{rsi_today:.1f}** — **{rsi_label}**. "
        f"*(RSI = Relative Strength Index, a 0–100 score measuring buying/selling momentum. "
        f"Above 70 = overbought, below 30 = oversold, 30–70 = neutral.)* "
        f"{rsi_explain} **Analyst Action:** {rsi_action}"
    )

   
    vol_direction = "above" if vol_vs_avg > 0 else "below"
    vol_color     = "🟢" if vol_vs_avg > 10 else ("🔴" if vol_vs_avg < -10 else "⚪")
    st.markdown(
        f"- **Volume Signal {vol_color}:** Average trading volume over the last 10 days is "
        f"**{abs(vol_vs_avg):.1f}% {vol_direction}** the 3-month average. "
        f"*(Volume = number of shares traded per day. High volume during a price rise = strong conviction. "
        f"Low volume = weak conviction — the move may not last.)*"
    )

  
    st.markdown("---")
    st.markdown("#### 🎯 The Bottom Line — So What? Now What?")

    if current_price > sma_50 and rsi_today < 70 and score >= 3:
        conclusion_type = "success"
        conclusion = (
            f"**{ticker} presents a positive short-term and fundamental picture.** "
            f"The price is in an uptrend (above 50-day average), momentum is healthy (RSI not overbought), "
            f"and the business fundamentals score {score}/4. "
            f"**Analyst Action: Consider this a watchlist candidate for accumulation on dips.**"
        )
    elif rsi_today > 70:
        conclusion_type = "warning"
        conclusion = (
            f"**{ticker} is technically overextended in the short term.** "
            f"RSI above 70 means the stock has risen quickly and buyers may be exhausted. "
            f"Even if the business is good, the *price* may be ahead of *value* right now. "
            f"**Analyst Action: Avoid new entry. Wait for RSI to cool below 65 before reconsidering.**"
        )
    elif current_price < sma_50 and score <= 1:
        conclusion_type = "error"
        conclusion = (
            f"**{ticker} shows weakness on both price and fundamentals.** "
            f"Trading below the 50-day average signals bearish short-term momentum, "
            f"and fundamental checks raise concerns (score {score}/4). "
            f"**Analyst Action: High caution. This is not an entry point. Revisit when price reclaims the 50-day average.**"
        )
    elif current_price < sma_50 and score >= 2:
        conclusion_type = "warning"
        conclusion = (
            f"**{ticker} has good fundamentals but is in a short-term price downtrend.** "
            f"This is a classic 'fundamentally good but technically weak' scenario — common during broader market corrections. "
            f"**Analyst Action: Add to watchlist. Wait for price to reclaim the 50-day average as a confirmation signal.**"
        )
    else:
        conclusion_type = "info"
        conclusion = (
            f"**{ticker} is in a neutral zone with mixed signals.** "
            f"No strong buy or sell case based on current data. "
            f"**Analyst Action: Monitor RSI and volume for a directional breakout. No urgent action required.**"
        )

    if conclusion_type == "success":
        st.success(conclusion)
    elif conclusion_type == "warning":
        st.warning(conclusion)
    elif conclusion_type == "error":
        st.error(conclusion)
    else:
        st.info(conclusion)

st.markdown("---")

st.markdown("### 📈 Interactive Technical Charts")
st.caption(
    "Technical charts show historical price patterns. "
    "They help analysts spot trends, support/resistance levels, and entry/exit points. "
    "Use the controls below to customise your view."
)

c1, c2, c3 = st.columns([2, 2, 2])
period_options = {
    '1 Month': '1mo',
    '3 Months': '3mo',
    '6 Months': '6mo',
    '1 Year': '1y',
    '5 Years': '5y'
}
with c1:
    selected_period = st.selectbox("Select Time Period", options=list(period_options.keys()), index=3)
with c2:
    chart_type = st.radio("Chart Type", ('Candle', 'Line'), horizontal=True)
with c3:
    indicators = st.selectbox(
        "Secondary Indicator",
        ('None', 'RSI', 'MACD', 'Moving Average'),
        help=(
            "RSI = momentum score (0-100). "
            "MACD = trend-following signal. "
            "Moving Average = smoothed price trend line."
        )
    )

chart_data = yf.Ticker(ticker).history(period=period_options[selected_period])

if not chart_data.empty:
    if chart_type == 'Candle':
        st.plotly_chart(
            candlestick(chart_data, period_options[selected_period]),
            use_container_width=True
        )
        st.caption(
            "📖 **Reading a candlestick:** Each candle = one trading day. "
            "Green candle = price closed higher than it opened (bullish). "
            "Red candle = price closed lower than it opened (bearish). "
            "The thin lines (wicks) show the day's highest and lowest prices."
        )
    else:
        st.plotly_chart(
            close_chart(chart_data, period_options[selected_period]),
            use_container_width=True
        )

    if indicators == 'RSI':
        st.plotly_chart(RSI(chart_data, period_options[selected_period]), use_container_width=True)
        st.caption(
            "📖 **Reading RSI:** The orange line is RSI (0–100). "
            "Red dashed line at 70 = overbought zone (price may be too high, pullback risk). "
            "Green dashed line at 30 = oversold zone (price may be too low, bounce opportunity). "
            "Best signals happen when RSI crosses these lines."
        )
    elif indicators == 'MACD':
        st.plotly_chart(MACD(chart_data, period_options[selected_period]), use_container_width=True)
        st.caption(
            "📖 **Reading MACD:** When the orange MACD line crosses above the red signal line = bullish signal. "
            "When it crosses below = bearish signal. "
            "MACD is best used to confirm trend direction, not predict exact price."
        )
    elif indicators == 'Moving Average':
        st.plotly_chart(Moving_average(chart_data, period_options[selected_period]), use_container_width=True)
        st.caption(
            "📖 **Reading Moving Average:** The purple line (SMA 50) is the average price over the last 50 days. "
            "When price is above this line, the trend is up. When below, the trend is down. "
            "It smooths out the daily noise and shows the real direction."
        )

st.markdown("---")


st.markdown("### 🗄️ Historical Data Export")
st.caption(
    "Preview the last 10 days of trading data below. "
    "Download the full dataset to analyse in Power BI, Tableau, or Excel — "
    "this is the standard analyst workflow: Python extracts and cleans, BI tool visualises."
)


export_data = data.copy()
export_data['RSI'] = pta.rsi(export_data['Close'])
export_data['SMA_50'] = export_data['Close'].rolling(50).mean()

display_df = export_data.tail(10).sort_index(ascending=False).round(2)
st.dataframe(display_df, use_container_width=True)

csv = export_data.to_csv().encode('utf-8')
st.download_button(
    label="📥 Download Cleaned Data (CSV) — for Power BI / Tableau / Excel",
    data=csv,
    file_name=f'{ticker}_cleaned_data.csv',
    mime='text/csv'
)