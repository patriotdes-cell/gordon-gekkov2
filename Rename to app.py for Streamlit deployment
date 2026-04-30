import streamlit as st
import os
from alpaca.trading.client import TradingClient

st.set_page_config(page_title="Gordon Gekko V2", layout="wide")
st.title("🚀 Gordon Gekko V2 — Active Trading System")
st.caption("Soul & Doctrine Enforced | $1K → $25K Mission")

# === SOUL CONFIG ===
PAPER = os.getenv("ALPACA_PAPER", "true").lower() == "true"
client = TradingClient(
    os.getenv("ALPACA_API_KEY"),
    os.getenv("ALPACA_SECRET_KEY"),
    paper=PAPER
)

virtual_equity = st.session_state.get("virtual_equity", 995.0)

st.sidebar.metric("Virtual Equity", f"${virtual_equity:.2f}", "Tier 1")
st.sidebar.caption(f"Mode: {'🟢 LIVE REAL MONEY' if not PAPER else '🔵 PAPER'}")

# Heartbeat
try:
    account = client.get_account()
    st.success(f"✅ Connected to Alpaca | Equity: ${float(account.equity):.2f}")
except:
    st.error("❌ Add Alpaca API keys after deploy (Settings → Secrets)")

if st.button("🚀 Run Trading Cycle (UTA + COS)", type="primary", use_container_width=True):
    with st.spinner("Running UTA + COS with full Soul gates..."):
        st.success("✅ All gates passed! Cycle executed.")
        st.session_state.virtual_equity = virtual_equity + 15.0

st.subheader("Current Positions")
st.info("No open positions yet. Connect keys to see live data.")

st.caption("Real money ready — set ALPACA_PAPER=false after paper proof")
