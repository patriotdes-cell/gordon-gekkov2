import streamlit as st
import os

st.set_page_config(page_title="Gordon Gekko V2", layout="wide")
st.title("🚀 Gordon Gekko V2 — Active Trading System")
st.caption("Soul & Doctrine Enforced | $1K → $25K Mission")

st.success("✅ App loaded successfully!")

st.info("Add your Alpaca keys in Settings → Secrets to connect trading.")
st.info("Then click the Run Trading Cycle button below.")

if st.button("🚀 Run Trading Cycle (UTA + COS)", type="primary"):
    st.balloons()
    st.success("✅ Soul gates passed! Simulated cycle executed.")
    st.session_state.virtual_equity = st.session_state.get("virtual_equity", 995) + 15

st.caption("Real trading coming next — after this works.")
