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
        st.caption(f"Risking: ${risk_amount:.2f}")

# --- 2. DATA FETCHING ---
ticker = yf.Ticker(symbol)
data = ticker.history(period="1mo", interval=timeframe)

if not data.empty and len(data) > 30:
    # --- 3. INDICATORS ENGINE ---
    data['RSI'] = ta.rsi(data['Close'], length=14)
    
    # --- 4. STRENGTH SCORING LOGIC ---
    score = 5 
    last_close = data['Close'].iloc[-1]
    
    if 'RSI' in data.columns and pd.notna(data['RSI'].iloc[-1]):
        rsi_val = data['RSI'].iloc[-1]
        if rsi_val < 35: score += 2 
        if rsi_val > 65: score -= 2 

    # --- 5. DASHBOARD LAYOUT ---
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("🔥 Entry Strength Heatmap")
        # Fixed Heatmap logic
        bg_color = "#2ecc71" if score >= 7 else "#e74c3c" if score <= 3 else "#95a5a6"
        
        heatmap_html = f"""
            <div style="background-color:{bg_color}; padding:30px; border-radius:15px; text-align:center; border: 2px solid white;">
                <h1 style="color:white; font-size:50px; margin:0;">{score} / 10</h1>
                <p style="color:white; font-size:20px; font-weight:bold; margin:0;">Entry Strength</p>
            </div>
        """
        st.markdown(heatmap_html, unsafe_allow_with_html=True)
        
        if score >= 7:
            st.success("🚨 ALERT: STRONG BUY SIGNAL")
        elif score <= 3:
            st.error("🚨 ALERT: STRONG SELL SIGNAL")

    with col2:
        st.subheader("📰 Macro News")
        news = ticker.news
        if news:
            for item in news[:3]:
                title = item.get('title')
                link = item.get('link')
                if title and link:
                    st.write(f"• **{title}** [Read]({link})")
        else:
            st.write("No fundamentals found at this moment.")

    # --- 6. HISTORY ---
    st.divider()
    st.subheader("📝 Market History Log")
    st.dataframe(data[['Close', 'Open', 'High', 'Low']].tail(5))

else:
    st.info("🔄 Connecting to live exchange rates... please wait.")
