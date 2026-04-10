import streamlit as st
import requests
import os
from dotenv import load_dotenv

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
            
            # Color code the verdict
            verdict = data.get("recommendation", "HOLD").upper()
            if "BUY" in verdict:
                st.success(f"### 🟢 FINAL VERDICT: BUY")
            elif "SELL" in verdict:
                st.error(f"### 🔴 FINAL VERDICT: SELL")
            else:
                st.warning(f"### 🟡 FINAL VERDICT: HOLD")
                
            st.divider()
            
            # --- MIDDLE SECTION: THE DATA ---
            col1, col2 = st.columns(2)
            with col1:
                st.subheader("📊 Quant Analyst")
                # Using a container to make it look like a distinct card
                with st.container(border=True):
                    st.markdown(data["quant_data"])
                    
            with col2:
                st.subheader("📰 Risk Analyst")
                with st.container(border=True):
                    st.markdown(data["news_data"])
                
            # --- BOTTOM SECTION: THE MEMO ---
            st.subheader("📝 Portfolio Manager's Memo")
            with st.container(border=True):
                st.write(data["memo"])
            
        except Exception as e:
            st.error(f"Error communicating with backend: {e}")