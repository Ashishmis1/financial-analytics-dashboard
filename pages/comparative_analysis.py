import streamlit as st
import yfinance as yf
import pandas as pd
import sqlite3
import plotly.graph_objects as go

st.set_page_config(page_title="Comparative Benchmarking", page_icon="⚖️", layout="wide")

st.title("⚖️ Comparative Market Analysis")
st.caption(
    "Two types of comparison every equity analyst runs: "
    "(1) How did this stock perform vs the overall market? "
    "(2) How did this stock perform vs its direct competitors?"
)


tab1, tab2 = st.tabs([
    "📊 Stock vs Market Benchmark (ETL Pipeline)",
    "🏆 Sector Peer Comparison (TCS vs Infy vs Wipro)"
])



with tab1:
    st.markdown("### Stock vs Market Benchmark")
    st.write(
        "Answers the key analyst question: **'Is this stock performing well, or just riding the market wave?'** "
        "If the Nifty 50 is up 15% and your stock is up 10%, you've actually *underperformed* — "
        "you'd have been better off buying an index fund. This chart makes that comparison visual and instant."
    )
    st.markdown("---")

    col1, col2, col3 = st.columns(3)
    with col1:
        stock_ticker = st.text_input("Target Stock Ticker", "TCS.NS")
    with col2:
        benchmark_ticker = st.selectbox(
            "Market Benchmark",
            ["^NSEI (Nifty 50)", "^BSESN (BSE Sensex)", "^GSPC (S&P 500)"]
        )
        bench_symbol = benchmark_ticker.split(" ")[0]
        bench_name   = benchmark_ticker.split(" ")[1].replace("(", "").replace(")", "")
    with col3:
        timeframe = st.selectbox("Timeframe", ["6mo", "1y", "2y", "5y"], index=1)

    st.markdown("---")

    if st.button("🚀 Run ETL Pipeline & Analyze", type="primary", key="etl_btn"):
        with st.spinner("Extracting data via API → Transforming returns → Loading to SQLite database..."):
            try:
                
                stock_data = yf.Ticker(stock_ticker).history(period=timeframe)
                bench_data = yf.Ticker(bench_symbol).history(period=timeframe)

                if stock_data.empty or bench_data.empty:
                    st.error("Failed to fetch data. Please check the ticker symbols.")
                    st.stop()

                df = pd.DataFrame()
                df[stock_ticker] = stock_data['Close']
                df[bench_symbol] = bench_data['Close']
                df = df.dropna()

                df[f'{stock_ticker}_%_Return'] = (
                    (df[stock_ticker] - df[stock_ticker].iloc[0]) / df[stock_ticker].iloc[0]
                ) * 100
                df[f'{bench_symbol}_%_Return'] = (
                    (df[bench_symbol] - df[bench_symbol].iloc[0]) / df[bench_symbol].iloc[0]
                ) * 100

                df = df.reset_index()
                df['Date'] = df['Date'].dt.strftime('%Y-%m-%d')

               
                conn = sqlite3.connect('historical_data.db')
                df.to_sql('comparative_returns', conn, if_exists='replace', index=False)
                conn.close()

               
                conn = sqlite3.connect('historical_data.db')
                query_df = pd.read_sql_query("SELECT * FROM comparative_returns", conn)
                conn.close()

                st.success("✅ ETL Pipeline Complete: Data extracted via API → transformed → loaded into SQLite database.")

                
                st.markdown("### 📈 Cumulative Return Comparison")
                st.caption(
                    "Both lines start at 0% on Day 1. This normalisation lets you fairly compare "
                    "a ₹3,000 stock against a 22,000-point index. The gap between the lines = "
                    "the stock's out/underperformance vs the market."
                )

                stock_ret  = query_df[f'{stock_ticker}_%_Return'].iloc[-1]
                bench_ret  = query_df[f'{bench_symbol}_%_Return'].iloc[-1]
                diff       = stock_ret - bench_ret
                line_color = '#22c55e' if diff >= 0 else '#ef4444'

                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=query_df['Date'], y=query_df[f'{stock_ticker}_%_Return'],
                    mode='lines', name=stock_ticker,
                    line=dict(width=2.5, color=line_color)
                ))
                fig.add_trace(go.Scatter(
                    x=query_df['Date'], y=query_df[f'{bench_symbol}_%_Return'],
                    mode='lines', name=bench_name,
                    line=dict(width=2, color='#f59e0b', dash='dash')
                ))
                fig.add_hline(y=0, line_dash="dot", line_color="gray", line_width=1)
                fig.update_layout(
                    height=420, yaxis_title="Cumulative Return (%)",
                    hovermode="x unified", plot_bgcolor='white',
                    paper_bgcolor='#f8fafd', margin=dict(l=0, r=20, t=20, b=0)
                )
                fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='LightGray')
                st.plotly_chart(fig, use_container_width=True)

                
                st.markdown("### 🤖 Automated Comparative Insight")

                if diff > 5:
                    st.success(
                        f"**Outperformance ✅** — Over this period, **{stock_ticker}** returned "
                        f"**{stock_ret:.2f}%**, beating **{bench_name}** ({bench_ret:.2f}%). "
                        f"Outperformance: **+{diff:.2f}%**. "
                        f"This means an investor in {stock_ticker} did better than simply buying the index. "
                        f"*(Positive alpha — this is what active stock-pickers aim for.)*"
                    )
                elif diff >= 0:
                    st.info(
                        f"**Marginal Outperformance ⚪** — {stock_ticker} returned {stock_ret:.2f}% vs "
                        f"{bench_name}'s {bench_ret:.2f}% (+{diff:.2f}% alpha). "
                        f"Barely beat the market — not enough to justify the additional stock-specific risk "
                        f"over a safer index fund."
                    )
                else:
                    st.warning(
                        f"**Underperformance ⚠️** — **{stock_ticker}** returned **{stock_ret:.2f}%**, "
                        f"lagging behind **{bench_name}** ({bench_ret:.2f}%). "
                        f"Underperformance: **{diff:.2f}%**. "
                        f"An investor would have earned more by simply investing in a Nifty 50 index fund "
                        f"instead of picking this stock. "
                        f"*(Negative alpha — the stock destroyed value relative to the market.)*"
                    )

                # ── RAW SQL TABLE ─────────────────────────────────
                with st.expander("🔍 View Raw Database Output (SQL Query Result)"):
                    st.caption("This table is the direct output of: SELECT * FROM comparative_returns")
                    st.dataframe(query_df, use_container_width=True)

            except Exception as e:
                st.error(f"ETL Pipeline Error: {e}")



with tab2:
    st.markdown("### Sector Peer Comparison")
    st.write(
        "**The analyst's real question isn't just 'is this stock up?' — it's 'is it better than alternatives?'** "
        "If TCS is down 5% but Infosys is down 15%, TCS is actually a strong relative performer. "
        "This tab compares 3 stocks in the same sector so you can spot the winner."
    )
    st.markdown("---")

    
    sector_presets = {
        "🖥️ Indian IT (TCS vs Infosys vs Wipro)":         ["TCS.NS",      "INFY.NS",     "WIPRO.NS"],
        "🏦 Indian Banking (HDFC vs ICICI vs Kotak)":     ["HDFCBANK.NS", "ICICIBANK.NS","KOTAKBANK.NS"],
        "⚡ Indian Energy (Reliance vs ONGC vs NTPC)":     ["RELIANCE.NS", "ONGC.NS",     "NTPC.NS"],
        "🛒 Indian FMCG (HUL vs ITC vs Nestle)":          ["HINDUNILVR.NS","ITC.NS",      "NESTLEIND.NS"],
        "🚗 Indian Auto (Tata Motors vs M&M vs Maruti)":  ["TATAMOTORS.NS","M&M.NS",      "MARUTI.NS"],
        "✏️ Custom (Enter your own tickers)":              [],
    }

    selected_preset = st.selectbox("Choose a Sector to Compare", list(sector_presets.keys()))
    preset_tickers  = sector_presets[selected_preset]

    col1, col2, col3, col4 = st.columns([2, 2, 2, 1])

    if preset_tickers:
        with col1: t1 = st.text_input("Stock 1", preset_tickers[0])
        with col2: t2 = st.text_input("Stock 2", preset_tickers[1])
        with col3: t3 = st.text_input("Stock 3", preset_tickers[2])
    else:
        with col1: t1 = st.text_input("Stock 1 (e.g. TCS.NS)",   "TCS.NS")
        with col2: t2 = st.text_input("Stock 2 (e.g. INFY.NS)",  "INFY.NS")
        with col3: t3 = st.text_input("Stock 3 (e.g. WIPRO.NS)", "WIPRO.NS")

    with col4:
        compare_period = st.selectbox("Period", ["3mo", "6mo", "1y", "2y"], index=2)

    if st.button("🔍 Compare Stocks", key="peer_btn"):
        tickers_to_compare = [t for t in [t1, t2, t3] if t.strip()]
        if len(tickers_to_compare) < 2:
            st.error("Please enter at least 2 stock tickers to compare.")
        else:
            with st.spinner("Fetching and comparing data..."):
                try:
                    
                    all_data   = {}
                    raw_close  = {}
                    colors     = ['#3b82f6', '#f59e0b', '#22c55e']

                    for tk in tickers_to_compare:
                        hist = yf.Ticker(tk.strip()).history(period=compare_period)
                        if not hist.empty:
                            pct_returns = (
                                (hist['Close'] - hist['Close'].iloc[0]) / hist['Close'].iloc[0]
                            ) * 100
                            all_data[tk]  = pct_returns
                            raw_close[tk] = hist['Close']

                    if not all_data:
                        st.error("Could not fetch data for any of the entered tickers.")
                        st.stop()

                    returns_df = pd.DataFrame(all_data).dropna()
                    returns_df.index = returns_df.index.strftime('%Y-%m-%d')

                    
                    st.markdown("#### 📈 Normalised Return Comparison")
                    st.caption(
                        "All stocks start at 0% on Day 1. This levels the playing field — "
                        "a ₹4,000 stock and a ₹1,500 stock can be compared fairly."
                    )

                    fig1 = go.Figure()
                    for i, (tk, ret_series) in enumerate(returns_df.items()):
                        fig1.add_trace(go.Scatter(
                            x=returns_df.index, y=ret_series,
                            mode='lines', name=tk,
                            line=dict(width=2.5, color=colors[i % len(colors)])
                        ))
                    fig1.add_hline(y=0, line_dash="dot", line_color="gray", line_width=1)
                    fig1.update_layout(
                        height=400, yaxis_title="Cumulative Return (%)",
                        hovermode="x unified", plot_bgcolor='white',
                        paper_bgcolor='#f8fafd', margin=dict(l=0, r=20, t=20, b=0)
                    )
                    fig1.update_yaxes(showgrid=True, gridwidth=1, gridcolor='LightGray')
                    st.plotly_chart(fig1, use_container_width=True)

                   
                    st.markdown("#### 📊 Side-by-Side Performance Metrics")
                    st.caption(
                        "Volatility = how much the daily price swings. "
                        "High return + low volatility = best risk-adjusted performance. "
                        "Sharpe-like ratio = return divided by volatility (higher is better)."
                    )

                    metric_rows = []
                    for tk, ret_series in returns_df.items():
                        close_series   = pd.DataFrame(raw_close[tk])['Close'] if tk in raw_close else None
                        daily_returns  = ret_series.pct_change().dropna() if len(ret_series) > 1 else pd.Series([0])
                        total_ret      = float(ret_series.iloc[-1])
                        volatility     = float(daily_returns.std() * (252 ** 0.5))  # annualised
                        sharpe_approx  = total_ret / (volatility * 100) if volatility > 0 else 0

                        metric_rows.append({
                            "Stock":                 tk,
                            "Total Return (%)":      f"{total_ret:+.2f}%",
                            "Annualised Volatility": f"{volatility*100:.2f}%",
                            "Risk-Adj. Score":       f"{sharpe_approx:.2f}",
                        })

                    metrics_df = pd.DataFrame(metric_rows).set_index("Stock")
                    st.dataframe(metrics_df, use_container_width=True)

                    st.caption(
                        "*(Annualised Volatility = daily price swings scaled to a yearly figure. "
                        "Lower is more stable. Risk-Adj. Score = return per unit of risk — "
                        "higher means better return for the risk taken.)*"
                    )

                   
                    st.markdown("#### 🤖 Automated Peer Comparison Verdict")

                    final_returns = {tk: float(returns_df[tk].iloc[-1]) for tk in returns_df.columns}
                    best_stock    = max(final_returns, key=final_returns.get)
                    worst_stock   = min(final_returns, key=final_returns.get)
                    best_ret      = final_returns[best_stock]
                    worst_ret     = final_returns[worst_stock]
                    spread        = best_ret - worst_ret

                    st.success(
                        f"**Winner: {best_stock}** delivered the highest return of **{best_ret:+.2f}%** "
                        f"over this period — outperforming **{worst_stock}** ({worst_ret:+.2f}%) "
                        f"by **{spread:.2f} percentage points**."
                    )

                    
                    vols = {}
                    for tk, ret_series in returns_df.items():
                        daily_ret = ret_series.pct_change().dropna()
                        vols[tk]  = float(daily_ret.std() * (252 ** 0.5) * 100)

                    lowest_vol_stock = min(vols, key=vols.get)
                    st.info(
                        f"**Most Stable: {lowest_vol_stock}** had the lowest annualised volatility "
                        f"({vols[lowest_vol_stock]:.2f}%), making it the least risky option in this peer group. "
                        f"*(For a risk-averse investor or a conservative portfolio, lower volatility "
                        f"is often preferred even if total return is slightly lower.)*"
                    )

                    if best_stock != lowest_vol_stock:
                        st.warning(
                            f"**Analyst Note:** There is a trade-off here. "
                            f"**{best_stock}** gave better returns but **{lowest_vol_stock}** was more stable. "
                            f"The right choice depends on the investor's risk appetite. "
                            f"A risk-adjusted score helps compare them on equal footing — "
                            f"see the table above."
                        )
                    else:
                        st.success(
                            f"**{best_stock}** is the clear winner on both return AND stability — "
                            f"the strongest risk-adjusted choice in this peer group."
                        )

                except Exception as e:
                    st.error(f"Error during peer comparison: {e}")