import streamlit as st

# 1. Set up the page title and icon
st.set_page_config(page_title="Forex Tracker", page_icon="📈")

# 2. Add a Header
st.title("🌍 Currency Exchange Tracker")
st.write("Welcome to your digital forex management tool.")

# 3. Create an Input Area
st.subheader("Convert Currency")
col1, col2 = st.columns(2)

with col1:
    amount = st.number_input("Enter Amount:", min_value=0.0, value=1.0)
    from_currency = st.selectbox("From:", ["USD", "UGX", "EUR", "GBP"])

with col2:
    to_currency = st.selectbox("To:", ["UGX", "USD", "EUR", "GBP"])

# 4. Simple Logic (Example Rates)
# In a real app, you could connect this to an API for live rates
rates = {
    "USD_to_UGX": 3800,
    "UGX_to_USD": 0.00026,
}

if st.button("Calculate"):
    if from_currency == "USD" and to_currency == "UGX":
        result = amount * rates["USD_to_UGX"]
        st.success(f"{amount} USD is approximately {result:,.0f} UGX")
    else:
        st.info("Calculation for this pair is coming soon!")

# 5. Add a Footer or Sidebar
st.sidebar.header("Settings")
st.sidebar.write("This app is powered by Streamlit.")
