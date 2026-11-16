import streamlit as st
import ccxt
import pandas as pd
import numpy as np
import time
from datetime import datetime

# Page Configuration
st.set_page_config(
    page_title="HalfTrend Multi-Pair Algo Platform",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for clean dark trading dashboard
st.markdown("""
<style>
    .stApp {
        background-color: #0b0e14;
        color: #e2e8f0;
    }
    .stButton>button {
        width: 100%;
        border-radius: 8px;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# Session State Initialization
if "bot_running" not in st.session_state:
    st.session_state.bot_running = False
if "trade_logs" not in st.session_state:
    st.session_state.trade_logs = []
if "pending_signals" not in st.session_state:
    st.session_state.pending_signals = []
if "loaded_pairs" not in st.session_state:
    st.session_state.loaded_pairs = []
if "connected_exchange_name" not in st.session_state:
    st.session_state.connected_exchange_name = ""
if "last_signal_candle" not in st.session_state:
    st.session_state.last_signal_candle = {}

# Header
st.title("📈 HalfTrend Multi-Pair Automated Trading Platform")
st.caption("Advanced HalfTrend Engine • ATR(100)/2 Risk Management • Bi-Directional Long & Short Active • Manual Approval Mode")

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

# Sidebar: 1. Connect Exchange
st.sidebar.header("🔌 1. Connect Exchange")
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
            st.sidebar.warning(f"Could not auto-fetch pairs: {err}")
            st.session_state.loaded_pairs = ["BTC/USD:USD", "ETH/USD:USD", "SOL/USD:USD", "XAU/USD:USD", "BTC/USDT:USDT", "ETH/USDT:USDT"]

if st.sidebar.button("🔄 Refresh Exchange Pairs"):
    st.cache_data.clear()
    pairs, err = fetch_exchange_pairs(selected_exchange)
    if pairs:
        st.session_state.loaded_pairs = pairs
        st.sidebar.success(f"✅ {len(pairs)} pairs loaded from {selected_exchange}!")

st.sidebar.caption(f"🟢 {len(st.session_state.loaded_pairs)} active pairs available on **{selected_exchange}**")

st.sidebar.markdown("---")
st.sidebar.header("⚙️ 2. HalfTrend & Signal Settings")

default_selections = []
for p in st.session_state.loaded_pairs:
    if any(p.startswith(prefix) for prefix in ["BTC/", "ETH/", "SOL/"]):
        default_selections.append(p)
    if len(default_selections) == 3:
        break
if not default_selections and st.session_state.loaded_pairs:
    default_selections = [st.session_state.loaded_pairs[0]]

selected_symbols = st.sidebar.multiselect(
    "📌 Multi-Asset Scanner Pairs (Max 5)",
    options=st.session_state.loaded_pairs,
    default=default_selections,
    max_selections=5,
    help="একসাথে সর্বোচ্চ ৫টি পেয়ার স্ক্যান হবে।"
)

custom_pair = st.sidebar.text_input("➕ Add Custom Pair (Optional)", placeholder="e.g. XAU/USDT:USDT")
if custom_pair.strip() and custom_pair.strip() not in selected_symbols:
    selected_symbols.append(custom_pair.strip())

timeframe = st.sidebar.selectbox("Chart Timeframe", ["1m", "5m", "15m", "30m", "1h", "4h"], index=2)
amplitude = st.sidebar.number_input("Amplitude (Lookback)", min_value=1, max_value=200, value=20, step=1)
channel_dev = st.sidebar.number_input("Channel Deviation", min_value=0.1, max_value=10.0, value=2.0, step=0.1)
base_risk_mult = st.sidebar.number_input("Base Risk Multiplier (ATR/2 x Mult)", min_value=0.5, max_value=15.0, value=3.0, step=0.1)

# SIGNAL MODE SELECTION
signal_mode = st.sidebar.selectbox(
    "🎯 Signal Generation Mode",
    [
        "Dynamic Both Directions (Active Long & Short on Flips/Pullbacks)",
        "Flexible Pullback Mode",
        "Strict Reversal (Only on HalfTrend Flip)"
    ],
    index=0,
    help="Dynamic Both Directions মোডে বুলিশ ও বেয়ারিশ উভয় সিগন্যালই (LONG এবং SHORT) সমানভাবে কাজ করবে।"
)

tp_target_choice = st.sidebar.selectbox("Active Take-Profit Target", ["TP1 (1x Risk)", "TP2 (2x Risk)", "TP3 (3x Risk)"], index=1)

st.sidebar.markdown("---")
st.sidebar.header("🛡️ 3. Execution & Capital")

capital_usdt = st.sidebar.number_input("Margin Per Trade ($)", min_value=5.0, value=150.0, step=10.0)
leverage = st.sidebar.slider("Set Leverage (x)", min_value=1, max_value=100, value=10)
max_open_trades = st.sidebar.slider("🛡️ Max Open Trades Limit", min_value=1, max_value=10, value=2)

execution_mode = st.sidebar.radio(
    "🎯 Trade Execution Mode", 
    ["Semi-Automatic (Manual Approval)", "Fully Automatic"], 
    index=0,
    help="Semi-Auto মোডে সিগন্যাল আসলে আপনার কনফার্মেশনের জন্য অপেক্ষা করবে।"
)

demo_mode = st.sidebar.checkbox("🧪 Paper Trading Mode (Safe Test)", value=True)

# HalfTrend Mathematical Engine (Pure Formula Logic)
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
    dev = channel_deviation * atr2

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
        # Dynamic Both Directions: Triggers on ANY trend flip OR strong rejection at HalfTrend line in either direction
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
            except:
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

        st.session_state.trade_logs.insert(0, sig_data)
        st.success(f"✅ Trade Executed ({sig_data['Mode']}) on {symbol}!")
    except Exception as ex_err:
        st.error(f"Execution Error on {sig_data['Pair']}: {str(ex_err)}")

# Top Overview Metrics
col1, col2, col3, col4 = st.columns(4)
col1.metric("Connected Exchange", selected_exchange)
col2.metric("Active Pairs", f"{len(selected_symbols)} Pairs ({timeframe})")
col3.metric("Mode", "Semi-Auto (Manual)" if "Semi-Automatic" in execution_mode else "Fully Auto")
col4.metric("Max Trades Limit", f"{len(st.session_state.trade_logs)} / {max_open_trades}")

if selected_symbols:
    st.caption(f"🎯 **Multi-Asset Watchlist:** {', '.join(selected_symbols)} | **Mode:** Bi-Directional Long & Short Active")

st.markdown("---")

# Manual Approval Notification Area (Supports Multiple Pending Signals)
if st.session_state.pending_signals:
    st.warning(f"🚨 **{len(st.session_state.pending_signals)} HalfTrend Signal(s) Waiting for Your Approval!**")
    for idx, sig in enumerate(list(st.session_state.pending_signals)):
        with st.container():
            pcol1, pcol2, pcol3, pcol4, pcol5, pcol6 = st.columns(6)
            pcol1.metric("Pair", sig["Pair"])
            pcol2.metric("Signal", sig["Side"])
            pcol3.metric("Entry", f"${sig['Entry Price']}")
            pcol4.metric("Stop Loss", f"${sig['Stop Loss']}")
            pcol5.metric("TP1 / TP2", f"${sig['TP1']} / ${sig['TP2']}")
            pcol6.metric("TP3 (3x)", f"${sig['TP3']}")
            st.info(f"📋 **{sig['Pair']} HalfTrend Setup:** Triggered at {sig['Time']} | Active Exchange Order TP: **${sig['Selected TP']}** ({tp_target_choice})")

            b_col1, b_col2, _ = st.columns([1, 1, 2])
            with b_col1:
                if st.button(f"✅ Approve & Execute {sig['Pair']}", key=f"app_{idx}_{sig['Pair']}", type="primary"):
                    if len(st.session_state.trade_logs) >= max_open_trades:
                        st.error(f"⚠️ Max Open Trades Limit ({max_open_trades}) পূর্ণ হয়ে গেছে!")
                    else:
                        execute_trade_action(sig, demo_mode, selected_exchange, api_key, api_secret, api_passphrase)
                        st.session_state.pending_signals.pop(idx)
                        st.rerun()
            with b_col2:
                if st.button(f"❌ Reject {sig['Pair']}", key=f"rej_{idx}_{sig['Pair']}"):
                    st.session_state.pending_signals.pop(idx)
                    st.rerun()
        st.markdown("---")

btn_col1, btn_col2, _ = st.columns([1, 1, 2])
with btn_col1:
    if st.button("🚀 Deploy & Start Multi-Pair HalfTrend", type="primary"):
        if not selected_symbols:
            st.error("⚠️ অন্তত ১টি বা তার বেশি পেয়ার সিলেক্ট করুন!")
        elif not demo_mode and (not api_key or not api_secret):
            st.error("⚠️ লাইভ ট্রেডের জন্য বাম পাশে API Key এবং Secret দিন অথবা Paper Trading Mode চালু করুন।")
        else:
            st.session_state.bot_running = True
with btn_col2:
    if st.button("🛑 Stop Strategy"):
        st.session_state.bot_running = False
        st.session_state.pending_signals = []

status_banner = st.empty()
live_scanner_placeholder = st.empty()

st.markdown("### 📜 Executed Trades & Signals Log")
log_placeholder = st.empty()
# Active Trades Management & Manual Close Section
if (
    'active_trades' in st.session_state
    and len(st.session_state.active_trades) > 0
):
  st.markdown('### 📊 Active Trades Management (PnL & Close)')

  for idx, trade in enumerate(st.session_state.active_trades):
    # ট্রেড ডিকশনারি থেকে মানগুলো নিরাপদে বের করে নেওয়া
    sym = trade.get('Pair', 'N/A')
    side = trade.get('Side', 'BUY')
    entry_price = trade.get('Entry Price', 0.0)
    qty = trade.get('Qty', 0.0)

    # লাইভ প্রাইস সেট করা
    current_price = locals().get('live_px', entry_price)

    # PnL হিসাব করা
    if side == 'BUY':
      pnl_usdt = (current_price - entry_price) * qty
      pnl_percent = (
          ((current_price - entry_price) / entry_price) * 100
          if entry_price > 0
          else 0.0
      )
    else:
      pnl_usdt = (entry_price - current_price) * qty
      pnl_percent = (
          ((entry_price - current_price) / entry_price) * 100
          if entry_price > 0
          else 0.0
      )

    # কলাম ও ক্লোজ বাটন ডিজাইন
    col_t1, col_t2, col_t3, col_t4 = st.columns([2, 2, 2, 1])
    with col_t1:
      st.write(f'**{sym}** ({side})')
      st.text(f'Entry: {entry_price}')
    with col_t2:
      st.text(f'Live: {current_price}')
    with col_t3:
      color = 'green' if pnl_usdt >= 0 else 'red'
      st.markdown(
          f"<span style='color:{color}; font-weight:bold;'>PnL: ${pnl_usdt:.2f}"
          f' ({pnl_percent:+.2f}%)</span>',
          unsafe_allow_html=True,
      )
    with col_t4:
      if st.button('Close', key=f'manual_close_{idx}'):
        trade['status'] = 'CLOSED_MANUAL'
        st.session_state.active_trades.pop(idx)
        st.success(f'{sym} manual closed successfully!')
        st.rerun()
  for idx, trade in enumerate(st.session_state.active_trades):
    sym = trade['Pair']
    side = trade['Side']
    entry_price = trade['Entry Price']
    qty = trade['Qty']

    # লাইভ প্রাইস বের করা (যদি স্ক্যানার থেকে পাওয়া যায়)
    current_price = locals().get('live_px', entry_price)

    # PnL হিসাব
    if side == 'BUY':
      pnl_usdt = (current_price - entry_price) * qty
      pnl_percent = ((current_price - entry_price) / entry_price) * 100
    else:
      pnl_usdt = (entry_price - current_price) * qty
      pnl_percent = ((entry_price - current_price) / entry_price) * 100

    # UI কলাম তৈরি
    col_t1, col_t2, col_t3, col_t4 = st.columns([2, 2, 2, 1])
    with col_t1:
      st.write(f'**{sym}** ({side})')
      st.text(f'Entry: {entry_price}')
    with col_t2:
      st.text(f'Live: {current_price}')
    with col_t3:
      color = 'green' if pnl_usdt >= 0 else 'red'
      st.markdown(
          f"<span style='color:{color}; font-weight:bold;'>PnL: ${pnl_usdt:.2f}"
          f' ({pnl_percent:+.2f}%)</span>',
          unsafe_allow_html=True,
      )
    with col_t4:
      if st.button('Close', key=f'manual_close_{idx}'):
        # ট্রেড ক্লোজ করার লজিক
        trade['status'] = 'CLOSED_MANUAL'
        # চাইলে ক্লোজড হিস্টরিতে পাঠাতে পারেন অথবা লিস্ট থেকে রিমুভ করতে পারেন
        st.session_state.active_trades.pop(idx)
        st.success(f'{sym} manual closed successfully!')
        st.rerun()

if st.session_state.bot_running:
    try:
        exchange = create_exchange_instance(selected_exchange, api_key, api_secret, api_passphrase)
        exchange.load_markets()

        mode_label = "LIVE" if not demo_mode else "PAPER TRADING"
        status_banner.success(f"🟢 {mode_label} ACTIVE on {selected_exchange} | HalfTrend Multi-Asset Scanner ({len(selected_symbols)} Pairs)")

        while st.session_state.bot_running:
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

                    scanner_rows.append({
                        "Pair": sym,
                        "Live Price": f"${live_px:,.4f}" if live_px < 10 else f"${live_px:,.2f}",
                        "HalfTrend Line": f"${res['ht_line']:,.4f}" if res['ht_line'] < 10 else f"${res['ht_line']:,.2f}",
                        "Multi-Asset Trend": res["trend"],
                        "Confirmed Signal": signal if signal else "Holding Trend..."
                    })

                    current_active_trades = len(st.session_state.trade_logs)

                    if signal in ["BUY", "SELL"]:
                        if st.session_state.last_signal_candle.get(sym) != candle_ts:
                            st.session_state.last_signal_candle[sym] = candle_ts
                            already_pending = any(p["Pair"] == sym for p in st.session_state.pending_signals)

                            if current_active_trades >= max_open_trades:
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
                                    st.toast(f"🔔 HalfTrend {signal} Signal on {sym}! Waiting for approval.")
                                    st.rerun()
                                else:
                                    execute_trade_action(sig_data=trade_payload, is_demo=demo_mode, ex_label=selected_exchange, key=api_key, secret=api_secret, pass_phrase=api_passphrase)

                except Exception as pair_err:
                    scanner_rows.append({
                        "Pair": sym,
                        "Live Price": "Error",
                        "HalfTrend Line": "-",
                        "Multi-Asset Trend": "Error",
                        "Confirmed Signal": str(pair_err)[:50]
                    })

            with live_scanner_placeholder.container():
                st.subheader(f"📡 Multi-Asset HalfTrend Dashboard ({now_str})")
                st.dataframe(pd.DataFrame(scanner_rows), use_container_width=True, hide_index=True)

            with log_placeholder.container():
                if st.session_state.trade_logs:
                    st.dataframe(pd.DataFrame(st.session_state.trade_logs), use_container_width=True)
                else:
                    st.info(f"🕒 `{now_str}` — সিলেক্ট করা **{len(selected_symbols)}টি পেয়ারে** HalfTrend সিগন্যাল স্ক্যান হচ্ছে...")

            time.sleep(10)

    except Exception as e:
        st.error(f"❌ Connection / Execution Error: {str(e)}")
        st.session_state.bot_running = False
else:
    status_banner.warning("⏸️ Strategy is currently Stopped. বাম পাশ থেকে সেটিংস চেক করে 'Deploy & Start Multi-Pair HalfTrend' ক্লিক করুন।")
    with log_placeholder.container():
        if st.session_state.trade_logs:
            st.dataframe(pd.DataFrame(st.session_state.trade_logs), use_container_width=True)
        else:
            st.write("🕒 বট বন্ধ রয়েছে। বাম পাশ থেকে পেয়ার সিলেক্ট করে ডিপ্লয় করুন।")
