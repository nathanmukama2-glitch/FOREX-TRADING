import streamlit as st
import yfinance as yf
import pandas_ta as ta
import pandas as pd
import feedparser 
from datetime import datetime
import pytz

st.set_page_config(page_title="Forex Foreteller Pro", layout="wide")
st.title("🦅 Forex Trading Foreteller Pro")

# --- 1. SIDEBAR: SETTINGS, RISK & SESSIONS ---
with st.sidebar:
    st.header("⚙️ Trading Settings")
    symbol = st.text_input("Pair (e.g., EURUSD=X)", "EURUSD=X")
    timeframe = st.selectbox("Timeframe", ["15m", "30m", "1h", "4h", "1d"], index=0)
    
    st.divider()
    st.header("🕒 Market Sessions (EAT)")
    # Logic for Entebbe Time (EAT)
    eat = pytz.timezone('Africa/Kampala')
    now_eat = datetime.now(eat).hour

    def get_session(hour):
        if 10 <= hour <= 18: return "🇬🇧 London: OPEN"
        if 15 <= hour <= 23: return "🇺🇸 New York: OPEN"
        if 2 <= hour <= 10: return "🇯🇵 Tokyo: OPEN"
        return "🌙 Market Quiet"

    session_status = get_session(now_eat)
    if "OPEN" in session_status:
        st.success(session_status)
    else:
        st.warning(session_status)
    
    st.divider()
    st.header("🧮 Risk Calculator")
    balance = st.number_input("Account Balance ($)", value=1000)
    risk_percent = st.slider("Risk Per Trade (%)", 0.5, 5.0, 1.0)
    stop_loss_pips = st.number_input("Stop Loss (Pips)", value=20)
    
    risk_amount = balance * (risk_percent / 100)
    if stop_loss_pips > 0:
        lot_size = risk_amount / (stop_loss_pips * 10)
        st.info(f"Recommended Lot: {lot_size:.2f}")

# --- 2. DATA FETCHING ---
ticker = yf.Ticker(symbol)
data = ticker.history(period="1mo", interval=timeframe)

if not data.empty and len(data) > 30:
    # --- 3. INDICATORS ENGINE ---
    data['RSI'] = ta.rsi(data['Close'], length=14)
    adx_df = ta.adx(data['High'], data['Low'], data['Close'], length=14)
    data = pd.concat([data, adx_df], axis=1)
    
    # --- LIQUIDITY CALCULATION ---
    data['Avg_Vol'] = data['Volume'].rolling(window=20).mean()
    current_vol = data['Volume'].iloc[-1]
    avg_vol = data['Avg_Vol'].iloc[-1]
    rvol = current_vol / avg_vol if avg_vol > 0 else 1
    
    # --- 4. SCORING LOGIC ---
    score = 5 
    rsi_val = data['RSI'].iloc[-1]
    if rsi_val < 30: score += 2 
    elif rsi_val > 70: score -= 2 

    last_adx = data['ADX_14'].iloc[-1]
    if last_adx < 20:
        score = 5 

    # --- 5. DASHBOARD TABS ---
    tab_signal, tab_liq, tab_calendar = st.tabs(["🎯 Live Signal", "💧 Liquidity", "📅 Macro Events"])

    with tab_signal:
        col1, col2 = st.columns([1, 1])
        with col1:
            st.subheader("🔥 Entry Strength Score")
            if score >= 8: st.success(f"### SCORE: {score} / 10 - BUY")
            elif score <= 2: st.error(f"### SCORE: {score} / 10 - SELL")
            else: st.info(f"### SCORE: {score} / 10 - WAIT")
            st.progress(score / 10)
        with col2:
            st.subheader("Technical Diagnostics")
            st.write(f"**RSI Momentum:** {rsi_val:.2f}")
            st.write(f"**Trend (ADX):** {last_adx:.2f}")

    with tab_liq:
        st.subheader("💧 Market Liquidity Analysis")
        l_col1, l_col2 = st.columns(2)
        with l_col1:
            st.metric("Relative Volume (RVOL)", f"{rvol:.2f}x")
            if rvol > 1.2: st.success("HIGH LIQUIDITY")
            else: st.warning("LOW LIQUIDITY")
        with l_col2:
            st.info("💡 Trading during the 'London/New York Overlap' (3 PM - 7 PM EAT) usually provides the best liquidity.")

    with tab_calendar:
        st.subheader("⚠️ High-Impact News")
        try:
            feed = feedparser.parse("https://nfs.faireconomy.media/ff_calendar_thisweek.xml")
            for entry in feed.entries[:5]:
                impact = "🔴" if "High" in getattr(entry, 'impact', '') else "🟡"
                st.write(f"{impact} **{entry.title}** ({entry.country})")
        except:
            st.error("Feed connection error.")

    # --- 6. HISTORY ---
    st.divider()
    st.subheader("📝 Live Market Log")
    st.dataframe(data[['Close', 'RSI', 'ADX_14', 'Volume']].tail(10))

else:
    st.info("🔄 Connecting to market data...")
