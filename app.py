import streamlit as st
import ccxt
import pandas as pd
import numpy as np
import time
from datetime import datetime

# Page Configuration
st.set_page_config(
    page_title="Deployed Strategies | HalfTrend Algo",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS - Exact Replica of Algopulse Dark SaaS UI
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    /* Main Pure Obsidian Dark Background */
    .stApp {
        background-color: #07090e;
        color: #f8fafc;
    }

    /* Top Header Padding Adjustment */
    .block-container {
        padding-top: 1.2rem !important;
        padding-bottom: 3rem !important;
        max-width: 1380px !important;
    }

    /* Hide default Streamlit top bar elements for clean SaaS look */
    header[data-testid="stHeader"] {
        background-color: rgba(7, 9, 14, 0.85);
        backdrop-filter: blur(12px);
    }

    /* Top SaaS Navbar */
    .ap-navbar {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 10px 0 18px 0;
        border-bottom: 1px solid #161b26;
        margin-bottom: 24px;
    }
    .ap-nav-left {
        display: flex;
        align-items: center;
        gap: 28px;
    }
    .ap-brand {
        font-size: 1.35rem;
        font-weight: 800;
        color: #ffffff;
        letter-spacing: -0.03em;
    }
    .ap-nav-links {
        display: flex;
        align-items: center;
        gap: 10px;
    }
    .ap-nav-item {
        color: #8b95a5;
        font-size: 0.88rem;
        font-weight: 500;
        padding: 7px 14px;
        border-radius: 8px;
        display: inline-flex;
        align-items: center;
        gap: 6px;
    }
    .ap-nav-item.active {
        background-color: #111c33;
        color: #3b82f6;
        border: 1px solid #1d3566;
        font-weight: 600;
    }
    .ap-nav-right {
        display: flex;
        align-items: center;
        gap: 14px;
    }
    .ap-avatar-pill {
        display: inline-flex;
        align-items: center;
        gap: 9px;
        background-color: #0e121b;
        border: 1px solid #1a202c;
        padding: 4px 12px 4px 5px;
        border-radius: 999px;
        font-size: 0.84rem;
        color: #e2e8f0;
        font-weight: 500;
    }
    .ap-avatar-circle {
        width: 26px;
        height: 26px;
        border-radius: 50%;
        background-color: #172554;
        color: #60a5fa;
        font-size: 0.72rem;
        font-weight: 700;
        display: flex;
        align-items: center;
        justify-content: center;
    }

    /* Page Title Header */
    .ap-page-title {
        font-size: 1.65rem;
        font-weight: 700;
        color: #ffffff;
        margin: 0;
        letter-spacing: -0.02em;
    }
    .ap-page-sub {
        color: #7c8594;
        font-size: 0.88rem;
        margin-top: 3px;
        margin-bottom: 20px;
    }

    /* Hero Summary Container (Exact Algopulse Box) */
    .ap-hero-box {
        background-color: #0c0f16;
        border: 1px solid #181e2a;
        border-radius: 14px;
        overflow: hidden;
        margin-bottom: 20px;
    }
    .ap-hero-top {
        padding: 24px 28px;
        border-bottom: 1px solid #181e2a;
    }
    .ap-hero-label {
        color: #8b95a5;
        font-size: 0.84rem;
        font-weight: 500;
        margin-bottom: 6px;
    }
    .ap-hero-value {
        font-size: 2.35rem;
        font-weight: 800;
        color: #ffffff;
        letter-spacing: -0.03em;
        line-height: 1.1;
    }
    .ap-hero-value span.decimals {
        font-size: 1.45rem;
        color: #64748b;
        font-weight: 700;
    }
    .ap-hero-badge-row {
        display: flex;
        align-items: center;
        gap: 10px;
        margin-top: 12px;
    }
    .ap-pnl-pill {
        background-color: #141923;
        border: 1px solid #222938;
        color: #94a3b8;
        font-size: 0.78rem;
        font-weight: 600;
        padding: 3px 10px;
        border-radius: 999px;
    }
    .ap-pnl-pill.pos {
        background-color: rgba(34, 197, 94, 0.12);
        border-color: rgba(34, 197, 94, 0.3);
        color: #4ade80;
    }
    .ap-pnl-pill.neg {
        background-color: rgba(239, 68, 68, 0.12);
        border-color: rgba(239, 68, 68, 0.3);
        color: #f87171;
    }
    .ap-hero-across {
        color: #64748b;
        font-size: 0.8rem;
    }

    /* 4-Column Sub-Stats Grid inside Hero Box */
    .ap-stats-grid {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
    }
    .ap-stat-cell {
        padding: 20px 28px;
        border-right: 1px solid #181e2a;
    }
    .ap-stat-cell:last-child {
        border-right: none;
    }
    .ap-stat-num {
        font-size: 1.35rem;
        font-weight: 700;
        color: #ffffff;
    }
    .ap-stat-num span.muted {
        font-size: 0.9rem;
        color: #64748b;
        font-weight: 500;
    }
    .ap-stat-title {
        font-size: 0.82rem;
        color: #cbd5e1;
        font-weight: 500;
        margin-top: 4px;
    }
    .ap-stat-sub {
        font-size: 0.75rem;
        color: #64748b;
        margin-top: 2px;
    }
    .ap-winrate-wrap {
        display: flex;
        align-items: center;
        gap: 14px;
        height: 100%;
    }
    .ap-winrate-ring {
        width: 38px;
        height: 38px;
        border-radius: 50%;
        border: 2px solid #262f40;
        display: flex;
        align-items: center;
        justify-content: center;
        color: #94a3b8;
        font-weight: 600;
        font-size: 0.9rem;
    }

    /* Strategy Row Card (Exact Algopulse Bottom Row) */
    .ap-strategy-row {
        background-color: #0c0f16;
        border: 1px solid #181e2a;
        border-radius: 12px;
        padding: 16px 24px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 12px;
        transition: border-color 0.2s ease;
    }
    .ap-strategy-row:hover {
        border-color: #293548;
    }
    .ap-strat-left {
        display: flex;
        align-items: center;
        gap: 14px;
    }
    .ap-strat-icon {
        width: 38px;
        height: 38px;
        border-radius: 50%;
        background-color: #131c31;
        border: 1px solid #1e2d4d;
        color: #60a5fa;
        font-weight: 700;
        font-size: 0.95rem;
        display: flex;
        align-items: center;
        justify-content: center;
        position: relative;
    }
    .ap-status-dot {
        width: 9px;
        height: 9px;
        border-radius: 50%;
        background-color: #22c55e;
        border: 2px solid #0c0f16;
        position: absolute;
        bottom: 0;
        right: 0;
    }
    .ap-status-dot.stopped {
        background-color: #64748b;
    }
    .ap-strat-name {
        font-size: 0.96rem;
        font-weight: 600;
        color: #f8fafc;
    }
    .ap-strat-meta {
        font-size: 0.79rem;
        color: #7c8594;
        margin-top: 2px;
    }
    .ap-strat-meta strong {
        color: #cbd5e1;
        font-weight: 600;
    }
    .ap-strat-right {
        display: flex;
        align-items: center;
        gap: 36px;
        text-align: right;
    }
    .ap-metric-col-label {
        font-size: 0.72rem;
        color: #64748b;
        margin-bottom: 3px;
    }
    .ap-metric-col-val {
        font-size: 0.9rem;
        font-weight: 600;
        color: #f1f5f9;
    }
    .ap-metric-col-val.green {
        color: #22c55e;
    }
    .ap-metric-col-val.red {
        color: #ef4444;
    }
    .ap-metric-col-sub {
        font-size: 0.72rem;
        color: #22c55e;
    }
    .ap-metric-col-sub.red {
        color: #ef4444;
    }

    /* Action Buttons Styling */
    .stButton>button {
        background-color: #131823;
        color: #e2e8f0;
        border: 1px solid #232b3b;
        border-radius: 8px;
        font-size: 0.84rem;
        font-weight: 600;
        padding: 0.45rem 0.9rem;
        transition: all 0.15s ease;
    }
    .stButton>button:hover {
        background-color: #1c2434;
        border-color: #3b82f6;
        color: #ffffff;
    }
    button[kind="primary"] {
        background-color: #2563eb !important;
        border-color: #2563eb !important;
        color: #ffffff !important;
    }
    button[kind="primary"]:hover {
        background-color: #1d4ed8 !important;
    }

    /* Sidebar Dark Match */
    section[data-testid="stSidebar"] {
        background-color: #090c12;
        border-right: 1px solid #161b26;
    }

    /* Responsive adjustments */
    @media (max-width: 768px) {
        .ap-stats-grid {
            grid-template-columns: repeat(2, 1fr);
        }
        .ap-strategy-row {
            flex-direction: column;
            align-items: flex-start;
            gap: 14px;
        }
        .ap-strat-right {
            width: 100%;
            justify-content: space-between;
            gap: 12px;
            text-align: left;
        }
    }
</style>
""", unsafe_allow_html=True)

# Session State Initialization
if "bot_running" not in st.session_state:
    st.session_state.bot_running = False
if "trade_logs" not in st.session_state:
    st.session_state.trade_logs = []
if "active_trades" not in st.session_state:
    st.session_state.active_trades = []
if "pending_signals" not in st.session_state:
    st.session_state.pending_signals = []
if "loaded_pairs" not in st.session_state:
    st.session_state.loaded_pairs = []
if "connected_exchange_name" not in st.session_state:
    st.session_state.connected_exchange_name = ""
if "last_signal_candle" not in st.session_state:
    st.session_state.last_signal_candle = {}
if "latest_prices" not in st.session_state:
    st.session_state.latest_prices = {}
if "show_scanner" not in st.session_state:
    st.session_state.show_scanner = True

# Supported Exchanges Map
EXCHANGE_OPTIONS = {
    "Delta Exchange India": "delta_india",
    "Delta Exchange Global": "delta",
    "Binance Futures": "binance",
    "Bybit": "bybit",
    "OKX": "okx",
    "Bitget": "bitget",
    "MEXC": "mexc",
    "Gate.io": "gate",
    "KuCoin Futures": "kucoinfutures"
}

# Initialize Exchange Function
def create_exchange_instance(selected_label, key="", secret="", password=""):
    ex_id = EXCHANGE_OPTIONS[selected_label]
    common_config = {
        'apiKey': key if key else '',
        'secret': secret if secret else '',
        'enableRateLimit': True,
        'options': {'defaultType': 'swap'}
    }
    if password:
        common_config['password'] = password

    if ex_id == "delta_india":
        exchange = ccxt.delta(common_config)
        exchange.options['defaultType'] = 'future'
        exchange.urls['api']['public'] = 'https://api.india.delta.exchange'
        exchange.urls['api']['private'] = 'https://api.india.delta.exchange'
    elif ex_id == "delta":
        exchange = ccxt.delta(common_config)
        exchange.options['defaultType'] = 'future'
    elif ex_id == "binance":
        common_config['options']['defaultType'] = 'future'
        exchange = ccxt.binance(common_config)
    elif ex_id == "bybit":
        exchange = ccxt.bybit(common_config)
    elif ex_id == "okx":
        exchange = ccxt.okx(common_config)
    elif ex_id == "bitget":
        exchange = ccxt.bitget(common_config)
    elif ex_id == "mexc":
        exchange = ccxt.mexc(common_config)
    elif ex_id == "gate":
        exchange = ccxt.gate(common_config)
    elif ex_id == "kucoinfutures":
        exchange = ccxt.kucoinfutures(common_config)
    else:
        exchange = ccxt.delta(common_config)

    return exchange

# Fetch Active Futures/Perpetual Pairs from Connected Exchange
@st.cache_data(ttl=300, show_spinner=False)
def fetch_exchange_pairs(selected_label):
    try:
        ex = create_exchange_instance(selected_label)
        markets = ex.load_markets()
        active_pairs = []
        for sym, m in markets.items():
            if m.get('active', True) and (m.get('swap') or m.get('future') or m.get('contract')):
                active_pairs.append(sym)
        if not active_pairs:
            active_pairs = [sym for sym, m in markets.items() if m.get('active', True)]
        return sorted(active_pairs), None
    except Exception as e:
        return [], str(e)

# Sidebar Configuration (Accessible anytime via top-left arrow)
st.sidebar.header("🔌 1. Connect Broker / Exchange")
selected_exchange = st.sidebar.selectbox("Select Exchange", list(EXCHANGE_OPTIONS.keys()))

api_key = st.sidebar.text_input("API Key", type="password", placeholder="Enter API Key")
api_secret = st.sidebar.text_input("API Secret", type="password", placeholder="Enter API Secret")
api_passphrase = ""
if selected_exchange in ["OKX", "Bitget", "KuCoin Futures"]:
    api_passphrase = st.sidebar.text_input("API Passphrase", type="password", placeholder="Required for OKX/Bitget/KuCoin")

if st.session_state.connected_exchange_name != selected_exchange or not st.session_state.loaded_pairs:
    with st.spinner(f"Loading active pairs from {selected_exchange}..."):
        pairs, err = fetch_exchange_pairs(selected_exchange)
        if pairs:
            st.session_state.loaded_pairs = pairs
            st.session_state.connected_exchange_name = selected_exchange
        else:
            st.session_state.loaded_pairs = ["ETH/USD:USD", "BTC/USD:USD", "SOL/USD:USD", "DOGE/USD:USD", "BTC/USDT:USDT", "ETH/USDT:USDT"]

if st.sidebar.button("🔄 Refresh Exchange Pairs"):
    st.cache_data.clear()
    pairs, err = fetch_exchange_pairs(selected_exchange)
    if pairs:
        st.session_state.loaded_pairs = pairs
        st.sidebar.success(f"✅ {len(pairs)} pairs loaded!")

st.sidebar.markdown("---")
st.sidebar.header("⚙️ 2. Strategy & Pairs")

strategy_display_name = st.sidebar.text_input("Strategy Name", value="HalfTrend Momentum Core")

default_selections = []
for p in st.session_state.loaded_pairs:
    if any(p.startswith(prefix) for prefix in ["ETH/", "BTC/", "SOL/"]):
        default_selections.append(p)
    if len(default_selections) == 3:
        break
if not default_selections and st.session_state.loaded_pairs:
    default_selections = [st.session_state.loaded_pairs[0]]

selected_symbols = st.sidebar.multiselect(
    "📌 Active Pairs (Max 5)",
    options=st.session_state.loaded_pairs,
    default=default_selections,
    max_selections=5
)

custom_pair = st.sidebar.text_input("➕ Add Custom Pair", placeholder="e.g. XAU/USDT:USDT")
if custom_pair.strip() and custom_pair.strip() not in selected_symbols:
    selected_symbols.append(custom_pair.strip())

timeframe = st.sidebar.selectbox("Chart Timeframe", ["1m", "5m", "15m", "30m", "1h", "4h"], index=2)
amplitude = st.sidebar.number_input("Amplitude (Lookback)", min_value=1, max_value=200, value=20, step=1)
channel_dev = st.sidebar.number_input("Channel Deviation", min_value=0.1, max_value=10.0, value=2.0, step=0.1)
base_risk_mult = st.sidebar.number_input("Risk Multiplier (ATR/2 x Mult)", min_value=0.5, max_value=15.0, value=3.0, step=0.1)

signal_mode = st.sidebar.selectbox(
    "🎯 Signal Generation Mode",
    [
        "Dynamic Both Directions (Active Long & Short on Flips/Pullbacks)",
        "Flexible Pullback Mode",
        "Strict Reversal (Only on HalfTrend Flip)"
    ],
    index=0
)

tp_target_choice = st.sidebar.selectbox("Take-Profit Target", ["TP1 (1x Risk)", "TP2 (2x Risk)", "TP3 (3x Risk)"], index=1)

st.sidebar.markdown("---")
st.sidebar.header("🛡️ 3. Capital & Execution")

capital_usdt = st.sidebar.number_input("Invested Capital ($)", min_value=5.0, value=150.0, step=10.0)
leverage = st.sidebar.slider("Set Leverage (x)", min_value=1, max_value=100, value=10)
max_open_trades = st.sidebar.slider("Max Open Positions", min_value=1, max_value=10, value=2)

execution_mode = st.sidebar.radio(
    "Execution Mode", 
    ["Semi-Automatic (Manual Approval)", "Fully Automatic"], 
    index=0
)

demo_mode = st.sidebar.checkbox("🧪 Paper Trading Mode (Safe Test)", value=True)

# HalfTrend Mathematical Engine
def calculate_halftrend_signals(df, amplitude=20, channel_deviation=2.0, base_risk_mult=3.0, mode="Dynamic"):
    n = len(df)
    high = df['high'].values
    low = df['low'].values
    close = df['close'].values
    open_p = df['open'].values

    prev_close = np.roll(close, 1)
    prev_close[0] = close[0]
    tr = np.maximum(high - low, np.maximum(np.abs(high - prev_close), np.abs(low - prev_close)))
    atr100 = pd.Series(tr).ewm(alpha=1/100, adjust=False).mean().values
    atr2 = atr100 / 2.0

    highma = pd.Series(high).rolling(window=amplitude, min_periods=1).mean().values
    lowma = pd.Series(low).rolling(window=amplitude, min_periods=1).mean().values

    highest_high = pd.Series(high).rolling(window=amplitude, min_periods=1).max().values
    lowest_low = pd.Series(low).rolling(window=amplitude, min_periods=1).min().values

    trend = np.zeros(n, dtype=int)
    next_trend = 0
    max_low_price = low[0]
    min_high_price = high[0]
    up = np.zeros(n)
    down = np.zeros(n)
    ht_line = np.zeros(n)

    for i in range(n):
        hp = highest_high[i]
        lp = lowest_low[i]
        prev_low = low[i-1] if i > 0 else low[i]
        prev_high = high[i-1] if i > 0 else high[i]

        if i == 0:
            trend[i] = 0
            up[i] = lp
            down[i] = hp
            ht_line[i] = up[i]
            continue

        trend[i] = trend[i-1]

        if next_trend == 1:
            max_low_price = max(lp, max_low_price)
            if highma[i] < max_low_price and close[i] < prev_low:
                trend[i] = 1
                next_trend = 0
                min_high_price = hp
        else:
            min_high_price = min(hp, min_high_price)
            if lowma[i] > min_high_price and close[i] > prev_high:
                trend[i] = 0
                next_trend = 1
                max_low_price = lp

        if trend[i] == 0:
            if trend[i-1] != 0:
                up[i] = down[i-1]
            else:
                up[i] = max(max_low_price, up[i-1])
            down[i] = down[i-1]
            ht_line[i] = up[i]
        else:
            if trend[i-1] != 1:
                down[i] = up[i-1]
            else:
                down[i] = min(min_high_price, down[i-1])
            up[i] = up[i-1]
            ht_line[i] = down[i]

    confirmed_idx = -2
    prev_idx = -3

    curr_trend = trend[confirmed_idx]
    prev_trend = trend[prev_idx]
    entry_px = close[confirmed_idx]
    live_px = close[-1]
    candle_ts = df['timestamp'].iloc[confirmed_idx]
    ht_val = ht_line[confirmed_idx]

    dist = atr2[confirmed_idx] * base_risk_mult
    trend_flipped = (curr_trend != prev_trend)

    is_green = close[confirmed_idx] > open_p[confirmed_idx]
    is_red = close[confirmed_idx] < open_p[confirmed_idx]

    if mode.startswith("Strict"):
        buy_signal = (curr_trend == 0) and trend_flipped
        sell_signal = (curr_trend == 1) and trend_flipped
    elif mode.startswith("Flexible"):
        bullish_dip = (curr_trend == 0) and (low[confirmed_idx] <= ht_val * 1.008) and is_green
        bearish_rally = (curr_trend == 1) and (high[confirmed_idx] >= ht_val * 0.992) and is_red
        buy_signal = (trend_flipped and curr_trend == 0) or bullish_dip
        sell_signal = (trend_flipped and curr_trend == 1) or bearish_rally
    else:
        bullish_trigger = (trend_flipped and curr_trend == 0) or ((curr_trend == 0) and (low[confirmed_idx] <= ht_val * 1.01) and is_green)
        bearish_trigger = (trend_flipped and curr_trend == 1) or ((curr_trend == 1) and (high[confirmed_idx] >= ht_val * 0.99) and is_red)
        buy_signal = bullish_trigger
        sell_signal = bearish_trigger

    signal = None
    sl = 0.0
    tp1 = 0.0
    tp2 = 0.0
    tp3 = 0.0

    if buy_signal:
        signal = "BUY"
        sl = entry_px - dist
        tp1 = entry_px + dist
        tp2 = entry_px + (dist * 2)
        tp3 = entry_px + (dist * 3)
    elif sell_signal:
        signal = "SELL"
        sl = entry_px + dist
        tp1 = entry_px - dist
        tp2 = entry_px - (dist * 2)
        tp3 = entry_px - (dist * 3)

    trend_label = "LONG (Bullish)" if curr_trend == 0 else "SHORT (Bearish)"
    return {
        "signal": signal,
        "trend": trend_label,
        "ht_line": ht_val,
        "live_price": live_px,
        "entry_price": entry_px,
        "sl": sl,
        "tp1": tp1,
        "tp2": tp2,
        "tp3": tp3,
        "candle_ts": candle_ts
    }

def execute_trade_action(sig_data, is_demo, ex_label, key, secret, pass_phrase):
    try:
        ex = create_exchange_instance(ex_label, key, secret, pass_phrase)
        ex.load_markets()
        
        symbol = sig_data["Pair"]
        signal = sig_data["Side"]
        qty = sig_data["Qty"]
        sl = sig_data["Stop Loss"]
        tp = sig_data["Selected TP"]

        if not is_demo:
            try:
                ex.set_leverage(sig_data["LeverageNum"], symbol)
            except Exception:
                pass
            sl_prec = float(ex.price_to_precision(symbol, sl))
            tp_prec = float(ex.price_to_precision(symbol, tp))
            if signal == "BUY":
                ex.create_market_buy_order(symbol, qty, params={'stopLoss': sl_prec, 'takeProfit': tp_prec})
            else:
                ex.create_market_sell_order(symbol, qty, params={'stopLoss': sl_prec, 'takeProfit': tp_prec})
            sig_data["Mode"] = "LIVE"
        else:
            sig_data["Mode"] = "PAPER"

        sig_data["Status"] = "OPEN"
        st.session_state.active_trades.insert(0, sig_data.copy())
        st.session_state.trade_logs.insert(0, sig_data.copy())
        st.toast(f"✅ Trade Executed ({sig_data['Mode']}) on {symbol}!")
    except Exception as ex_err:
        st.error(f"Execution Error on {sig_data['Pair']}: {str(ex_err)}")

def close_active_trade(idx, is_demo, ex_label, key, secret, pass_phrase):
    trade = st.session_state.active_trades[idx]
    symbol = trade["Pair"]
    side = trade["Side"]
    qty = trade["Qty"]
    entry_px = trade["Entry Price"]
    exit_px = st.session_state.latest_prices.get(symbol, entry_px)

    try:
        if not is_demo and trade.get("Mode") == "LIVE":
            ex = create_exchange_instance(ex_label, key, secret, pass_phrase)
            ex.load_markets()
            if side == "BUY":
                ex.create_market_sell_order(symbol, qty, params={'reduceOnly': True})
            else:
                ex.create_market_buy_order(symbol, qty, params={'reduceOnly': True})

        pnl_usdt = (exit_px - entry_px) * qty if side == "BUY" else (entry_px - exit_px) * qty
        closed_record = trade.copy()
        closed_record["Status"] = "CLOSED"
        closed_record["Exit Price"] = round(exit_px, 4)
        closed_record["Realized PnL ($)"] = round(pnl_usdt, 2)
        closed_record["Closed Time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        st.session_state.trade_logs.insert(0, closed_record)
        st.session_state.active_trades.pop(idx)
        st.toast(f"✅ {symbol} Closed | PnL: ${pnl_usdt:+.2f}")
    except Exception as err:
        st.error(f"Error closing {symbol}: {str(err)}")

# --- Calculate Real-Time Portfolio Metrics ---
unrealized_pnl = 0.0
for t in st.session_state.active_trades:
    cur_p = st.session_state.latest_prices.get(t["Pair"], t["Entry Price"])
    if t["Side"] == "BUY":
        unrealized_pnl += (cur_p - t["Entry Price"]) * t["Qty"]
    else:
        unrealized_pnl += (t["Entry Price"] - cur_p) * t["Qty"]

closed_trades = [t for t in st.session_state.trade_logs if t.get("Status") == "CLOSED"]
realized_pnl = sum(float(t.get("Realized PnL ($)", 0.0)) for t in closed_trades)
winning_trades = [t for t in closed_trades if float(t.get("Realized PnL ($)", 0.0)) > 0]

total_pnl = realized_pnl + unrealized_pnl
current_val = capital_usdt + total_pnl
pnl_pct = (total_pnl / capital_usdt * 100) if capital_usdt > 0 else 0.0

whole_part = int(current_val)
dec_part = f"{abs(current_val - whole_part):.2f}"[1:]  # e.g., ".00"

win_rate_display = f"{int(len(winning_trades)/len(closed_trades)*100)}%" if closed_trades else "—"
win_rate_sub = f"{len(winning_trades)} won of {len(closed_trades)} closed" if closed_trades else "shows after the first close"

pill_cls = "pos" if total_pnl > 0 else ("neg" if total_pnl < 0 else "")
pnl_sign = "+" if total_pnl > 0 else ("-" if total_pnl < 0 else "")

active_strat_num = "1" if st.session_state.bot_running else "0"
active_strat_sub = "strategies running" if st.session_state.bot_running else "strategy stopped"

open_pos_count = len(st.session_state.active_trades)
open_pos_sub = f"{open_pos_count} active right now" if open_pos_count > 0 else "none right now"
total_trades_count = len(closed_trades) + open_pos_count

# --- 1. EXACT ALGOPULSE TOP NAVIGATION BAR ---
st.markdown(f"""
<div class="ap-navbar">
    <div class="ap-nav-left">
        <div class="ap-brand">Algopulse</div>
        <div class="ap-nav-links">
            <span class="ap-nav-item">⊞ Dashboard</span>
            <span class="ap-nav-item">⚡ Strategies</span>
            <span class="ap-nav-item">🔌 Brokers</span>
            <span class="ap-nav-item active">🚀 Deployed</span>
            <span class="ap-nav-item">📊 Reports</span>
        </div>
    </div>
    <div class="ap-nav-right">
        <span style="color:#8b95a5; font-size:0.9rem;">🌙</span>
        <span style="color:#8b95a5; font-size:0.9rem;">🔔</span>
        <div class="ap-avatar-pill">
            <span class="ap-avatar-circle">HT</span>
            <span>HalfTrend Desk</span>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# --- 2. PAGE HEADER & QUICK CONTROLS ---
hdr_col1, hdr_col2, hdr_col3 = st.columns([3.5, 1, 1])
with hdr_col1:
    st.markdown("""
    <h1 class="ap-page-title">Deployed Strategies</h1>
    <div class="ap-page-sub">Monitor all your running strategies and their trades</div>
    """, unsafe_allow_html=True)
with hdr_col2:
    st.write("")
    if not st.session_state.bot_running:
        if st.button("🚀 Start Strategy", type="primary"):
            if not selected_symbols:
                st.error("⚠️ অন্তত ১টি পেয়ার সিলেক্ট করুন!")
            elif not demo_mode and (not api_key or not api_secret):
                st.error("⚠️ API Key/Secret দিন অথবা Paper Mode চালু করুন।")
            else:
                st.session_state.bot_running = True
                st.rerun()
    else:
        if st.button("🛑 Stop Strategy"):
            st.session_state.bot_running = False
            st.session_state.pending_signals = []
            st.rerun()
with hdr_col3:
    st.write("")
    if st.button("⚙️ Configure"):
        st.info("👈 বাম পাশের সাইডবার (Top-Left `>` বাটন) থেকে এক্সচেঞ্জ, ক্যাপিটাল ও স্ট্র্যাটেজি সেটিংস পরিবর্তন করুন।")

# --- 3. EXACT ALGOPULSE HERO PORTFOLIO CARD ---
st.markdown(f"""
<div class="ap-hero-box">
    <div class="ap-hero-top">
        <div class="ap-hero-label">Current value</div>
        <div class="ap-hero-value">${whole_part:,}<span class="decimals">{dec_part}</span></div>
        <div class="ap-hero-badge-row">
            <span class="ap-pnl-pill {pill_cls}">• {pnl_sign}${abs(total_pnl):.2f} · {pnl_pct:+.2f}%</span>
            <span class="ap-hero-across">across 1 strategy ({'Paper Test' if demo_mode else 'LIVE'})</span>
        </div>
    </div>
    <div class="ap-stats-grid">
        <div class="ap-stat-cell">
            <div class="ap-stat-num">{active_strat_num} <span class="muted">/ 1</span></div>
            <div class="ap-stat-title">Active</div>
            <div class="ap-stat-sub">{active_strat_sub}</div>
        </div>
        <div class="ap-stat-cell">
            <div class="ap-stat-num">{open_pos_count}</div>
            <div class="ap-stat-title">Open positions</div>
            <div class="ap-stat-sub">{open_pos_sub}</div>
        </div>
        <div class="ap-stat-cell">
            <div class="ap-stat-num">{total_trades_count}</div>
            <div class="ap-stat-title">Trades</div>
            <div class="ap-stat-sub">{open_pos_count} open</div>
        </div>
        <div class="ap-stat-cell">
            <div class="ap-winrate-wrap">
                <div class="ap-winrate-ring">{win_rate_display}</div>
                <div>
                    <div class="ap-stat-title" style="margin-top:0;">Win rate</div>
                    <div class="ap-stat-sub">{win_rate_sub}</div>
                </div>
            </div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# --- 4. FILTER & VIEW BAR ---
f_col1, f_col2, f_col3 = st.columns([1, 4, 1])
with f_col1:
    st.button("🎛️ Filters", disabled=True)
with f_col3:
    toggle_label = "Hide Scanner" if st.session_state.show_scanner else "Show Scanner"
    if st.button(f"⊞ {toggle_label}"):
        st.session_state.show_scanner = not st.session_state.show_scanner
        st.rerun()

# --- 5. EXACT ALGOPULSE DEPLOYED STRATEGY ROW CARD ---
pairs_label = ", ".join([s.split(":")[0] for s in selected_symbols]) if selected_symbols else "No Pairs"
dot_cls = "" if st.session_state.bot_running else "stopped"
realized_cls = "green" if realized_pnl >= 0 else "red"
total_cls = "green" if total_pnl >= 0 else "red"
win_pct_short = f"{int(len(winning_trades)/len(closed_trades)*100)}%" if closed_trades else "0%"

st.markdown(f"""
<div class="ap-strategy-row">
    <div class="ap-strat-left">
        <div class="ap-strat-icon">
            {strategy_display_name[0].upper() if strategy_display_name else 'H'}
            <span class="ap-status-dot {dot_cls}"></span>
        </div>
        <div>
            <div class="ap-strat-name">{strategy_display_name}</div>
            <div class="ap-strat-meta">{pairs_label} · {selected_exchange} · <strong>{leverage}x leverage</strong></div>
        </div>
    </div>
    <div class="ap-strat-right">
        <div>
            <div class="ap-metric-col-label">Invested</div>
            <div class="ap-metric-col-val">${capital_usdt:,.0f}</div>
        </div>
        <div>
            <div class="ap-metric-col-label">Win / Trades</div>
            <div class="ap-metric-col-val">{win_pct_short} / {total_trades_count}</div>
        </div>
        <div>
            <div class="ap-metric-col-label">Realized today</div>
            <div class="ap-metric-col-val {realized_cls}">{realized_pnl:+.2f}</div>
        </div>
        <div>
            <div class="ap-metric-col-label">PnL</div>
            <div class="ap-metric-col-val {total_cls}">{total_pnl:+.2f}</div>
            <div class="ap-metric-col-sub {total_cls}">{pnl_pct:+.1f}%</div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# --- 6. MANUAL APPROVAL SIGNALS (SEMI-AUTO) ---
if st.session_state.pending_signals:
    st.warning(f"🚨 **{len(st.session_state.pending_signals)} HalfTrend Signal(s) Waiting for Approval**")
    for idx, sig in enumerate(list(st.session_state.pending_signals)):
        with st.container():
            pcol1, pcol2, pcol3, pcol4, pcol5, pcol6 = st.columns(6)
            pcol1.metric("Pair", sig["Pair"])
            pcol2.metric("Signal", sig["Side"])
            pcol3.metric("Entry", f"${sig['Entry Price']}")
            pcol4.metric("Stop Loss", f"${sig['Stop Loss']}")
            pcol5.metric("TP1 / TP2", f"${sig['TP1']} / ${sig['TP2']}")
            pcol6.metric("TP3 (3x)", f"${sig['TP3']}")

            b_col1, b_col2, _ = st.columns([1.2, 1.2, 3.6])
            with b_col1:
                if st.button(f"✅ Approve {sig['Pair']}", key=f"app_{idx}_{sig['Pair']}_{sig['Time']}", type="primary"):
                    if len(st.session_state.active_trades) >= max_open_trades:
                        st.error(f"⚠️ Max Open Trades Limit ({max_open_trades}) পূর্ণ হয়ে গেছে!")
                    else:
                        execute_trade_action(sig, demo_mode, selected_exchange, api_key, api_secret, api_passphrase)
                        st.session_state.pending_signals.pop(idx)
                        st.rerun()
            with b_col2:
                if st.button(f"❌ Reject {sig['Pair']}", key=f"rej_{idx}_{sig['Pair']}_{sig['Time']}"):
                    st.session_state.pending_signals.pop(idx)
                    st.rerun()

# --- 7. OPEN POSITIONS & INSTANT MANUAL CLOSE ---
active_trades_placeholder = st.empty()

def render_active_trades():
    with active_trades_placeholder.container():
        if st.session_state.active_trades:
            st.markdown("#### ⚡ Active Open Positions")
            for idx, trade in enumerate(list(st.session_state.active_trades)):
                sym = trade.get('Pair', 'N/A')
                side = trade.get('Side', 'BUY')
                entry_price = float(trade.get('Entry Price', 0.0))
                qty = float(trade.get('Qty', 0.0))
                current_price = float(st.session_state.latest_prices.get(sym, entry_price))

                if side == 'BUY':
                    t_pnl = (current_price - entry_price) * qty
                    t_pct = ((current_price - entry_price) / entry_price) * 100 if entry_price > 0 else 0.0
                else:
                    t_pnl = (entry_price - current_price) * qty
                    t_pct = ((entry_price - current_price) / entry_price) * 100 if entry_price > 0 else 0.0

                c1, c2, c3, c4, c5 = st.columns([2, 1.4, 1.4, 1.8, 1.2])
                with c1:
                    side_clr = "#22c55e" if side == "BUY" else "#ef4444"
                    st.markdown(f"**{sym}** <span style='color:{side_clr}; font-weight:700;'>[{side}]</span>", unsafe_allow_html=True)
                    st.caption(f"Qty: {qty} · {trade.get('Leverage', '10x')} ({trade.get('Mode', 'PAPER')})")
                with c2:
                    st.caption("Entry Price")
                    st.write(f"${entry_price:,.4f}" if entry_price < 10 else f"${entry_price:,.2f}")
                with c3:
                    st.caption("Live Price")
                    st.write(f"${current_price:,.4f}" if current_price < 10 else f"${current_price:,.2f}")
                with c4:
                    st.caption("Unrealized PnL")
                    p_clr = "#22c55e" if t_pnl >= 0 else "#ef4444"
                    st.markdown(f"<span style='color:{p_clr}; font-weight:700;'>${t_pnl:+.2f} ({t_pct:+.2f}%)</span>", unsafe_allow_html=True)
                with c5:
                    st.write("")
                    if st.button("✖ Close", key=f"close_btn_{idx}_{sym}_{trade.get('Time', '')}"):
                        close_active_trade(idx, demo_mode, selected_exchange, api_key, api_secret, api_passphrase)
                        st.rerun()

if not st.session_state.bot_running:
    render_active_trades()

live_scanner_placeholder = st.empty()
log_placeholder = st.empty()

# --- 8. LIVE MARKET SCANNER ENGINE ---
if st.session_state.bot_running:
    try:
        exchange = create_exchange_instance(selected_exchange, api_key, api_secret, api_passphrase)
        exchange.load_markets()

        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        scanner_rows = []

        for sym in selected_symbols:
            try:
                bars = exchange.fetch_ohlcv(sym, timeframe=timeframe, limit=150)
                df = pd.DataFrame(bars, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])

                res = calculate_halftrend_signals(df, amplitude, channel_dev, base_risk_mult, signal_mode)
                signal = res["signal"]
                live_px = res["live_price"]
                entry_px = res["entry_price"]
                candle_ts = res["candle_ts"]

                st.session_state.latest_prices[sym] = live_px

                scanner_rows.append({
                    "Pair": sym,
                    "Live Price": f"${live_px:,.4f}" if live_px < 10 else f"${live_px:,.2f}",
                    "HalfTrend Line": f"${res['ht_line']:,.4f}" if res['ht_line'] < 10 else f"${res['ht_line']:,.2f}",
                    "Trend": res["trend"],
                    "Signal": signal if signal else "Holding Trend..."
                })

                current_active_count = len(st.session_state.active_trades)

                if signal in ["BUY", "SELL"]:
                    if st.session_state.last_signal_candle.get(sym) != candle_ts:
                        st.session_state.last_signal_candle[sym] = candle_ts
                        already_pending = any(p["Pair"] == sym for p in st.session_state.pending_signals)

                        if current_active_count >= max_open_trades:
                            st.toast(f"⚠️ Max Open Trades ({max_open_trades}) reached. Skipped {sym}.")
                        elif not already_pending:
                            raw_qty = (capital_usdt * leverage) / live_px
                            qty = float(exchange.amount_to_precision(sym, raw_qty))
                            chosen_tp = res["tp1"] if "TP1" in tp_target_choice else (res["tp2"] if "TP2" in tp_target_choice else res["tp3"])

                            trade_payload = {
                                "Time": now_str,
                                "Exchange": selected_exchange,
                                "Pair": sym,
                                "Side": signal,
                                "Qty": qty,
                                "Entry Price": round(entry_px, 4),
                                "Stop Loss": round(res["sl"], 4),
                                "TP1": round(res["tp1"], 4),
                                "TP2": round(res["tp2"], 4),
                                "TP3": round(res["tp3"], 4),
                                "Selected TP": round(chosen_tp, 4),
                                "Leverage": f"{leverage}x",
                                "LeverageNum": leverage
                            }

                            if "Semi-Automatic" in execution_mode:
                                st.session_state.pending_signals.append(trade_payload)
                                st.toast(f"🔔 HalfTrend {signal} Signal on {sym}!")
                                st.rerun()
                            else:
                                execute_trade_action(sig_data=trade_payload, is_demo=demo_mode, ex_label=selected_exchange, key=api_key, secret=api_secret, pass_phrase=api_passphrase)

            except Exception as pair_err:
                scanner_rows.append({
                    "Pair": sym,
                    "Live Price": "Error",
                    "HalfTrend Line": "-",
                    "Trend": "Error",
                    "Signal": str(pair_err)[:50]
                })

        render_active_trades()

        if st.session_state.show_scanner:
            with live_scanner_placeholder.container():
                st.markdown(f"#### 📡 Live Multi-Asset Scanner ({now_str})")
                st.dataframe(pd.DataFrame(scanner_rows), use_container_width=True, hide_index=True)

        if st.session_state.trade_logs:
            with log_placeholder.container():
                st.markdown("#### 📜 Trade History Log")
                st.dataframe(pd.DataFrame(st.session_state.trade_logs), use_container_width=True, hide_index=True)

        time.sleep(10)
        st.rerun()

    except Exception as e:
        st.error(f"❌ Connection / Execution Error: {str(e)}")
        st.session_state.bot_running = False
else:
    if st.session_state.trade_logs:
        with log_placeholder.container():
            st.markdown("#### 📜 Trade History Log")
            st.dataframe(pd.DataFrame(st.session_state.trade_logs), use_container_width=True, hide_index=True)
