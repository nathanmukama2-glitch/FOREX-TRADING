import streamlit as st
import yfinance as yf
import pandas_ta as ta
import pandas as pd
import plotly.graph_objects as go
import feedparser 
from datetime import datetime
import pytz

st.set_page_config(page_title="Forex Foreteller Pro", layout="wide")
st.title("🦅 Forex Trading Foreteller Pro")

# --- 1. SIDEBAR: SETTINGS & SESSIONS ---
with st.sidebar:
    st.header("⚙️ Trading Settings")
    symbol = st.text_input("Pair (e.g., EURUSD=X)", "EURUSD=X")
    timeframe = st.selectbox("Timeframe", ["15m", "30m", "1h", "4h", "1d"], index=0)
    
    if st.button("🔄 Force Data Refresh"):
        st.rerun()

    st.divider()
    st.header("🕒 Market Sessions (EAT)")
    eat = pytz.timezone('Africa/Kampala')
    now_eat = datetime.now(eat).hour

    def get_session(hour):
        if 10 <= hour <= 18: return "🇬🇧 London: OPEN"
        if 15 <= hour <= 23: return "🇺🇸 New York: OPEN"
        if 2 <= hour <= 10: return "🇯🇵 Tokyo: OPEN"
        return "🌙 Market Quiet"

    st.info(get_session(now_eat))
    
    st.divider()
    st.header("🧮 Risk Calculator")
    balance = st.number_input("Account Balance ($)", value=1000)
    risk_percent = st.slider("Risk (%)", 0.5, 5.0, 1.0)
    stop_loss_pips = st.number_input("Stop Loss (Pips)", value=20)
    
    risk_amount = balance * (risk_percent / 100)
    if stop_loss_pips > 0:
        lot_size = risk_amount / (stop_loss_pips * 10)
        st.success(f"Recommended Lot: {lot_size:.2f}")

# --- 2. DATA FETCHING ---
ticker = yf.Ticker(symbol)
data = ticker.history(period="1mo", interval=timeframe)

if not data.empty and len(data) > 30:
    # --- 3. INDICATORS ENGINE ---
    data['RSI'] = ta.rsi(data['Close'], length=14)
    adx_df = ta.adx(data['High'], data['Low'], data['Close'], length=14)
    bbands = ta.bbands(data['Close'], length=20, std=2)
    data = pd.concat([data, adx_df, bbands], axis=1)
    
    upper_col = [c for c in data.columns if 'BBU' in c][0]
    lower_col = [c for c in data.columns if 'BBL' in c][0]
    mid_col = [c for c in data.columns if 'BBM' in c][0]
    
    # RVOL (Liquidity)
    data['Avg_Vol'] = data['Volume'].rolling(window=20).mean()
    rvol = data['Volume'].iloc[-1] / data['Avg_Vol'].iloc[-1] if data['Avg_Vol'].iloc[-1] > 0 else 1
    
    # --- 4. SCORING LOGIC ---
    score = 5 
    rsi_val = data['RSI'].iloc[-1]
    price = data['Close'].iloc[-1]
    curr_upper = data[upper_col].iloc[-1]
    curr_lower = data[lower_col].iloc[-1]

    if rsi_val < 35: score += 2 
    elif rsi_val > 65: score -= 2 
    if price <= curr_lower: score += 2 
    elif price >= curr_upper: score -= 2 
    if data['ADX_14'].iloc[-1] < 15: score = 5 

    # --- 5. DASHBOARD TABS ---
    tab_signal, tab_chart, tab_calendar = st.tabs(["🎯 Live Signal", "📈 Market Chart", "📅 Macro Events"])

    with tab_signal:
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("🔥 Entry Strength Score")
            if score >= 7: st.success(f"### SCORE: {score} / 10 - BUY")
            elif score <= 3: st.error(f"### SCORE: {score} / 10 - SELL")
            else: st.info(f"### SCORE: {score} / 10 - WAIT")
            st.progress(score / 10)
        with col2:
            st.subheader("💧 Liquidity Status")
            if rvol > 1.2: st.write(f"### 🟢 HIGH ({rvol:.2f}x)")
            elif rvol > 0.8: st.write(f"### 🟡 NORMAL ({rvol:.2f}x)")
            else: st.write(f"### 🔴 LOW ({rvol:.2f}x)")
            st.write(f"**RSI:** {rsi_val:.2f} | **ADX:** {data['ADX_14'].iloc[-1]:.2f}")

    with tab_chart:
        st.subheader(f"Interactive {symbol} Analysis")
        # Create the Bollinger Chart
        fig = go.Figure()
        
        # Candlesticks
        fig.add_trace(go.Candlestick(x=data.index, open=data['Open'], high=data['High'], 
                                     low=data['Low'], close=data['Close'], name="Price"))
        
        # Upper Band
        fig.add_trace(go.Scatter(x=data.index, y=data[upper_col], line=dict(color='rgba(173, 216, 230, 0.5)'), name="Upper Band"))
        
        # Lower Band
        fig.add_trace(go.Scatter(x=data.index, y=data[lower_col], line=dict(color='rgba(173, 216, 230, 0.5)'), name="Lower Band", fill='tonexty'))
        
        # Mid Band
        fig.add_trace(go.Scatter(x=data.index, y=data[mid_col], line=dict(color='orange', dash='dot'), name="Middle (Avg)"))

        fig.update_layout(xaxis_rangeslider_visible=False, height=500, template="plotly_dark")
        st.plotly_chart(fig, use_container_width=True)
        st.info("💡 Tip: When the blue bands get narrow (The Squeeze), a big move is coming!")

    with tab_calendar:
        st.subheader("⚠️ High-Impact News (This Week)")
        try:
            feed = feedparser.parse("https://nfs.faireconomy.media/ff_calendar_thisweek.xml")
            news_found = False
            for entry in feed.entries:
                impact = getattr(entry, 'impact', '').strip().lower()
                if impact == "high":
                    st.error(f"🔴 **HIGH:** {entry.title} ({entry.country})")
                    news_found = True
            if not news_found: st.info("No major news events scheduled.")
        except: st.error("News server error.")

    st.divider()
    st.subheader("📝 Live Market Log")
    st.dataframe(data[['Close', 'RSI', 'ADX_14', upper_col, lower_col]].tail(5))
else:
    st.info("🔄 Connecting to market data...")
