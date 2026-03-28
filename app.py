import streamlit as st
import yfinance as yf
import pandas_ta as ta
import pandas as pd

st.set_page_config(page_title="Forex Foreteller Pro", layout="wide")
st.title("🦅 Forex Trading Foreteller Pro")

# 1. Sidebar
symbol = st.sidebar.text_input("Enter Pair (e.g., EURUSD=X)", "EURUSD=X")
timeframe = st.sidebar.selectbox("Select Timeframe", ["15m", "30m", "1h", "4h", "1d"], index=0)

# 2. Data Fetcher
ticker = yf.Ticker(symbol)
data = ticker.history(period="1mo", interval=timeframe)

if not data.empty and len(data) > 30:
    # 3. Indicators Engine (RSI, MACD, Bollinger)
    data['RSI'] = ta.rsi(data['Close'], length=14)
    macd = ta.macd(data['Close'])
    if macd is not None: data = pd.concat([data, macd], axis=1)
    bbands = ta.bbands(data['Close'], length=20, std=2)
    if bbands is not None: data = pd.concat([data, bbands], axis=1)

    # 4. Strength Scoring
    score = 5 
    last_close = data['Close'].iloc[-1]
    
    # RSI Score
    if 'RSI' in data.columns and pd.notna(data['RSI'].iloc[-1]):
        rsi_val = data['RSI'].iloc[-1]
        if rsi_val < 35: score += 2 
        if rsi_val > 65: score -= 2 

    # 5. Dashboard Layout
    col1, col2 = st.columns([1, 1])
    
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
        news = ticker.news
        if news:
            for item in news[:3]: # Show top 3 headlines
                st.write(f"**{item['title']}**")
                st.caption(f"Source: {item['publisher']} | [Read More]({item['link']})")
        else:
            st.write("No recent news found for this pair.")

    # 6. History Log
    st.divider()
    st.subheader("📝 History Log")
    st.dataframe(data.tail(5))

else:
    st.info("🔄 Syncing with market data...")
