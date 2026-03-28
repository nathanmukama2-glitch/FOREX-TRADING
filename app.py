import streamlit as st
import yfinance as yf
import pandas_ta as ta
import pandas as pd

st.set_page_config(page_title="Forex Foreteller Pro", layout="wide")
st.title("🦅 Forex Trading Foreteller Pro")

# --- 1. SIDEBAR: SETTINGS & RISK CALCULATOR ---
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
    
    # --- 4. STRENGTH SCORING LOGIC ---
    score = 5 
    
    # RSI Scoring
    if pd.notna(data['RSI'].iloc[-1]):
        rsi_val = data['RSI'].iloc[-1]
        if rsi_val < 30: score += 2 
        elif rsi_val > 70: score -= 2 

    # Trend Strength (ADX) - Don't trade if ADX < 20 (Weak Trend)
    last_adx = data['ADX_14'].iloc[-1]
    if last_adx < 20:
        score = 5 # Force neutral if there is no trend
    
    # --- 5. DASHBOARD & ALERTS ---
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("🔥 Entry Strength Score")
        
        if score >= 8:
            st.success(f"### SCORE: {score} / 10")
            st.balloons() # Visual celebration for high strength
            st.warning("🚨 ALERT: HIGH PROBABILITY BUY SIGNAL DETECTED")
        elif score <= 2:
            st.error(f"### SCORE: {score} / 10")
            st.warning("🚨 ALERT: HIGH PROBABILITY SELL SIGNAL DETECTED")
        else:
            st.info(f"### SCORE: {score} / 10")
            
        st.progress(score / 10)
        st.write(f"**Trend Strength (ADX):** {last_adx:.2f} ({'Strong' if last_adx > 25 else 'Weak'})")

    with col2:
        st.subheader("📰 Macro News")
        news = ticker.news
        if news:
            for item in news[:3]:
                st.write(f"• **{item.get('title')}** [Read]({item.get('link')})")

    # --- 6. ADVANCED HISTORY ---
    st.divider()
    st.subheader("📝 Live Foreteller Log")
    # Show last 5 periods with indicators
    st.dataframe(data[['Close', 'RSI', 'ADX_14']].tail(5))

else:
    st.info("🔄 Connecting to live exchange rates...")
