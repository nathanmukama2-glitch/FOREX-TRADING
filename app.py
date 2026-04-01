import streamlit as st
import yfinance as yf
import pandas_ta as ta
import pandas as pd
import feedparser 
from datetime import datetime
import pytz

st.set_page_config(page_title="Forex Foreteller Pro", layout="wide")
st.title("🦅 Forex Trading Foreteller Pro")

# --- 1. SIDEBAR: SETTINGS & SESSIONS ---
with st.sidebar:
    st.header("⚙️ Trading Settings")
    symbol = st.text_input("Pair (e.g., EURUSD=X)", "EURUSD=X")
    timeframe = st.selectbox("Timeframe", ["15m", "30m", "1h", "4h", "1d"], index=0)
    
    if st.button("🔄 Force Data Refresh"):
        st.rerun()

    st.divider()
    st.header("🕒 Market Sessions (EAT)")
    eat = pytz.timezone('Africa/Kampala')
    now_eat = datetime.now(eat).hour

    def get_session(hour):
        if 10 <= hour <= 18: return "🇬🇧 London: OPEN"
        if 15 <= hour <= 23: return "🇺🇸 New York: OPEN"
        if 2 <= hour <= 10: return "🇯🇵 Tokyo: OPEN"
        return "🌙 Market Quiet"

    st.info(get_session(now_eat))
    
    st.divider()
    st.header("🧮 Risk & Profit Tracker")
    balance = st.number_input("Account Balance ($)", value=1000)
    entry_price = st.number_input("Your Entry Price", value=0.0, format="%.5f")
    risk_percent = st.slider("Risk (%)", 0.5, 5.0, 1.0)
    
    risk_amount = balance * (risk_percent / 100)
    st.caption(f"Risking: ${risk_amount:.2f} on this trade.")

# --- 2. DATA FETCHING ---
ticker = yf.Ticker(symbol)
data = ticker.history(period="1mo", interval=timeframe)

if not data.empty and len(data) > 30:
    # --- 3. INDICATORS ENGINE ---
    data['RSI'] = ta.rsi(data['Close'], length=14)
    adx_df = ta.adx(data['High'], data['Low'], data['Close'], length=14)
    bbands = ta.bbands(data['Close'], length=20, std=2)
    data = pd.concat([data, adx_df, bbands], axis=1)
    
    # Smart Column Detection to fix the KeyError
    upper_col = [c for c in data.columns if 'BBU' in c][0]
    lower_col = [c for c in data.columns if 'BBL' in c][0]
    mid_col = [c for c in data.columns if 'BBM' in c][0]
    
    # RVOL (Liquidity)
    data['Avg_Vol'] = data['Volume'].rolling(window=20).mean()
    rvol = data['Volume'].iloc[-1] / data['Avg_Vol'].iloc[-1] if data['Avg_Vol'].iloc[-1] > 0 else 1
    
    # --- 4. SCORING LOGIC ---
    score = 5 
    rsi_val = data['RSI'].iloc[-1]
    price = data['Close'].iloc[-1]
    curr_upper = data[upper_col].iloc[-1]
    curr_lower = data[lower_col].iloc[-1]

    if rsi_val < 35: score += 2 
    elif rsi_val > 65: score -= 2 

    if price <= curr_lower: score += 2 
    elif price >= curr_upper: score -= 2 

    if data['ADX_14'].iloc[-1] < 15: score = 5 

    # --- 5. DASHBOARD TABS ---
    tab_signal, tab_profit, tab_calendar = st.tabs(["🎯 Live Signal", "💰 Profit Targets", "📅 Macro Events"])

    with tab_signal:
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("🔥 Entry Strength Score")
            if score >= 7: st.success(f"### SCORE: {score} / 10 - BUY")
            elif score <= 3: st.error(f"### SCORE: {score} / 10 - SELL")
            else: st.info(f"### SCORE: {score} / 10 - WAIT")
            st.progress(score / 10)
        with col2:
            st.subheader("Technical Diagnostics")
            st.write(f"**RSI:** {rsi_val:.2f}")
            st.write(f"**Liquidity:** {rvol:.2f}x")

    with tab_profit:
        st.subheader("🎯 Target Planning")
        if entry_price > 0:
            if score >= 7: # Buying
                tp1 = data[mid_col].iloc[-1]
                tp2 = curr_upper
                st.write(f"🟢 **Target 1 (Mid):** {tp1:.5f}")
                st.write(f"🟢 **Target 2 (Upper):** {tp2:.5f}")
            elif score <= 3: # Selling
                tp1 = data[mid_col].iloc[-1]
                tp2 = curr_lower
                st.write(f"🔴 **Target 1 (Mid):** {tp1:.5f}")
                st.write(f"🔴 **Target 2 (Lower):** {tp2:.5f}")
        else:
            st.info("Enter your 'Entry Price' in the sidebar to see Take Profit targets.")

    with tab_calendar:
        st.subheader("⚠️ High-Impact News")
        try:
            feed = feedparser.parse("https://nfs.faireconomy.media/ff_calendar_thisweek.xml")
            for entry in feed.entries[:5]:
                impact = "🔴" if "High" in getattr(entry, 'impact', '') else "🟡"
                st.write(f"{impact} **{entry.title}** ({entry.country})")
        except:
            st.error("Calendar feed offline.")

    # --- 6. HISTORY ---
    st.divider()
    st.subheader("📝 Live Market Log")
    st.dataframe(data[['Close', 'RSI', 'ADX_14', upper_col, lower_col]].tail(10))

else:
    st.info("🔄 Connecting to market data...")
