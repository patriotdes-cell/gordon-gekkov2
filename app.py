

import streamlit as st
import os
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
import pandas as pd
import yfinance as yf

from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest
from alpaca.trading.enums import OrderSide, OrderType, TimeInForce

st.set_page_config(page_title="Gordon Gekko", layout="wide", page_icon="💰")

st.title("💼 Gordon Gekko Trading Terminal")
st.markdown("**The game is rigged. Play it anyway.**")

# Load secrets
api_key = st.secrets.get("ALPACA_API_KEY")
secret_key = st.secrets.get("ALPACA_SECRET_KEY")
paper = st.secrets.get("ALPACA_PAPER", "true").lower() == "true"

if not api_key or not secret_key:
    st.error("❌ Missing Alpaca credentials in Secrets")
    st.stop()

# Connect to Alpaca
@st.cache_resource
def get_client():
    return TradingClient(api_key, secret_key, paper=paper)

client = get_client()

try:
    account = client.get_account()
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Equity", f"${float(account.equity):,.2f}")
    with col2:
        st.metric("Buying Power", f"${float(account.buying_power):,.2f}")
    with col3:
        st.metric("Cash", f"${float(account.cash):,.2f}")
    with col4:
        st.metric("Mode", "🟢 PAPER" if paper else "🔴 LIVE")
except Exception as e:
    st.error(f"Alpaca Error: {e}")
    st.stop()

ny_time = datetime.now(ZoneInfo("America/New_York"))
st.caption(f"🕒 New York Time: {ny_time.strftime('%Y-%m-%d %H:%M:%S')}")

# ====================== WATCHLIST ======================
st.subheader("📋 Watchlist")
watchlist_symbols = st.multiselect("Add symbols", 
                                 ["AAPL", "TSLA", "NVDA", "AMZN", "GOOGL", "SPY", "QQQ"], 
                                 default=["AAPL", "TSLA", "NVDA"])

# ====================== CHARTS & SIGNALS ======================
st.subheader("📈 Live Charts + Signals")
symbol = st.text_input("Enter Symbol for Chart", value="AAPL").upper().strip()

if symbol:
    with st.spinner(f"Loading {symbol}..."):
        # Use 6 months so MA200 works
        data = yf.download(symbol, period="6mo", interval="1d", progress=False)
        
        if not data.empty:
            # Calculate MAs safely
            data['MA50'] = data['Close'].rolling(window=50).mean()
            data['MA200'] = data['Close'].rolling(window=200).mean()
            
            latest = data.iloc[-1]
            
            # Safe signal logic
            if pd.isna(latest['MA50']) or pd.isna(latest['MA200']):
                signal = "⏳ Not enough data for signal"
                signal_color = "⚪"
            elif latest['MA50'] > latest['MA200']:
                signal = "🟢 BULLISH"
                signal_color = "🟢"
            else:
                signal = "🔴 BEARISH"
                signal_color = "🔴"
            
            col_chart, col_signals = st.columns([3, 1])
            
            with col_chart:
                st.line_chart(data['Close'], use_container_width=True)
            
            with col_signals:
                st.metric("Signal", signal)
                st.metric("Current Price", f"${latest['Close']:.2f}")
                change = ((latest['Close'] / data.iloc[-2]['Close']) - 1) * 100 if len(data) > 1 else 0
                st.metric("Daily Change", f"{change:.2f}%")
                
                # Quick orders
                if st.button(f"🚀 Quick Buy 1 {symbol}", type="primary"):
                    try:
                        order = MarketOrderRequest(symbol=symbol, qty=1, side=OrderSide.BUY,
                                                 type=OrderType.MARKET, time_in_force=TimeInForce.DAY)
                        client.submit_order(order)
                        st.success(f"✅ Buy order submitted for {symbol}!")
                    except Exception as e:
                        st.error(f"Buy failed: {e}")
                
                if st.button(f"🔻 Quick Sell 1 {symbol}"):
                    try:
                        order = MarketOrderRequest(symbol=symbol, qty=1, side=OrderSide.SELL,
                                                 type=OrderType.MARKET, time_in_force=TimeInForce.DAY)
                        client.submit_order(order)
                        st.success(f"✅ Sell order submitted for {symbol}!")
                    except Exception as e:
                        st.error(f"Sell failed: {e}")
        else:
            st.error(f"Could not load data for {symbol}")

# ====================== PORTFOLIO & POSITIONS ======================
st.subheader("📊 Portfolio Performance")
try:
    history = client.get_portfolio_history(timeframe="1D", limit=100)
    if history and history.equity:
        df = pd.DataFrame({'timestamp': history.timestamp, 'equity': history.equity})
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='s')
        st.line_chart(df.set_index('timestamp')['equity'])
except:
    st.info("Portfolio history loading...")

st.subheader("📍 Current Positions")
try:
    positions = client.get_all_positions()
    if positions:
        pos_df = pd.DataFrame([{
            'Symbol': p.symbol,
            'Qty': float(p.qty),
            'Avg Price': float(p.avg_entry_price),
            'Market Value': float(p.market_value),
            'Unrealized P/L': float(p.unrealized_pl),
            'P/L %': round(float(p.unrealized_plpc)*100, 2)
        } for p in positions])
        st.dataframe(pos_df, use_container_width=True)
    else:
        st.info("No open positions yet.")
except Exception as e:
    st.warning("Could not load positions.")

st.caption("Gordon Gekko V2 • Fixed & Upgraded")
