import streamlit as st
from datetime import datetime
from zoneinfo import ZoneInfo
import yfinance as yf
import pandas as pd

from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest
from alpaca.trading.enums import OrderSide, OrderType, TimeInForce

st.set_page_config(page_title="Gordon Gekko", layout="wide", page_icon="💰")

st.title("💼 Gordon Gekko Trading Terminal")
st.markdown("**The game is rigged. Play it anyway.**")

# Secrets
api_key = st.secrets.get("ALPACA_API_KEY")
secret_key = st.secrets.get("ALPACA_SECRET_KEY")
paper = st.secrets.get("ALPACA_PAPER", "true").lower() == "true"

if not api_key or not secret_key:
    st.error("❌ Add your Alpaca credentials in Secrets")
    st.stop()

# Connect
@st.cache_resource
def get_client():
    return TradingClient(api_key, secret_key, paper=paper)

client = get_client()

# Account Info
try:
    account = client.get_account()
    col1, col2, col3, col4 = st.columns(4)
    with col1: st.metric("Equity", f"${float(account.equity):,.2f}")
    with col2: st.metric("Buying Power", f"${float(account.buying_power):,.2f}")
    with col3: st.metric("Cash", f"${float(account.cash):,.2f}")
    with col4: st.metric("Mode", "🟢 PAPER" if paper else "🔴 LIVE")
except:
    st.error("Could not connect to Alpaca")

st.caption(f"🕒 NY Time: {datetime.now(ZoneInfo('America/New_York')).strftime('%Y-%m-%d %H:%M:%S')}")

# ====================== SIMPLE CHART ======================
st.subheader("📈 Quick Chart")
symbol = st.text_input("Symbol", value="AAPL").upper().strip()

if symbol:
    with st.spinner("Loading chart..."):
        try:
            data = yf.download(symbol, period="3mo", progress=False)
            if not data.empty:
                st.line_chart(data['Close'])
                price = data['Close'].iloc[-1]
                st.metric("Current Price", f"${price:.2f}")
            else:
                st.warning("No data found")
        except:
            st.error("Could not load chart")

# ====================== QUICK TRADE ======================
st.subheader("⚡ Quick Trade")
col_a, col_b, col_c = st.columns([2,1,1])
with col_a:
    trade_symbol = st.text_input("Trade Symbol", value=symbol, key="trade_sym").upper()
with col_b:
    action = st.selectbox("Action", ["Buy", "Sell"])
with col_c:
    qty = st.number_input("Quantity", min_value=1, value=1)

if st.button("🚀 Submit Order", type="primary"):
    try:
        order = MarketOrderRequest(
            symbol=trade_symbol,
            qty=qty,
            side=OrderSide.BUY if action == "Buy" else OrderSide.SELL,
            type=OrderType.MARKET,
            time_in_force=TimeInForce.DAY
        )
        client.submit_order(order)
        st.success(f"✅ {action} order for {qty} {trade_symbol} submitted!")
    except Exception as e:
        st.error(f"Order failed: {e}")

# ====================== POSITIONS ======================
st.subheader("📍 Current Positions")
try:
    positions = client.get_all_positions()
    if positions:
        df = pd.DataFrame([{
            'Symbol': p.symbol,
            'Qty': float(p.qty),
            'Avg Price': float(p.avg_entry_price),
            'Market Value': float(p.market_value),
            'P/L $': float(p.unrealized_pl),
            'P/L %': round(float(p.unrealized_plpc)*100, 2)
        } for p in positions])
        st.dataframe(df, use_container_width=True)
    else:
        st.info("No open positions")
except:
    st.info("Positions will show here")

st.caption("Simplified Gordon Gekko V2 • Stable Version")
