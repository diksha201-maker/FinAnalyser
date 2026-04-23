import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import time
from datetime import date, timedelta
import random

# ─────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Stock Market Analytics Hub",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─────────────────────────────────────────────
# CUSTOM CSS — Dark Finance Theme
# ─────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=DM+Sans:wght@300;400;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'DM Sans', sans-serif;
        background-color: #0a0e1a;
        color: #e2e8f0;
    }
    .stApp { background-color: #0a0e1a; }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0f1629 0%, #0a0e1a 100%);
        border-right: 1px solid #1e2d4a;
    }

    /* Metric Cards */
    div[data-testid="metric-container"] {
        background: linear-gradient(135deg, #0f1629 0%, #151f35 100%);
        border: 1px solid #1e3a5f;
        border-radius: 12px;
        padding: 16px;
        box-shadow: 0 4px 24px rgba(0,212,255,0.05);
    }
    div[data-testid="metric-container"] label {
        color: #64748b !important;
        font-size: 0.75rem !important;
        font-family: 'Space Mono', monospace !important;
        letter-spacing: 0.1em;
        text-transform: uppercase;
    }
    div[data-testid="metric-container"] div[data-testid="stMetricValue"] {
        color: #e2e8f0 !important;
        font-family: 'Space Mono', monospace !important;
        font-size: 1.5rem !important;
    }

    /* Headers */
    h1 { font-family: 'Space Mono', monospace !important; color: #00d4ff !important; letter-spacing: -0.02em; }
    h2 { font-family: 'Space Mono', monospace !important; color: #e2e8f0 !important; font-size: 1.1rem !important; }
    h3 { font-family: 'DM Sans', sans-serif !important; color: #94a3b8 !important; }

    /* Tab styling */
    button[data-baseweb="tab"] {
        font-family: 'Space Mono', monospace !important;
        color: #64748b !important;
        font-size: 0.8rem !important;
        letter-spacing: 0.05em;
    }
    button[data-baseweb="tab"][aria-selected="true"] {
        color: #00d4ff !important;
        border-bottom: 2px solid #00d4ff !important;
    }

    /* Selectbox / sliders */
    .stSelectbox > div > div { background-color: #0f1629; border: 1px solid #1e3a5f; border-radius: 8px; }
    .stSlider > div > div > div { background-color: #00d4ff !important; }

    /* Info boxes */
    .insight-box {
        background: linear-gradient(135deg, #0f2a1a, #0a1a10);
        border-left: 3px solid #00ff88;
        border-radius: 8px;
        padding: 12px 16px;
        margin: 8px 0;
        font-size: 0.85rem;
        color: #86efac;
    }
    .warning-box {
        background: linear-gradient(135deg, #2a1a0f, #1a100a);
        border-left: 3px solid #ff6b35;
        border-radius: 8px;
        padding: 12px 16px;
        margin: 8px 0;
        font-size: 0.85rem;
        color: #fdba74;
    }

    /* Section dividers */
    hr { border-color: #1e2d4a !important; }

    /* Live badge */
    .live-badge {
        display: inline-block;
        background: rgba(0,255,136,0.1);
        border: 1px solid #00ff88;
        color: #00ff88;
        font-family: 'Space Mono', monospace;
        font-size: 0.65rem;
        padding: 2px 8px;
        border-radius: 100px;
        letter-spacing: 0.1em;
        animation: pulse 2s infinite;
    }
    @keyframes pulse {
        0%,100% { opacity: 1; }
        50% { opacity: 0.4; }
    }

    /* DataFrame */
    .stDataFrame { border: 1px solid #1e3a5f; border-radius: 10px; }

    /* Page title banner */
    .title-banner {
        background: linear-gradient(90deg, #0f1629, #0a1e3d, #0f1629);
        border: 1px solid #1e3a5f;
        border-radius: 14px;
        padding: 20px 28px;
        margin-bottom: 24px;
        display: flex;
        align-items: center;
        gap: 16px;
    }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# DATA GENERATION
# ─────────────────────────────────────────────
STOCKS = {
    "TRENT": {"name": "Trent Ltd", "sector": "Retail", "base": 1200, "volatility": 0.022, "trend": 0.0012},
    "DMART": {"name": "Avenue Supermarket", "sector": "Retail", "base": 3900, "volatility": 0.015, "trend": 0.0006},
    "REDTAPE": {"name": "Redtape Ltd", "sector": "Footwear", "base": 480, "volatility": 0.025, "trend": 0.0008},
    "SHOPSTOP": {"name": "Shoppers Stop", "sector": "Retail", "base": 720, "volatility": 0.028, "trend": 0.0005},
    "ABFRL": {"name": "Aditya Birla Fashion", "sector": "Fashion", "base": 190, "volatility": 0.030, "trend": 0.0003},
}

FY_RANGES = {
    "FY 2023-2024": (date(2023, 4, 1), date(2024, 3, 31)),
    "FY 2024-2025": (date(2024, 4, 1), date(2025, 3, 31)),
    "FY 2025-2026": (date(2025, 4, 1), date(2026, 3, 31)),
}

@st.cache_data
def generate_stock_data(ticker, start, end, seed=42):
    np.random.seed(seed + hash(ticker) % 100)
    dates = pd.bdate_range(start=start, end=end)
    n = len(dates)
    info = STOCKS[ticker]

    # Simulate realistic OHLCV
    close = [info["base"]]
    for i in range(1, n):
        ret = info["trend"] + info["volatility"] * np.random.randn()
        close.append(close[-1] * (1 + ret))
    close = np.array(close)

    high = close * (1 + np.abs(np.random.normal(0, 0.008, n)))
    low  = close * (1 - np.abs(np.random.normal(0, 0.008, n)))
    open_ = low + (high - low) * np.random.uniform(0.2, 0.8, n)
    volume = np.random.randint(500_000, 5_000_000, n)

    df = pd.DataFrame({
        "Date": dates, "Open": open_, "High": high,
        "Low": low, "Close": close, "Volume": volume
    })
    df["MA7"]  = df["Close"].rolling(7).mean()
    df["MA30"] = df["Close"].rolling(30).mean()
    df["Daily_Return"] = df["Close"].pct_change() * 100
    return df

def get_all_data(fy):
    start, end = FY_RANGES[fy]
    return {t: generate_stock_data(t, start, end) for t in STOCKS}

# ─────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 📊 Dashboard Controls")
    st.markdown("---")

    selected_fy = st.selectbox("📅 Financial Year", list(FY_RANGES.keys()), index=1)
    selected_ticker = st.selectbox(
        "🏢 Select Stock",
        list(STOCKS.keys()),
        format_func=lambda x: f"{x} — {STOCKS[x]['name']}"
    )
    st.markdown("---")
    live_refresh = st.toggle("🔴 Live Simulation", value=False)
    refresh_speed = st.slider("Refresh Interval (sec)", 2, 10, 4) if live_refresh else 4
    st.markdown("---")

    # Portfolio weights
    st.markdown("#### 💼 Portfolio Weights (%)")
    weights = {}
    for t, info in STOCKS.items():
        weights[t] = st.slider(info["name"][:18], 0, 100, 20, key=f"w_{t}")
    total_w = sum(weights.values())
    if total_w != 100:
        st.warning(f"Weights sum = {total_w}% (should be 100%)")
    st.markdown("---")
    st.markdown('<span class="live-badge">● LIVE SIM</span>' if live_refresh else "", unsafe_allow_html=True)
    st.caption("Data is simulated for presentation purposes.")

# ─────────────────────────────────────────────
# TITLE BANNER
# ─────────────────────────────────────────────
st.markdown(f"""
<div class="title-banner">
    <div>
        <h1 style="margin:0; font-size:1.8rem;">📈 Stock Market Analytics Hub</h1>
        <p style="margin:4px 0 0 0; color:#64748b; font-size:0.85rem; font-family:'Space Mono',monospace;">
            Indian Retail & Fashion Sector · {selected_fy} · 5 Stocks Tracked
        </p>
    </div>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# TABS
# ─────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🏠 Market Overview",
    "🔍 Stock Deep Dive",
    "💼 Portfolio Tracker",
    "🔥 Heatmap & Correlation",
    "⚡ Live Simulation"
])

all_data = get_all_data(selected_fy)

# ══════════════════════════════════════════════
# TAB 1: MARKET OVERVIEW
# ══════════════════════════════════════════════
with tab1:
    st.markdown("### 📌 Key Market Indicators")

    cols = st.columns(5)
    for i, (ticker, info) in enumerate(STOCKS.items()):
        df = all_data[ticker]
        start_price = df["Close"].iloc[0]
        end_price   = df["Close"].iloc[-1]
        pct_change  = ((end_price - start_price) / start_price) * 100
        cols[i].metric(
            label=ticker,
            value=f"₹{end_price:,.1f}",
            delta=f"{pct_change:+.2f}%"
        )

    st.markdown("---")

    # Combined Price Trend Chart
    st.markdown("### 📊 Price Trends — All Stocks")
    fig_trend = go.Figure()
    colors = ["#00d4ff", "#00ff88", "#ff6b35", "#bf5af2", "#ffd60a"]
    for i, (ticker, df) in enumerate(all_data.items()):
        norm = (df["Close"] / df["Close"].iloc[0]) * 100
        fig_trend.add_trace(go.Scatter(
            x=df["Date"], y=norm,
            name=STOCKS[ticker]["name"],
            line=dict(color=colors[i], width=2),
            hovertemplate=f"<b>{ticker}</b><br>Date: %{{x|%b %Y}}<br>Indexed: %{{y:.1f}}<extra></extra>"
        ))
    fig_trend.update_layout(
        template="plotly_dark",
        paper_bgcolor="#0a0e1a", plot_bgcolor="#0f1629",
        height=400,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        yaxis_title="Price Index (Base=100)",
        xaxis=dict(gridcolor="#1e2d4a"),
        yaxis=dict(gridcolor="#1e2d4a"),
        hovermode="x unified",
        margin=dict(l=10, r=10, t=40, b=10)
    )
    fig_trend.add_hline(y=100, line_dash="dot", line_color="#475569", opacity=0.6)
    st.plotly_chart(fig_trend, use_container_width=True)

    # Sector Performance Bar
    st.markdown("### 📊 Annual Return by Stock")
    returns = {}
    for ticker, df in all_data.items():
        returns[ticker] = ((df["Close"].iloc[-1] - df["Close"].iloc[0]) / df["Close"].iloc[0]) * 100

    bar_colors = ["#00ff88" if v >= 0 else "#ff4757" for v in returns.values()]
    fig_bar = go.Figure(go.Bar(
        x=list(returns.keys()),
        y=list(returns.values()),
        marker_color=bar_colors,
        text=[f"{v:+.1f}%" for v in returns.values()],
        textposition="outside",
        hovertemplate="<b>%{x}</b><br>Return: %{y:.2f}%<extra></extra>"
    ))
    fig_bar.update_layout(
        template="plotly_dark",
        paper_bgcolor="#0a0e1a", plot_bgcolor="#0f1629",
        height=320,
        yaxis=dict(gridcolor="#1e2d4a", title="Return (%)"),
        xaxis=dict(gridcolor="#1e2d4a"),
        margin=dict(l=10, r=10, t=20, b=10),
        showlegend=False
    )
    st.plotly_chart(fig_bar, use_container_width=True)

    # Insights
    best   = max(returns, key=returns.get)
    worst  = min(returns, key=returns.get)
    st.markdown(f'<div class="insight-box">🚀 <b>Best Performer:</b> {STOCKS[best]["name"]} with <b>{returns[best]:+.2f}%</b> return in {selected_fy}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="warning-box">⚠️ <b>Underperformer:</b> {STOCKS[worst]["name"]} with <b>{returns[worst]:+.2f}%</b> return in {selected_fy}</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════
# TAB 2: STOCK DEEP DIVE
# ══════════════════════════════════════════════
with tab2:
    df = all_data[selected_ticker]
    info = STOCKS[selected_ticker]

    st.markdown(f"### 🔍 {info['name']} ({selected_ticker}) — Deep Dive")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Open (FY Start)",  f"₹{df['Open'].iloc[0]:,.1f}")
    c2.metric("Current Close",    f"₹{df['Close'].iloc[-1]:,.1f}",  delta=f"vs ₹{df['Close'].iloc[0]:,.1f}")
    c3.metric("52W High",         f"₹{df['High'].max():,.1f}")
    c4.metric("52W Low",          f"₹{df['Low'].min():,.1f}")

    # Candlestick + MA
    st.markdown("#### 🕯️ Candlestick Chart with Moving Averages")
    fig_candle = make_subplots(rows=2, cols=1, shared_xaxes=True,
                               row_heights=[0.7, 0.3], vertical_spacing=0.03)

    fig_candle.add_trace(go.Candlestick(
        x=df["Date"], open=df["Open"], high=df["High"],
        low=df["Low"], close=df["Close"],
        name="OHLC",
        increasing_line_color="#00ff88", decreasing_line_color="#ff4757"
    ), row=1, col=1)

    fig_candle.add_trace(go.Scatter(
        x=df["Date"], y=df["MA7"], name="MA 7",
        line=dict(color="#ffd60a", width=1.5, dash="dot")
    ), row=1, col=1)

    fig_candle.add_trace(go.Scatter(
        x=df["Date"], y=df["MA30"], name="MA 30",
        line=dict(color="#bf5af2", width=1.5)
    ), row=1, col=1)

    vol_colors = ["#00ff88" if r >= 0 else "#ff4757" for r in df["Daily_Return"].fillna(0)]
    fig_candle.add_trace(go.Bar(
        x=df["Date"], y=df["Volume"],
        marker_color=vol_colors, name="Volume", opacity=0.7
    ), row=2, col=1)

    fig_candle.update_layout(
        template="plotly_dark",
        paper_bgcolor="#0a0e1a", plot_bgcolor="#0f1629",
        height=560,
        xaxis_rangeslider_visible=False,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0),
        margin=dict(l=10, r=10, t=40, b=10)
    )
    fig_candle.update_xaxes(gridcolor="#1e2d4a")
    fig_candle.update_yaxes(gridcolor="#1e2d4a")
    st.plotly_chart(fig_candle, use_container_width=True)

    # Daily Returns distribution
    st.markdown("#### 📊 Daily Returns Distribution")
    fig_hist = go.Figure()
    fig_hist.add_trace(go.Histogram(
        x=df["Daily_Return"].dropna(),
        nbinsx=50, name="Daily Return %",
        marker_color="#00d4ff", opacity=0.8
    ))
    fig_hist.add_vline(x=0, line_dash="dash", line_color="#ff4757")
    fig_hist.update_layout(
        template="plotly_dark",
        paper_bgcolor="#0a0e1a", plot_bgcolor="#0f1629",
        height=280,
        xaxis_title="Daily Return (%)", yaxis_title="Frequency",
        margin=dict(l=10, r=10, t=20, b=10)
    )
    st.plotly_chart(fig_hist, use_container_width=True)

    avg_ret = df["Daily_Return"].mean()
    vol_pct = df["Daily_Return"].std()
    if avg_ret > 0:
        st.markdown(f'<div class="insight-box">📈 <b>Avg Daily Return:</b> {avg_ret:+.3f}% | <b>Volatility (Std):</b> {vol_pct:.3f}%</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="warning-box">📉 <b>Avg Daily Return:</b> {avg_ret:+.3f}% | <b>Volatility (Std):</b> {vol_pct:.3f}%</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════
# TAB 3: PORTFOLIO TRACKER
# ══════════════════════════════════════════════
with tab3:
    st.markdown("### 💼 Portfolio Performance")

    INVEST_PER_STOCK = 100_000  # ₹1L per stock (scaled by weight)
    portfolio_rows = []
    total_invested = 0
    total_current  = 0

    for ticker, df in all_data.items():
        alloc = weights[ticker] / 100
        invested  = 200_000 * alloc
        units     = invested / df["Close"].iloc[0] if df["Close"].iloc[0] > 0 else 0
        current   = units * df["Close"].iloc[-1]
        pnl       = current - invested
        pnl_pct   = (pnl / invested * 100) if invested > 0 else 0
        total_invested += invested
        total_current  += current
        portfolio_rows.append({
            "Stock": STOCKS[ticker]["name"],
            "Ticker": ticker,
            "Allocation %": f"{weights[ticker]}%",
            "Invested (₹)": f"₹{invested:,.0f}",
            "Current Value (₹)": f"₹{current:,.0f}",
            "P&L (₹)": f"{'▲' if pnl>=0 else '▼'} ₹{abs(pnl):,.0f}",
            "Return %": f"{pnl_pct:+.2f}%",
            "_pnl": pnl
        })

    total_pnl = total_current - total_invested
    total_ret = (total_pnl / total_invested * 100) if total_invested > 0 else 0

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Total Invested",    f"₹{total_invested:,.0f}")
    m2.metric("Current Value",     f"₹{total_current:,.0f}", delta=f"₹{total_pnl:+,.0f}")
    m3.metric("Overall Return",    f"{total_ret:+.2f}%")
    m4.metric("Best FY",           selected_fy)

    col_a, col_b = st.columns([1, 1])

    with col_a:
        st.markdown("#### 🥧 Allocation Breakdown")
        pie_labels = [STOCKS[t]["name"] for t in STOCKS]
        pie_values = [weights[t] for t in STOCKS]
        fig_pie = go.Figure(go.Pie(
            labels=pie_labels, values=pie_values,
            hole=0.5,
            marker=dict(colors=["#00d4ff","#00ff88","#ff6b35","#bf5af2","#ffd60a"]),
            textinfo="label+percent",
            hovertemplate="<b>%{label}</b><br>%{percent}<extra></extra>"
        ))
        fig_pie.update_layout(
            template="plotly_dark",
            paper_bgcolor="#0a0e1a",
            height=320,
            showlegend=False,
            margin=dict(l=10, r=10, t=10, b=10)
        )
        st.plotly_chart(fig_pie, use_container_width=True)

    with col_b:
        st.markdown("#### 📊 P&L by Stock")
        pnl_vals   = [r["_pnl"] for r in portfolio_rows]
        pnl_names  = [r["Ticker"] for r in portfolio_rows]
        pnl_colors = ["#00ff88" if v >= 0 else "#ff4757" for v in pnl_vals]
        fig_pnl = go.Figure(go.Bar(
            x=pnl_names, y=pnl_vals,
            marker_color=pnl_colors,
            text=[f"₹{v:+,.0f}" for v in pnl_vals],
            textposition="outside"
        ))
        fig_pnl.update_layout(
            template="plotly_dark",
            paper_bgcolor="#0a0e1a", plot_bgcolor="#0f1629",
            height=320,
            yaxis=dict(gridcolor="#1e2d4a", title="P&L (₹)"),
            margin=dict(l=10, r=10, t=10, b=10)
        )
        st.plotly_chart(fig_pnl, use_container_width=True)

    st.markdown("#### 📋 Portfolio Summary Table")
    display_df = pd.DataFrame([{k: v for k, v in r.items() if k != "_pnl"} for r in portfolio_rows])
    st.dataframe(display_df, use_container_width=True, hide_index=True)

# ══════════════════════════════════════════════
# TAB 4: HEATMAP & CORRELATION
# ══════════════════════════════════════════════
with tab4:
    st.markdown("### 🔥 Sector & Correlation Analysis")

    # Monthly returns heatmap
    st.markdown("#### 📅 Monthly Returns Heatmap")
    monthly_data = {}
    for ticker, df in all_data.items():
        df_m = df.set_index("Date")["Close"].resample("ME").last().pct_change() * 100
        monthly_data[ticker] = df_m

    monthly_df = pd.DataFrame(monthly_data).dropna()
    monthly_df.index = monthly_df.index.strftime("%b %Y")

    fig_heat = go.Figure(go.Heatmap(
        z=monthly_df.values.T,
        x=monthly_df.index.tolist(),
        y=[STOCKS[t]["name"][:15] for t in monthly_df.columns],
        colorscale=[[0,"#ff4757"],[0.5,"#1e2d4a"],[1,"#00ff88"]],
        zmid=0,
        text=np.round(monthly_df.values.T, 1),
        texttemplate="%{text}%",
        hovertemplate="<b>%{y}</b><br>%{x}<br>Return: %{z:.2f}%<extra></extra>",
        colorbar=dict(title="Return %", tickfont=dict(color="#94a3b8"))
    ))
    fig_heat.update_layout(
        template="plotly_dark",
        paper_bgcolor="#0a0e1a", plot_bgcolor="#0f1629",
        height=340,
        margin=dict(l=10, r=10, t=20, b=60),
        xaxis=dict(tickangle=-45)
    )
    st.plotly_chart(fig_heat, use_container_width=True)

    # Correlation Matrix
    st.markdown("#### 🔗 Price Correlation Matrix")
    corr_df = pd.DataFrame({t: all_data[t]["Close"].values for t in STOCKS})
    corr_df.columns = [STOCKS[t]["name"][:12] for t in STOCKS]
    corr_matrix = corr_df.corr()

    fig_corr = go.Figure(go.Heatmap(
        z=corr_matrix.values,
        x=corr_matrix.columns.tolist(),
        y=corr_matrix.index.tolist(),
        colorscale=[[0,"#ff4757"],[0.5,"#1e2d4a"],[1,"#00d4ff"]],
        zmin=-1, zmax=1, zmid=0,
        text=np.round(corr_matrix.values, 2),
        texttemplate="%{text}",
        hovertemplate="%{x} × %{y}<br>Correlation: %{z:.3f}<extra></extra>",
        colorbar=dict(title="Corr", tickfont=dict(color="#94a3b8"))
    ))
    fig_corr.update_layout(
        template="plotly_dark",
        paper_bgcolor="#0a0e1a", plot_bgcolor="#0f1629",
        height=380,
        margin=dict(l=10, r=10, t=20, b=10)
    )
    st.plotly_chart(fig_corr, use_container_width=True)

    avg_corr = (corr_matrix.values.sum() - len(STOCKS)) / (len(STOCKS)**2 - len(STOCKS))
    if avg_corr > 0.7:
        st.markdown(f'<div class="warning-box">⚠️ High average correlation ({avg_corr:.2f}) — stocks tend to move together. Diversification benefit is limited.</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="insight-box">✅ Average correlation: {avg_corr:.2f} — reasonable diversification across selected stocks.</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════
# TAB 5: LIVE SIMULATION
# ══════════════════════════════════════════════
with tab5:
    st.markdown("### ⚡ Live Market Simulation")
    st.markdown("Simulates real-time price ticks for all 5 stocks. Toggle *Live Simulation* in the sidebar to activate.")

    if not live_refresh:
        st.info("🔴 Enable *Live Simulation* in the sidebar to start the live feed.")
    else:
        price_placeholder  = st.empty()
        chart_placeholder  = st.empty()
        ticker_placeholder = st.empty()

        # Seed with last known prices
        live_prices = {t: all_data[t]["Close"].iloc[-1] for t in STOCKS}
        history = {t: [live_prices[t]] for t in STOCKS}
        timestamps = [0]

        for tick in range(60):
            for t in STOCKS:
                shock = STOCKS[t]["volatility"] * np.random.randn() * 0.4
                live_prices[t] *= (1 + shock)
                history[t].append(live_prices[t])
            timestamps.append(tick + 1)

            # Metric cards
            with price_placeholder.container():
                cols = st.columns(5)
                for i, (t, p) in enumerate(live_prices.items()):
                    prev = history[t][-2] if len(history[t]) > 1 else p
                    delta_v = p - prev
                    cols[i].metric(
                        label=f"{t}",
                        value=f"₹{p:,.1f}",
                        delta=f"₹{delta_v:+.2f}"
                    )

            # Live chart
            with chart_placeholder.container():
                fig_live = go.Figure()
                live_colors = ["#00d4ff","#00ff88","#ff6b35","#bf5af2","#ffd60a"]
                for i, t in enumerate(STOCKS):
                    norm = [v / history[t][0] * 100 for v in history[t]]
                    fig_live.add_trace(go.Scatter(
                        x=list(range(len(norm))), y=norm,
                        name=t, line=dict(color=live_colors[i], width=2)
                    ))
                fig_live.update_layout(
                    template="plotly_dark",
                    paper_bgcolor="#0a0e1a", plot_bgcolor="#0f1629",
                    height=380,
                    yaxis_title="Indexed Price",
                    xaxis_title="Ticks",
                    legend=dict(orientation="h", y=1.1),
                    margin=dict(l=10, r=10, t=30, b=10)
                )
                fig_live.add_hline(y=100, line_dash="dot", line_color="#475569", opacity=0.5)
                st.plotly_chart(fig_live, use_container_width=True)

            with ticker_placeholder.container():
                tick_str = " &nbsp;|&nbsp; ".join(
                    [f"<span style='color:{'#00ff88' if history[t][-1]>=history[t][-2] else '#ff4757'}'>"
                     f"{t} ₹{live_prices[t]:,.1f}</span>"
                     for t in STOCKS if len(history[t]) >= 2]
                )
                st.markdown(
                    f'<div style="background:#0f1629;border:1px solid #1e3a5f;border-radius:8px;padding:10px 16px;'
                    f'font-family:Space Mono,monospace;font-size:0.8rem;">'
                    f'<span class="live-badge">● LIVE</span> &nbsp; {tick_str}</div>',
                    unsafe_allow_html=True
                )

            time.sleep(refresh_speed)

        st.success("✅ Simulation complete. Toggle Live Simulation again to restart.")

# ─────────────────────────────────────────────
# FOOTER
# ─────────────────────────────────────────────
st.markdown("---")
st.markdown(
    '<p style="text-align:center;color:#334155;font-size:0.75rem;font-family:Space Mono,monospace;">'
    'Stock Market Analytics Hub · Simulated Data for Presentation · Indian Retail & Fashion Sector'
    '</p>',
    unsafe_allow_html=True)
