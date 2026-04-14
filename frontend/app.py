import streamlit as st
import requests
import os
from dotenv import load_dotenv
import yfinance as yf

load_dotenv()

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

st.set_page_config(page_title="AI Investment Committee", layout="wide")
st.title("🏛️ AI Investment Committee")

ticker = st.text_input("Enter Stock Ticker (e.g., AAPL, NVDA):", "NVDA").upper()

if st.button("Run Analysis"):
    with st.spinner(f"The Committee is researching {ticker}..."):
        try:
            response = requests.post(f"{BACKEND_URL}/api/analyze", json={"ticker": ticker})
            response.raise_for_status()
            data = response.json()
            
            # --- TOP SECTION: THE VERDICT ---
            st.divider()
            st.markdown(f"<h2 style='text-align: center;'>Recommendation for {ticker}</h2>", unsafe_allow_html=True)
            listing_line = " · ".join(filter(None, [
                data.get("company_name", ""),
                data.get("exchange", "N/A"),
                data.get("country", "N/A"),
            ]))
            if listing_line:
                st.markdown(
                    f"<p style='text-align:center; color:#555; margin-top:-10px;'>{listing_line}</p>",
                    unsafe_allow_html=True,
                )
            
            # Color code the verdict
            verdict = data.get("recommendation", "HOLD").upper()
            if "BUY" in verdict:
                st.success(f"### 🟢 FINAL VERDICT: BUY")
            elif "SELL" in verdict:
                st.error(f"### 🔴 FINAL VERDICT: SELL")
            else:
                st.warning(f"### 🟡 FINAL VERDICT: HOLD")

            st.markdown(f"**Confidence:** {data.get('confidence_score', 'N/A')}")
            st.markdown(f"**Why this call:** {data.get('rationale', 'N/A')}")
            
            st.divider()
            
            # --- MIDDLE SECTION: THE DATA ---
            col1, col2 = st.columns(2)
            with col1:
                st.subheader("📊 Quant Analyst")
                with st.container():
                    st.markdown(data["quant_data"])
                    stock = yf.Ticker(ticker)
                    history = stock.history(period="6mo")
                    if not history.empty:
                        st.subheader("📈 6-Month Price Trend")
                        st.line_chart(history["Close"])
                    else:
                        st.info("Chart data not available for this ticker.")

            with col2:
                st.subheader("📰 Risk Analyst")
                with st.container():
                    st.markdown(data["news_data"])
                
            # --- BOTTOM SECTION: THE MEMO ---
            st.subheader("📝 Portfolio Manager's Memo")
            with st.container():
                st.write(data["memo"])
            
        except Exception as e:
            st.error(f"Error communicating with backend: {e}")