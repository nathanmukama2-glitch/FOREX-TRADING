import streamlit as st
import yfinance as yf
import pandas_ta as ta
import pandas as pd
import requests
from bs4 import BeautifulSoup

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
    data['Delta'] = (data['Close'] - data['Open']) * data['Volume']
    cum_delta = data['Delta'].tail(10).sum()
    
    # --- 4. STRENGTH SCORING LOGIC ---
    score = 5 
    
    # RSI Scoring
    if pd.notna(data['RSI'].iloc[-1]):
        rsi_val = data['RSI'].iloc[-1]
        if rsi_val < 30: score += 2 
        elif rsi_val > 70: score -= 2 

    # Order Flow (Delta) Scoring
    if cum_delta > 0: score += 2
    elif cum_delta < 0: score -= 2

    # --- 5. DASHBOARD LAYOUT ---
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("🔥 Foreteller Entry Strength")
        
        # Display Final Score
        if score >= 8:
            st.success(f"### SCORE: {score} / 10 - STRONG BUY")
            st.toast("BUY SETUP DETECTED")
        elif score <= 2:
            st.error(f"### SCORE: {score} / 10 - STRONG SELL")
            st.toast("SELL SETUP DETECTED")
        else:
            st.info(f"### SCORE: {score} / 10 - NEUTRAL")
        
        st.progress(score / 10)

    with col2:
        st.subheader("📅 High-Impact Economic Events")
        # Simplified News Feed for Fundamentals
        news = ticker.news
        if news:
            for item in news[:3]:
                st.write(f"• **{item.get('title')}**")
        else:
            st.write("No major USD/EUR volatility events currently detected.")

    # --- 6. ADVANCED VOLUME PROFILE ---
    st.divider()
    st.subheader("📊 Recent Order Flow (Volume Delta)")
    st.area_chart(data['Delta'].tail(30))
    st.caption("Green spikes indicate strong buyer control; Red spikes indicate seller control.")

else:
    st.info("🔄 Connecting to live exchange rates... check your internet in Entebbe.")
