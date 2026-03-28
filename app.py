import streamlit as st
import yfinance as yf
import pandas_ta as ta
import pandas as pd

st.set_page_config(page_title="Forex Foreteller Pro", layout="wide")
st.title("🦅 Forex Trading Foreteller Pro")

# --- 1. SIDEBAR: RISK MGMT ---
with st.sidebar:
    st.header("⚙️ Trading Settings")
    symbol = st.text_input("Pair (e.g., EURUSD=X)", "EURUSD=X")
    timeframe = st.selectbox("Timeframe", ["15m", "30m", "1h", "4h", "1d"], index=0)
    
    st.divider()
    st.header("🧮 Risk Calculator")
    balance = st.number_input("Account Balance ($)", value=1000, step=100)
    risk_percent = st.slider("Risk Per Trade (%)", 0.5, 5.0, 1.0)
    stop_loss_pips = st.number_input("Stop Loss (Pips)", value=20, step=5)
    
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
    adx = ta.adx(data['High'], data['Low'], data['Close'], length=14)
    data = pd.concat([data, adx], axis=1)
    data['Delta'] = (data['Close'] - data['Open']) * data['Volume']
    
    # --- 4. SCORING BREAKDOWN ---
    score = 5 
    rsi_vote = "Neutral"
    vol_vote = "Neutral"
    trend_status = "Active"
    
    # RSI Logic
    rsi_val = data['RSI'].iloc[-1]
    if rsi_val < 30: 
        score += 2
        rsi_vote = "Bullish (+2)"
    elif rsi_val > 70: 
        score -= 2
        rsi_vote = "Bearish (-2)"

    # Volume Delta Logic (Last 5 bars)
    recent_delta = data['Delta'].tail(5).sum()
    if recent_delta > 0:
        score += 2
        vol_vote = "Bullish (+2)"
    elif recent_delta < 0:
        score -= 2
        vol_vote = "Bearish (-2)"

    # ADX Safety Filter
    last_adx = data['ADX_14'].iloc[-1]
    if last_adx < 20:
        score = 5
        trend_status = "Weak (Score Reset)"

    # --- 5. DASHBOARD ---
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("🔥 Entry Strength Score")
        if score >= 8: st.success(f"### SCORE: {score} / 10")
        elif score <= 2: st.error(f"### SCORE: {score} / 10")
        else: st.info(f"### SCORE: {score} / 10")
        st.progress(score / 10)

    with col2:
        st.subheader("⚖️ Signal Breakdown")
        breakdown_data = {
            "Judge": ["RSI Momentum", "Order Flow (Delta)", "Trend Filter (ADX)"],
            "Decision": [rsi_vote, vol_vote, trend_status],
            "Value": [f"{rsi_val:.2f}", f"{recent_delta:,.0f}", f"{last_adx:.2f}"]
        }
        st.table(pd.DataFrame(breakdown_data))

    # --- 6. HISTORY LOGGER ---
    st.divider()
    st.subheader("📝 Signal History Log")
    # We create a log of the last 15 periods and their scores
    history_log = data[['Close', 'RSI', 'ADX_14']].tail(15).copy()
    st.dataframe(history_log)

else:
    st.info("🔄 Connecting to market data...")
