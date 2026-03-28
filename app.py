import streamlit as st
import yfinance as yf
import pandas_ta as ta
import pandas as pd

st.title("🦅 Forex Foreteller Pro")

# 1. Data Fetcher
symbol = st.sidebar.text_input("Enter Pair (e.g., EURUSD=X)", "EURUSD=X")
data = yf.download(symbol, period="1d", interval="15m")

if not data.empty:
    # 2. Indicator Calculations
    data['RSI'] = ta.rsi(data['Close'], length=14)
    macd = ta.macd(data['Close'])
    data = pd.concat([data, macd], axis=1)
    
    # 3. Scoring Logic (Strength of Entry)
    last_rsi = data['RSI'].iloc[-1]
    score = 5 # Start at neutral
    
    if last_rsi < 30: score += 2  # Oversold (Strong Buy)
    if last_rsi > 70: score -= 2  # Overbought (Strong Sell)
    
    # 4. Display Results
    st.metric(label="Entry Strength Score", value=f"{score}/10")
    
    if score >= 7:
        st.success("🚨 ALERT: STRONG BUY SIGNAL")
    elif score <= 3:
        st.error("🚨 ALERT: STRONG SELL SIGNAL")
    else:
        st.warning("⚖️ Status: Wait for Setup")

else:
    st.error("Waiting for data... check your symbol.")
