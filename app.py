import streamlit as st
import yfinance as yf
import pandas_ta as ta
import pandas as pd
import numpy as np

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
    
    # Lot Size Calculation (Standard Lot = 100,000 units)
    # Approx $10 per pip for 1.0 lot
    risk_amount = balance * (risk_percent / 100)
    if stop_loss_pips > 0:
        lot_size = risk_amount / (stop_loss_pips * 10)
        st.success(f"Recommended Lot: {lot_size:.2f}")
        st.caption(f"Risking: ${risk_amount:.2f}")

# --- 2. DATA FETCHING ---
ticker = yf.Ticker(symbol)
data = ticker.history(period="1mo", interval=timeframe)

if not data.empty and len(data) > 30:
    # --- 3. INDICATORS ENGINE ---
    data['RSI'] = ta.rsi(data['Close'], length=14)
    macd = ta.macd(data['Close'])
    if macd is not None: data = pd.concat([data, macd], axis=1)
    
    # Cumulative Delta Approximation (Order Flow)
    data['Delta'] = (data['Close'] - data['Open']) * data['Volume']
    cum_delta = data['Delta'].tail(10).sum()

    # --- 4. STRENGTH SCORING LOGIC ---
    score = 5 
    last_close = data['Close'].iloc[-1]
    
    # RSI Logic
    if 'RSI' in data.columns and pd.notna(data['RSI'].iloc[-1]):
        rsi_val = data['RSI'].iloc[-1]
        if rsi_val < 35: score += 2 
        if rsi_val > 65: score -= 2 

    # Order Flow Logic
    if cum_delta > 0: score += 1
    else: score -= 1

    # --- 5. DASHBOARD LAYOUT ---
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("🔥 Entry Strength Heatmap")
        # Visual Color Logic
        bg_color = "green" if score >= 7 else "red" if score <= 3 else "gray"
        st.markdown(f"""
            <div style="background-color:{bg_color}; padding:20px; border-radius:10px; text-align:center;">
                <h1 style="color:white; margin:0;">{score} / 10</h1>
                <p style="color:white; font-weight:bold;">Strength Rating</p>
            </div>
        """, unsafe_allow_with_html=True)
        
        if score >= 7:
            st.success("🚨 ALERT: STRONG BUY SIGNAL")
            st.toast("Trade Occurring: BULLISH SETUP")
        elif score <= 3:
            st.error("🚨 ALERT: STRONG SELL SIGNAL")
            st.toast("Trade Occurring: BEARISH SETUP")

    with col2:
        st.subheader("📰 Macro Fundamentals")
        news = ticker.news
        if news:
            for item in news[:3]:
                title = item.get('title')
                link = item.get('link')
                if title and link:
                    st.write(f"• **{title}** [Link]({link})")
        else:
            st.write("No fundamental news found.")

    # --- 6. HISTORY LOG & DATA ---
    st.divider()
    st.subheader("📊 Recent Order Flow (Delta)")
    st.line_chart(data['Delta'].tail(20))
    st.dataframe(data.tail(5))

else:
    st.info("🔄 Initializing Foreteller Engine...")
