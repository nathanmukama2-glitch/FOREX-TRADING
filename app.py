import streamlit as st
import yfinance as yf
import pandas_ta as ta
import pandas as pd
import feedparser # Add 'feedparser' to your requirements.txt

st.set_page_config(page_title="Forex Foreteller Pro", layout="wide")
st.title("🦅 Forex Trading Foreteller Pro")

# --- 1. SIDEBAR: SETTINGS & RISK ---
with st.sidebar:
    st.header("⚙️ Trading Settings")
    symbol = st.text_input("Pair (e.g., EURUSD=X)", "EURUSD=X")
    timeframe = st.selectbox("Timeframe", ["15m", "30m", "1h", "4h", "1d"], index=0)
    
    st.divider()
    st.header("🧮 Risk Calculator")
    balance = st.number_input("Account Balance ($)", value=1000)
    risk_percent = st.slider("Risk Per Trade (%)", 0.5, 5.0, 1.0)
    stop_loss_pips = st.number_input("Stop Loss (Pips)", value=20)
    
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
    
    # --- 4. SCORING LOGIC ---
    score = 5 
    rsi_val = data['RSI'].iloc[-1]
    if rsi_val < 30: score += 2 
    elif rsi_val > 70: score -= 2 

    last_adx = data['ADX_14'].iloc[-1]
    if last_adx < 20:
        score = 5 # Safety reset for weak trends

    # --- 5. DASHBOARD TABS ---
    tab_signal, tab_calendar = st.tabs(["🎯 Live Signal", "📅 Macro Events"])

    with tab_signal:
        col1, col2 = st.columns([1, 1])
        with col1:
            st.subheader("🔥 Entry Strength Score")
            if score >= 8: st.success(f"### SCORE: {score} / 10 - BUY")
            elif score <= 2: st.error(f"### SCORE: {score} / 10 - SELL")
            else: st.info(f"### SCORE: {score} / 10 - WAIT")
            st.progress(score / 10)
        with col2:
            st.subheader("Technical Diagnostics")
            st.write(f"**RSI Momentum:** {rsi_val:.2f}")
            st.write(f"**Trend (ADX):** {last_adx:.2f}")

    with tab_calendar:
        st.subheader("⚠️ High-Impact News (USD/EUR/GBP)")
        try:
            # Fetching live events from a reliable calendar feed
            calendar_url = "https://nfs.faireconomy.media/ff_calendar_thisweek.xml"
            feed = feedparser.parse(calendar_url)
            
            if feed.entries:
                for entry in feed.entries[:8]:
                    # Highlights events likely to cause high volatility
                    impact_color = "🔴" if "High" in getattr(entry, 'impact', '') else "🟡"
                    st.write(f"{impact_color} **{entry.title}** | {entry.country} | {entry.date} {entry.time}")
            else:
                st.write("No major news events found for the next 24 hours.")
        except:
            st.error("Economic feed temporarily unavailable. Check manual calendar.")

    # --- 6. HISTORY ---
    st.divider()
    st.subheader("📝 Live Market Log")
    st.dataframe(data[['Close', 'RSI', 'ADX_14']].tail(10))

else:
    st.info("🔄 Refreshing live exchange data... check your connection in Entebbe.")
