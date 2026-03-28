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
    data = pd.concat([data, macd], axis=1)
    # Find the Histogram column dynamically to prevent KeyError
    hist_col = [col for col in data.columns if 'MACDh' in col][0]
    
    # Bollinger Bands
    bbands = ta.bbands(data['Close'], length=20, std=2)
    data = pd.concat([data, bbands], axis=1)

    # Fibonacci Logic
    highest_high = data['High'].max()
    lowest_low = data['Low'].min()
    diff = highest_high - lowest_low
    fib_618 = highest_high - (0.618 * diff)
    fib_500 = highest_high - (0.5 * diff)

    # Latest Values
    last_close = data['Close'].iloc[-1]
    last_rsi = data['RSI'].iloc[-1]
    last_macd_h = data[hist_col].iloc[-1]
    upper_bb = data['BBU_20_2.0'].iloc[-1]
    lower_bb = data['BBL_20_2.0'].iloc[-1]

    # 4. Strength Scoring Logic
    score = 5 
    
    # RSI Rules
    if pd.notna(last_rsi):
        if last_rsi < 30: score += 2 
        if last_rsi > 70: score -= 2 
        
    # MACD Rules
    if pd.notna(last_macd_h):
        if last_macd_h > 0: score += 1 
        else: score -= 1 

    # Bollinger Band Rules
    if last_close <= lower_bb: score += 2 
    if last_close >= upper_bb: score -= 2 

    # Fibonacci Rules (Entry at 61.8% retracement)
    if abs(last_close - fib_618) / last_close < 0.001:
        score += 1

    # 5. Dashboard Layout
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.metric(label="Entry Strength Score", value=f"{score}/10")
        
        if score >= 7:
            st.success("🚨 ALERT: STRONG BUY SIGNAL")
            st.toast("Trade Occurring: BULLISH SETUP")
        elif score <= 3:
            st.error("🚨 ALERT: STRONG SELL SIGNAL")
            st.toast("Trade Occurring: BEARISH SETUP")
        else:
            st.info("⚖️ Status: No High-Probability Setup")

    with col2:
        st.subheader("Live Technical Summary")
        st.write(f"**Current Price:** {last_close:.4f}")
        st.write(f"**Fibonacci 61.8% Level:** {fib_618:.4f}")
        st.write(f"**RSI:** {last_rsi:.2f} ({'Oversold' if last_rsi < 30 else 'Overbought' if last_rsi > 70 else 'Neutral'})")

    # 6. History Log
    st.divider()
    st.subheader("📝 History Log")
    st.dataframe(data[['Close', 'RSI', hist_col]].tail(5))

else:
    st.error("Fetching market data... If this takes too long, verify the symbol is correct.")
