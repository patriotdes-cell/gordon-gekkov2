import streamlit as st
import os
from datetime import datetime
from zoneinfo import ZoneInfo  # Modern replacement for pytz

# Alpaca imports
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import GetAssetsRequest, MarketOrderRequest
from alpaca.trading.enums import OrderSide, OrderType, TimeInForce, AssetClass

# ====================== CONFIG ======================
st.set_page_config(
    page_title="Gordon",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("💼 Gordon Gekko Trading Dashboard")
st.markdown("**Wall Street never sleeps.**")

# ====================== SIDEBAR ======================
with st.sidebar:
    st.header("🔑 Alpaca Credentials")
    api_key = st.text_input("API Key", type="password", value=os.getenv("ALPACA_API_KEY", ""))
    secret_key = st.text_input("Secret Key", type="password", value=os.getenv("ALPACA_SECRET_KEY", ""))
    is_paper = st.checkbox("Paper Trading", value=True)
    
    if st.button("Connect"):
        st.session_state.connected = True
        st.success("Connected to Alpaca!")

# ====================== MAIN APP ======================
if "connected" not in st.session_state:
    st.info("👈 Enter your Alpaca credentials in the sidebar to get started.")
    st.stop()

try:
    trading_client = TradingClient(api_key, secret_key, paper=is_paper)
    
    # Account Info
    account = trading_client.get_account()
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Equity", f"${float(account.equity):,.2f}")
    with col2:
        st.metric("Buying Power", f"${float(account.buying_power):,.2f}")
    with col3:
        st.metric("Cash", f"${float(account.cash):,.2f}")
    with col4:
        st.metric("Portfolio Value", f"${float(account.portfolio_value):,.2f}")

    # Current Time (NY timezone - market hours)
    ny_time = datetime.now(ZoneInfo("America/New_York"))
    st.caption(f"🕒 New York Time: {ny_time.strftime('%Y-%m-%d %H:%M:%S')}")

    # Positions
    st.subheader("📊 Current Positions")
    positions = trading_client.get_all_positions()
    
    if positions:
        pos_data = []
        for p in positions:
            pos_data.append({
                "Symbol": p.symbol,
                "Qty": float(p.qty),
                "Avg Price": float(p.avg_entry_price),
                "Market Value": float(p.market_value),
                "Unrealized P/L": float(p.unrealized_pl),
                "Unrealized P/L %": float(p.unrealized_plpc) * 100
            })
        st.dataframe(pos_data, use_container_width=True)
    else:
        st.info("No open positions yet.")

    # Quick Trade Section
    st.subheader("⚡ Quick Market Order")
    col_a, col_b = st.columns([3, 1])
    with col_a:
        symbol = st.text_input("Symbol", value="AAPL", max_chars=10).upper()
    with col_b:
        side = st.selectbox("Side", ["Buy", "Sell"])
    
    qty = st.number_input("Quantity", min_value=1, value=1)
    
    if st.button("🚀 Place Market Order", type="primary"):
        order_data = MarketOrderRequest(
            symbol=symbol,
            qty=qty,
            side=OrderSide.BUY if side == "Buy" else OrderSide.SELL,
            type=OrderType.MARKET,
            time_in_force=TimeInForce.DAY
        )
        order = trading_client.submit_order(order_data)
        st.success(f"Order submitted! ID: {order.id}")

except Exception as e:
    st.error(f"Error: {e}")
    st.info("Double-check your API keys and internet connection.")

# Footer
st.caption("Made with ❤️ for the Gordon Gekko vibe | Powered by Alpaca + Streamlit")
