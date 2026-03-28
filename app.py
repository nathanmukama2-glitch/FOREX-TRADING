import streamlit as st
import yfinance as yf
import pandas_ta as ta
import pandas as pd

st.title("🦅 Forex Foreteller Pro")

# 1. Data Fetcher
symbol = st.sidebar.text_input("Enter Pair (e.g., EURUSD=X)", "EURUSD=X")

# We fetch more data (5 days) to ensure the RSI has enough history to calculate
data = yf.download(symbol, period="5d", interval="15m")

if not data.empty and len(data) > 14:
    # 2. Indicator Calculations
    data['RSI'] = ta.rsi(data['Close'], length=14)
    
    # 3. Scoring Logic with Safety Check
    last_rsi = data['RSI'].iloc[-1]
    score = 5 

    # This check prevents the TypeError if RSI is not yet calculated
    if pd.notna(last_rsi):
        if last_rsi < 30: score += 2  # Oversold (Strong Buy)
        if last_rsi > 70: score -= 2  # Overbought (Strong Sell)
        
        # 4. Display Results
        st.metric(label="Entry Strength Score", value=f"{score}/10")
        st.write(f"Current RSI: {last_rsi:.2f}")
        
        if score >= 7:
            st.success("🚨 ALERT: STRONG BUY SIGNAL")
        elif score <= 3:
            st.error("🚨 ALERT: STRONG SELL SIGNAL")
        else:
            st.warning("⚖️ Status: Wait for Setup")
    else:
        st.info("Calculating technical indicators... please wait a moment.")

else:
    st.error("Waiting for sufficient market data. Please ensure the symbol is correct.")
