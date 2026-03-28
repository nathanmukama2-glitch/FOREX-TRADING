import streamlit as st
import yfinance as yf
import pandas_ta as ta
import pandas as pd
import numpy as np

st.set_page_config(page_title="Forex Foreteller Pro", layout="wide")
st.title("🦅 Forex Trading Foreteller Pro")

# --- 1. SIDEBAR: SETTINGS ---
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
    # --- 3. INDICATORS & ORDER FLOW ENGINE ---
    data['RSI'] = ta.rsi(data['Close'], length=14)
    
    # Simple Order Flow (Price Change * Volume)
    data['Delta'] = (data['Close'] - data['Open']) * data['Volume']
    cum_delta = data['Delta'].tail(10).sum()
    
    # --- 4. STRENGTH SCORING LOGIC ---
    score = 5 
    
    # RSI Logic
    if pd.notna(data['RSI'].iloc[-1]):
        rsi_val = data['RSI'].iloc[-1]
        if rsi_val < 30: score += 2 
        elif rsi_val > 70: score -= 2 

    # Order Flow Logic (Cumulative Delta)
    if cum_delta > 0: 
        score += 2  # Strong Buying Pressure
    elif cum_delta < 0:
        score -= 2  # Strong Selling Pressure

    # --- 5. DASHBOARD ---
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("🔥 Foreteller Entry Strength")
        if score >= 8:
            st.success(f"### SCORE: {score} / 10")
            st.warning("🚨 ALERT: SMART MONEY BUYING DETECTED")
        elif score <= 2:
            st.error(f"### SCORE: {score} / 10")
            st.warning("🚨 ALERT: SMART MONEY SELLING DETECTED")
        else:
            st.info(f"### SCORE: {score} / 10")
        
        st.progress(score / 10)
        
    with col2:
        st.subheader("🌊 Order Flow Heatmap (Last 10 Bars)")
        delta_color = "green" if cum_delta > 0 else "red"
        st.markdown(f"""
            <div style="background-color:{delta_color}; padding:15px; border-radius:10px; text-align:center; color:white;">
                <b>Cumulative Delta: {cum_delta:,.0f}</b><br>
                {'Bullish Pressure' if cum_delta > 0 else 'Bearish Pressure'}
            </div>
        """, unsafe_allow_with_html=True)

    # --- 6. VOLUME PROFILE CHART ---
    st.divider()
    st.subheader("📊 Volume Profile & Price Action")
    st.bar_chart(data['Volume'].tail(20))

else:
    st.info("🔄 Connecting to live exchange rates...")
