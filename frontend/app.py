import os
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()
import streamlit as st
import requests

# The backend URL is determined by Docker Compose
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

st.set_page_config(page_title="AI Investment Committee", layout="wide")
st.title("🏛️ AI Investment Committee")

ticker = st.text_input("Enter Stock Ticker:", "NVDA").upper()

if st.button("Run Analysis"):
    with st.spinner("Agents are researching..."):
        try:
            response = requests.post(f"{BACKEND_URL}/api/analyze", json={"ticker": ticker})
            response.raise_for_status()
            data = response.json()
            
            col1, col2 = st.columns(2)
            with col1:
                st.subheader("📊 Quantitative Data")
                st.info(data["quant_data"])
            with col2:
                st.subheader("📰 Risk & News")
                st.warning(data["news_data"])
                
            st.divider()
            st.subheader("📝 Final Investment Memo")
            st.write(data["memo"])
            
        except Exception as e:
            st.error(f"Error communicating with backend: {e}")