import streamlit as st
import yfinance as yf
import pandas_ta as ta
import pandas as pd

st.set_page_config(page_title="Forex Foreteller Pro", layout="wide")
st.title("🦅 Forex Trading Foreteller Pro")

# 1. Sidebar Configuration
symbol = st.sidebar.text_input("Enter Pair (e.g., EURUSD=X)", "EURUSD=X")
timeframe = st.sidebar.selectbox("Select Timeframe", ["15m", "30m", "1h", "4h", "1d"], index=0)

# 2. Data Fetcher
data = yf.download(symbol, period="1mo", interval=timeframe)

if not data.empty and len(data) > 30:
    # 3. Indicators Engine
    data['RSI'] = ta.rsi(data['Close'], length=14)
    
    # MACD Calculation
    macd = ta.macd(data['Close'])
    if macd is not None:
        data = pd.concat([data, macd], axis=1)
    
    # Bollinger Bands
    bbands = ta.bbands(data['Close'], length=20, std=2)
    if bbands is not None:
        data = pd.concat([data, bbands], axis=1)

    # 4. Strength Scoring Logic
    score = 5 
    last_close = data['Close'].iloc[-1]
    
    # RSI Score
    if 'RSI' in data.columns and pd.notna(data['RSI'].iloc[-1]):
        rsi_val = data['RSI'].iloc[-1]
        if rsi_val < 30: score += 2 
        if rsi_val > 70: score -= 2 
        
    # MACD Score (Safe detection)
    hist_cols = [col for col in data.columns if 'MACDh' in col]
    if hist_cols and pd.notna(data[hist_cols[0]].iloc[-1]):
        if data[hist_cols[0]].iloc[-1] > 0: score += 1
        else: score -= 1

    # Bollinger Score
    if 'BBL_20_2.0' in data.columns and last_close <= data['BBL_20_2.0'].iloc[-1]:
        score += 2
    if 'BBU_20_2.0' in data.columns and last_close >= data['BBU_20_2.0'].iloc[-1]:
        score -= 2

    # 5. Dashboard Layout
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.metric(label="Entry Strength Score", value=f"{score}/10")
        if score >= 7:
            st.success("🚨 ALERT: STRONG BUY SIGNAL")
        elif score <= 3:
            st.error("🚨 ALERT: STRONG SELL SIGNAL")
        else:
            st.info("⚖️ Status: No High-Probability Setup")

    with col2:
        st.subheader("📰 Macro News & Fundamentals")
        st.write("Fetching latest news ticker...")
        st.caption("Check the Economic Calendar for high-impact USD/EUR events today.")

    # 6. History Log
    st.divider()
    st.subheader("📝 History Log")
    st.dataframe(data.tail(5))

else:
    st.info("🔄 Connecting to market data... Please wait a few seconds for the feed to initialize.")
