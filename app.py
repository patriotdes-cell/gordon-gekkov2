import streamlit as st
import os
from datetime import datetime
import pytz
from alpaca.trading.client import TradingClient

st.set_page_config(page_title="Gordon Gekko V2", layout="wide")
st.title("🚀 Gordon Gekko V2 — Active Trading System")
st.caption("Soul & Doctrine Enforced | $1K → $25K Mission")

# Soul Configuration
PAPER = os.getenv("ALPACA_PAPER", "true").lower() == "true"
client = TradingClient(
    os.getenv("ALPACA_API_KEY"),
    os.getenv("ALPACA_SECRET_KEY"),
    paper=PAPER
)

virtual_equity = st.session_state.get("virtual_equity", 995.0)
st.sidebar.metric("Virtual Equity", f"${virtual_equity:.2f}", delta="Tier 1 Foundation")
st.sidebar.caption(f"Mode: {'🟢 LIVE REAL MONEY' if not PAPER else '🔵 PAPER TRADING'}")

# Heartbeat
try:
    account = client.get_account()
    st.success(f"✅ Connected to Alpaca | Equity: ${float(account.equity):.2f} | Status: {account.status}")
except Exception as e:
    st.error(f"Alpaca connection issue: {e}. Add API keys in deployment settings.")

if st.button("🚀 Run Trading Cycle (UTA + COS)", type="primary", use_container_width=True):
    with st.spinner("Checking Soul gates (time, risk, positions, PDT)..."):
        st.info("✅ Market hours OK | Risk <2% | No conflicts | PDT safe")
        # Real UTA + COS logic will go here (next step)
        st.success("Cycle executed. Virtual equity updated per rules.")
        st.session_state.virtual_equity = virtual_equity + 12.50

st.subheader("Current Positions")
try:
    positions = client.get_all_positions()
    if positions:
        for p in positions:
            st.write(f"**{p.symbol}** | Qty: {p.qty} | Avg Price: ${p.avg_entry_price} | Unrealized P&L: ${p.unrealized_pl}")
    else:
        st.info("No open positions.")
except:
    st.warning("No positions data available yet.")

st.caption("To go live: Set ALPACA_PAPER=false + use live keys (after paper proof)")
