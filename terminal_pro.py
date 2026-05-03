import streamlit as st
import yfinance as yf
import pandas as pd
import ta
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
import requests
from datetime import datetime, timedelta
import feedparser
import time

# ══════════════════════════════════════════════════════════════
# CONFIGURACIÓN DE PÁGINA
# ══════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="NAPOLITANO TERMINAL PRO",
    layout="wide",
    initial_sidebar_state="expanded",
    page_icon="📡"
)

# ══════════════════════════════════════════════════════════════
# ESTADO DE SESIÓN
# ══════════════════════════════════════════════════════════════
if 'favoritos' not in st.session_state:
    st.session_state.favoritos = ["GGAL.BA", "YPFD.BA", "AAPL", "MSFT", "MELI", "VIST", "TGSU2.BA", "BTC-USD", "GC=F", "CL=F"]
if 'alertas' not in st.session_state:
    st.session_state.alertas = {}
if 'notas' not in st.session_state:
    st.session_state.notas = {}

# ══════════════════════════════════════════════════════════════
# CSS BLOOMBERG-STYLE
# ══════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@300;400;600;700&family=Bebas+Neue&display=swap');

:root {
    --bg-primary: #060A0F;
    --bg-secondary: #0D1520;
    --bg-card: #111B27;
    --bg-hover: #162133;
    --accent-orange: #FF6B1A;
    --accent-cyan: #00D4FF;
    --accent-green: #00FF88;
    --accent-red: #FF3366;
    --accent-yellow: #FFD700;
    --text-primary: #E8EDF5;
    --text-secondary: #7A8BA0;
    --border: #1E2D3D;
    --border-accent: rgba(255,107,26,0.25);
}

.stApp {
    background-color: var(--bg-primary);
    font-family: 'JetBrains Mono', monospace;
}

/* HEADER TERMINAL */
.terminal-header {
    background: linear-gradient(135deg, #060A0F 0%, #0D1520 50%, #060A0F 100%);
    border-bottom: 2px solid var(--accent-orange);
    padding: 12px 20px;
    display: flex;
    align-items: center;
    gap: 20px;
    margin-bottom: 20px;
    position: relative;
    overflow: hidden;
}

.terminal-header::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0; bottom: 0;
    background: repeating-linear-gradient(
        90deg,
        transparent,
        transparent 80px,
        rgba(255,107,26,0.03) 80px,
        rgba(255,107,26,0.03) 81px
    );
}

.terminal-logo {
    font-family: 'Bebas Neue', sans-serif;
    font-size: 28px;
    color: var(--accent-orange);
    letter-spacing: 4px;
    text-shadow: 0 0 20px rgba(255,107,26,0.40);
    z-index: 1;
}

.terminal-ticker {
    font-size: 11px;
    color: var(--text-secondary);
    z-index: 1;
}

/* PRECIO */
.price-giant {
    font-family: 'JetBrains Mono', monospace;
    font-size: 48px;
    font-weight: 700;
    color: var(--text-primary);
    letter-spacing: -1px;
    line-height: 1;
}

.delta-up { color: var(--accent-green); font-size: 22px; font-weight: 600; }
.delta-down { color: var(--accent-red); font-size: 22px; font-weight: 600; }
.company-name { color: var(--accent-cyan); font-size: 14px; letter-spacing: 2px; text-transform: uppercase; }
.market-badge {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 4px;
    padding: 2px 8px;
    font-size: 10px;
    color: var(--text-secondary);
}

/* CARDS */
.metric-card {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-left: 3px solid var(--accent-orange);
    border-radius: 6px;
    padding: 14px 18px;
    margin: 4px 0;
    transition: all 0.2s;
}

.metric-card:hover {
    border-color: var(--accent-cyan);
    background: var(--bg-hover);
    box-shadow: 0 0 20px rgba(0,212,255,0.08);
}

.metric-label {
    font-size: 9px;
    color: var(--text-secondary);
    letter-spacing: 2px;
    text-transform: uppercase;
    margin-bottom: 4px;
}

.metric-value {
    font-size: 20px;
    font-weight: 600;
    color: var(--text-primary);
}

/* SCORE BULL/BEAR */
.score-container {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 20px;
    text-align: center;
}

.score-number {
    font-family: 'Bebas Neue', sans-serif;
    font-size: 72px;
    line-height: 1;
}

.score-bullish { color: var(--accent-green); text-shadow: 0 0 30px rgba(0,255,136,0.40); }
.score-bearish { color: var(--accent-red); text-shadow: 0 0 30px rgba(255,51,102,0.40); }
.score-neutral { color: var(--accent-yellow); text-shadow: 0 0 30px rgba(255,215,0,0.40); }

/* SEÑALES */
.signal-buy {
    background: linear-gradient(135deg, #003320, #001A10);
    border: 1px solid #00FF88;
    border-radius: 8px;
    padding: 14px 18px;
    font-size: 14px;
    color: #00FF88;
    font-weight: 600;
}

.signal-sell {
    background: linear-gradient(135deg, #330020, #1A0010);
    border: 1px solid #FF3366;
    border-radius: 8px;
    padding: 14px 18px;
    font-size: 14px;
    color: #FF3366;
    font-weight: 600;
}

.signal-hold {
    background: linear-gradient(135deg, #1A1500, #0D0B00);
    border: 1px solid #FFD700;
    border-radius: 8px;
    padding: 14px 18px;
    font-size: 14px;
    color: #FFD700;
    font-weight: 600;
}

/* NOTICIAS */
.news-item {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 6px;
    padding: 12px 16px;
    margin: 6px 0;
    cursor: pointer;
    transition: all 0.2s;
}

.news-item:hover {
    border-color: var(--accent-orange);
    background: var(--bg-hover);
}

.news-source {
    font-size: 9px;
    color: var(--accent-orange);
    letter-spacing: 2px;
    text-transform: uppercase;
}

.news-title {
    font-size: 13px;
    color: var(--text-primary);
    margin: 4px 0;
    line-height: 1.4;
}

.news-time { font-size: 10px; color: var(--text-secondary); }

/* WATCHLIST */
.watchlist-item {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 6px;
    padding: 10px 14px;
    margin: 4px 0;
    display: flex;
    justify-content: space-between;
    align-items: center;
    transition: all 0.2s;
}

.watchlist-item:hover { background: var(--bg-hover); }

/* SECTION HEADERS */
.section-hdr {
    font-family: 'Bebas Neue', sans-serif;
    font-size: 20px;
    color: var(--accent-orange);
    letter-spacing: 3px;
    border-bottom: 1px solid var(--border);
    padding-bottom: 8px;
    margin: 24px 0 12px 0;
}

/* STATUS BAR */
.status-bar {
    background: var(--bg-secondary);
    border-bottom: 1px solid var(--border);
    padding: 6px 20px;
    font-size: 10px;
    color: var(--text-secondary);
    display: flex;
    gap: 20px;
    align-items: center;
}

.status-dot-green { color: var(--accent-green); }
.status-dot-red { color: var(--accent-red); }

/* SIDEBAR */
section[data-testid="stSidebar"] {
    background: var(--bg-secondary) !important;
    border-right: 1px solid var(--border) !important;
}

/* INPUTS */
.stTextInput > div > div > input {
    background: var(--bg-card) !important;
    border: 1px solid var(--border) !important;
    color: var(--text-primary) !important;
    font-family: 'JetBrains Mono', monospace !important;
    border-radius: 4px !important;
}

.stTextInput > div > div > input:focus {
    border-color: var(--accent-orange) !important;
    box-shadow: 0 0 10px rgba(255,107,26,0.20) !important;
}

/* BOTONES */
.stButton > button {
    background: transparent !important;
    border: 1px solid var(--accent-orange) !important;
    color: var(--accent-orange) !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 12px !important;
    border-radius: 4px !important;
    transition: all 0.2s !important;
}

.stButton > button:hover {
    background: var(--accent-orange) !important;
    color: var(--bg-primary) !important;
    box-shadow: 0 0 15px rgba(255,107,26,0.27) !important;
}

/* TOGGLE */
.stToggle {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 14px !important;
    font-weight: 700 !important;
    color: #FFFFFF !important;
}

.stToggle label,
.stToggle p,
.stToggle span {
    color: #FFFFFF !important;
    font-weight: 700 !important;
    font-size: 14px !important;
}

/* SIDEBAR - texto blanco y grueso */
section[data-testid="stSidebar"] p,
section[data-testid="stSidebar"] label,
section[data-testid="stSidebar"] span,
section[data-testid="stSidebar"] div {
    color: #FFFFFF !important;
    font-weight: 700 !important;
}

section[data-testid="stSidebar"] .stMarkdown p {
    color: #FFFFFF !important;
    font-weight: 700 !important;
    font-size: 14px !important;
    letter-spacing: 1px !important;
}

/* DATAFRAME */
.stDataFrame {
    border: 1px solid var(--border) !important;
    border-radius: 6px !important;
}

/* LIVE BLINKER */
@keyframes blink {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.2; }
}

.live-dot {
    display: inline-block;
    width: 8px;
    height: 8px;
    background: var(--accent-green);
    border-radius: 50%;
    animation: blink 1.2s infinite;
    margin-right: 6px;
    box-shadow: 0 0 8px #00FF88;
}

/* FIBONCCI TABLE */
.fib-row {
    display: flex;
    justify-content: space-between;
    padding: 6px 12px;
    border-bottom: 1px solid var(--border);
    font-size: 12px;
}

.fib-row:last-child { border-bottom: none; }

/* SCROLLBAR */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: var(--bg-primary); }
::-webkit-scrollbar-thumb { background: var(--border); border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: var(--accent-orange); }

/* GAUGE */
.gauge-container { position: relative; margin: 0 auto; }

/* DIVIDER */
hr { border-color: var(--border) !important; }

/* TABS */
.stTabs [data-baseweb="tab-list"] {
    background: var(--bg-secondary) !important;
    gap: 2px;
}
.stTabs [data-baseweb="tab"] {
    background: transparent !important;
    color: var(--text-secondary) !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 11px !important;
    letter-spacing: 1px !important;
    border-bottom: 2px solid transparent !important;
}
.stTabs [aria-selected="true"] {
    color: var(--accent-orange) !important;
    border-bottom-color: var(--accent-orange) !important;
}

/* SELECTBOX */
.stSelectbox > div > div {
    background: var(--bg-card) !important;
    border: 1px solid var(--border) !important;
    color: var(--text-primary) !important;
    font-family: 'JetBrains Mono', monospace !important;
}

/* Ocultar decoracion de streamlit */
#MainMenu { visibility: hidden; }
footer { visibility: hidden; }
header { visibility: hidden; }

/* ALERTA CARD */
.alert-triggered {
    background: linear-gradient(135deg, #1A0A00, #0D0500);
    border: 2px solid var(--accent-orange);
    border-radius: 8px;
    padding: 12px 16px;
    animation: pulse 2s infinite;
}

@keyframes pulse {
    0%, 100% { box-shadow: 0 0 5px rgba(255,107,26,0.27); }
    50% { box-shadow: 0 0 20px rgba(255,107,26,0.53); }
}
</style>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════
# CLASES DE DATOS
# ══════════════════════════════════════════════════════════════

class StockData:
    @st.cache_data(ttl=45)
    def get_data(ticker, period="2y"):
        try:
            stock = yf.Ticker(ticker)
            df = stock.history(period=period)
            if df.empty:
                return None, None, {}

            df = df.copy()

            # ── Indicadores Técnicos (librería ta) ───────────
            # RSI
            df['RSI']   = ta.momentum.RSIIndicator(df['Close'], window=14).rsi()
            df['RSI_9'] = ta.momentum.RSIIndicator(df['Close'], window=9).rsi()

            # MACD
            _macd = ta.trend.MACD(df['Close'], window_slow=26, window_fast=12, window_sign=9)
            df['MACD_12_26_9']  = _macd.macd()
            df['MACDs_12_26_9'] = _macd.macd_signal()
            df['MACDh_12_26_9'] = _macd.macd_diff()

            # EMAs / SMAs
            df['EMA_9']   = ta.trend.EMAIndicator(df['Close'], window=9).ema_indicator()
            df['EMA_21']  = ta.trend.EMAIndicator(df['Close'], window=21).ema_indicator()
            df['EMA_50']  = ta.trend.EMAIndicator(df['Close'], window=50).ema_indicator()
            df['EMA_100'] = ta.trend.EMAIndicator(df['Close'], window=100).ema_indicator()
            df['EMA_200'] = ta.trend.EMAIndicator(df['Close'], window=200).ema_indicator()
            df['SMA_50']  = ta.trend.SMAIndicator(df['Close'], window=50).sma_indicator()
            df['SMA_200'] = ta.trend.SMAIndicator(df['Close'], window=200).sma_indicator()

            # Bollinger Bands
            _bb = ta.volatility.BollingerBands(df['Close'], window=20, window_dev=2)
            df['BBU_20_2'] = _bb.bollinger_hband()
            df['BBM_20_2'] = _bb.bollinger_mavg()
            df['BBL_20_2'] = _bb.bollinger_lband()

            # ATR
            df['ATR'] = ta.volatility.AverageTrueRange(df['High'], df['Low'], df['Close'], window=14).average_true_range()

            # ADX
            _adx = ta.trend.ADXIndicator(df['High'], df['Low'], df['Close'], window=14)
            df['ADX_14'] = _adx.adx()

            # Stochastic
            _stoch = ta.momentum.StochasticOscillator(df['High'], df['Low'], df['Close'], window=14)
            df['STOCHk_14'] = _stoch.stoch()
            df['STOCHd_14'] = _stoch.stoch_signal()

            # Williams %R
            df['WR'] = ta.momentum.WilliamsRIndicator(df['High'], df['Low'], df['Close'], lbp=14).williams_r()

            # CCI
            df['CCI'] = ta.trend.CCIIndicator(df['High'], df['Low'], df['Close'], window=20).cci()

            # OBV
            df['OBV'] = ta.volume.OnBalanceVolumeIndicator(df['Close'], df['Volume']).on_balance_volume()

            # MFI
            df['MFI'] = ta.volume.MFIIndicator(df['High'], df['Low'], df['Close'], df['Volume'], window=14).money_flow_index()

            # VWAP
            try:
                df['VWAP'] = ta.volume.VolumeWeightedAveragePrice(df['High'], df['Low'], df['Close'], df['Volume']).volume_weighted_average_price()
            except:
                pass

            # SuperTrend (calculado manualmente)
            def _supertrend(high, low, close, period=7, mult=3):
                atr_val = ta.volatility.AverageTrueRange(high, low, close, window=period).average_true_range()
                hl2 = (high + low) / 2
                upper = hl2 + mult * atr_val
                lower = hl2 - mult * atr_val
                st_val = pd.Series(np.nan, index=close.index)
                st_dir = pd.Series(np.nan, index=close.index)
                for i in range(1, len(close)):
                    if pd.isna(atr_val.iloc[i]):
                        continue
                    upper.iloc[i] = min(upper.iloc[i], upper.iloc[i-1]) if close.iloc[i-1] <= upper.iloc[i-1] else upper.iloc[i]
                    lower.iloc[i] = max(lower.iloc[i], lower.iloc[i-1]) if close.iloc[i-1] >= lower.iloc[i-1] else lower.iloc[i]
                    if close.iloc[i] > upper.iloc[i-1]:
                        st_dir.iloc[i] = 1
                    elif close.iloc[i] < lower.iloc[i-1]:
                        st_dir.iloc[i] = -1
                    else:
                        st_dir.iloc[i] = st_dir.iloc[i-1] if pd.notna(st_dir.iloc[i-1]) else 1
                    st_val.iloc[i] = lower.iloc[i] if st_dir.iloc[i] == 1 else upper.iloc[i]
                return st_val, st_dir

            df['SUPERT_7_3'], df['SUPERTd_7_3'] = _supertrend(df['High'], df['Low'], df['Close'], 7, 3)

            # Ichimoku simplificado
            try:
                _ichi = ta.trend.IchimokuIndicator(df['High'], df['Low'])
                df['ISA_9']  = _ichi.ichimoku_a()
                df['ISB_26'] = _ichi.ichimoku_b()
            except:
                pass

            # Volumen promedio
            df['VOL_MA20'] = df['Volume'].rolling(20).mean()
            df['VOL_RATIO'] = df['Volume'] / df['VOL_MA20']

            # ── Fibonacci ─────────────────────────────────────
            swing_window = min(252, len(df))
            high_swing = df['High'].tail(swing_window).max()
            low_swing = df['Low'].tail(swing_window).min()
            diff = high_swing - low_swing
            fib_levels = {
                '0% (Máx)': high_swing,
                '23.6%': high_swing - 0.236 * diff,
                '38.2%': high_swing - 0.382 * diff,
                '50%': high_swing - 0.500 * diff,
                '61.8%': high_swing - 0.618 * diff,
                '78.6%': high_swing - 0.786 * diff,
                '100% (Mín)': low_swing,
                'Ext 127.2%': low_swing - 0.272 * diff,
                'Ext 161.8%': low_swing - 0.618 * diff,
            }

            return df, stock.info, fib_levels
        except Exception as e:
            st.error(f"Error cargando {ticker}: {e}")
            return None, None, {}

    @st.cache_data(ttl=60)
    def get_quick_price(ticker):
        try:
            t = yf.Ticker(ticker)
            hist = t.history(period="2d")
            if hist.empty:
                return None, None
            last = hist['Close'].iloc[-1]
            prev = hist['Close'].iloc[-2] if len(hist) > 1 else last
            return last, (last - prev) / prev * 100
        except:
            return None, None


class NewsData:
    @st.cache_data(ttl=300)
    def get_rss_news(ticker, company_name=""):
        """Agrega noticias de múltiples fuentes RSS."""
        feeds = []
        base_ticker = ticker.replace(".BA", "").replace("-USD", "").replace("=F", "")
        search_term = company_name if company_name else base_ticker

        # Fuentes RSS gratuitas
        rss_sources = [
            (f"https://finance.yahoo.com/rss/headline?s={ticker}", "Yahoo Finance"),
            (f"https://feeds.finance.yahoo.com/rss/2.0/headline?s={ticker}&region=US&lang=en-US", "Yahoo Finance"),
            ("https://www.investing.com/rss/news.rss", "Investing.com"),
            (f"https://seekingalpha.com/api/sa/combined/{base_ticker}.xml", "Seeking Alpha"),
            ("https://feeds.bloomberg.com/markets/news.rss", "Bloomberg"),
            ("https://www.marketwatch.com/rss/topstories", "MarketWatch"),
            ("https://feeds.a.dj.com/rss/RSSMarketsMain.xml", "WSJ Markets"),
        ]

        all_entries = []
        for url, source in rss_sources:
            try:
                feed = feedparser.parse(url)
                for entry in feed.entries[:3]:
                    title = entry.get('title', '')
                    if base_ticker.lower() in title.lower() or (search_term and search_term.lower() in title.lower()):
                        all_entries.append({
                            'title': title,
                            'link': entry.get('link', '#'),
                            'source': source,
                            'published': entry.get('published', ''),
                            'summary': entry.get('summary', '')[:200] if entry.get('summary') else ''
                        })
                    elif not (base_ticker.lower() in title.lower()):
                        all_entries.append({
                            'title': title,
                            'link': entry.get('link', '#'),
                            'source': source,
                            'published': entry.get('published', ''),
                            'summary': entry.get('summary', '')[:200] if entry.get('summary') else ''
                        })
            except:
                pass

        # Limitar y priorizar las que mencionan el ticker
        ticker_news = [e for e in all_entries if base_ticker.lower() in e['title'].lower()]
        general_news = [e for e in all_entries if base_ticker.lower() not in e['title'].lower()]
        return (ticker_news + general_news)[:15]

    @st.cache_data(ttl=600)
    def get_fear_greed():
        """Obtiene Fear & Greed Index de CNN/Alternative.me."""
        try:
            r = requests.get("https://api.alternative.me/fng/?limit=7", timeout=5)
            data = r.json()
            return data['data']
        except:
            return None

    @st.cache_data(ttl=300)
    def get_crypto_global():
        """Stats globales del mercado crypto."""
        try:
            r = requests.get("https://api.coingecko.com/api/v3/global", timeout=5)
            return r.json().get('data', {})
        except:
            return {}


class TechnicalScore:
    """Calcula un score técnico 0-100 multi-factor."""

    def calculate(df, fib_levels, info=None):
        signals = []
        details = []

        last = df.iloc[-1]
        prev = df.iloc[-2]
        close = last['Close']

        # ── RSI (0-15 pts) ────────────────────────────────────
        rsi = last.get('RSI', np.nan)
        if pd.notna(rsi):
            if 40 <= rsi <= 60:
                signals.append(5); details.append(f"RSI neutral {rsi:.1f}")
            elif rsi < 30:
                signals.append(15); details.append(f"✅ RSI sobreventa {rsi:.1f}")
            elif rsi < 40:
                signals.append(10); details.append(f"RSI bajo {rsi:.1f}")
            elif rsi > 70:
                signals.append(-10); details.append(f"⚠️ RSI sobrecompra {rsi:.1f}")
            elif rsi > 60:
                signals.append(2); details.append(f"RSI alto {rsi:.1f}")

        # ── Supertrend (0-15 pts) ────────────────────────────
        st_dir_col = next((c for c in df.columns if c.startswith('SUPERTd_7')), None)
        if st_dir_col:
            st_dir = last.get(st_dir_col, 0)
            if st_dir == 1:
                signals.append(15); details.append("✅ SuperTrend ALCISTA")
            else:
                signals.append(-15); details.append("⚠️ SuperTrend BAJISTA")

        # ── EMAs (0-20 pts) ──────────────────────────────────
        ema_score = 0
        if pd.notna(last.get('EMA_50')) and close > last['EMA_50']:
            ema_score += 5
        if pd.notna(last.get('EMA_100')) and close > last['EMA_100']:
            ema_score += 5
        if pd.notna(last.get('EMA_200')) and close > last['EMA_200']:
            ema_score += 10

        # Golden cross / Death cross
        if (pd.notna(last.get('EMA_50')) and pd.notna(last.get('EMA_200'))):
            if last['EMA_50'] > last['EMA_200'] and prev.get('EMA_50', 0) <= prev.get('EMA_200', 0):
                ema_score += 5; details.append("🌟 GOLDEN CROSS EMA50/200")
            elif last['EMA_50'] < last['EMA_200'] and prev.get('EMA_50', 0) >= prev.get('EMA_200', 0):
                ema_score -= 5; details.append("💀 DEATH CROSS EMA50/200")

        signals.append(ema_score)
        if ema_score > 0:
            details.append(f"✅ EMAs favorables (+{ema_score})")

        # ── MACD (0-10 pts) ──────────────────────────────────
        macd_h_col = next((c for c in df.columns if c.startswith('MACDh_')), None)
        macd_col = next((c for c in df.columns if c.startswith('MACD_')), None)
        if macd_h_col and macd_col:
            hist = last.get(macd_h_col, 0)
            prev_hist = prev.get(macd_h_col, 0)
            if hist > 0 and prev_hist <= 0:
                signals.append(10); details.append("✅ MACD cruce alcista")
            elif hist < 0 and prev_hist >= 0:
                signals.append(-10); details.append("⚠️ MACD cruce bajista")
            elif hist > 0:
                signals.append(5); details.append("MACD positivo")
            else:
                signals.append(-5)

        # ── Bollinger Bands (0-10 pts) ───────────────────────
        bb_lower = next((c for c in df.columns if c.startswith('BBL_')), None)
        bb_upper = next((c for c in df.columns if c.startswith('BBU_')), None)
        if bb_lower and bb_upper:
            bbl = last.get(bb_lower, np.nan)
            bbu = last.get(bb_upper, np.nan)
            if pd.notna(bbl) and close <= bbl:
                signals.append(10); details.append("✅ Precio en BB inferior (rebote potencial)")
            elif pd.notna(bbu) and close >= bbu:
                signals.append(-5); details.append("⚠️ Precio en BB superior")

        # ── Volumen (0-10 pts) ───────────────────────────────
        vol_ratio = last.get('VOL_RATIO', 1)
        if pd.notna(vol_ratio):
            if vol_ratio > 2:
                signals.append(10); details.append(f"✅ Volumen {vol_ratio:.1f}x promedio (fuerte convicción)")
            elif vol_ratio > 1.5:
                signals.append(5); details.append(f"Volumen elevado {vol_ratio:.1f}x")
            elif vol_ratio < 0.5:
                signals.append(-2); details.append(f"Volumen muy bajo {vol_ratio:.1f}x")

        # ── Fibonacci (0-10 pts) ─────────────────────────────
        fib_618 = fib_levels.get('61.8%', None)
        fib_382 = fib_levels.get('38.2%', None)
        if fib_618 and close > fib_618:
            signals.append(10); details.append("✅ Precio sobre Fib 61.8%")
        elif fib_382 and close < fib_382:
            signals.append(-5); details.append("⚠️ Precio bajo Fib 38.2%")

        # ── MFI Money Flow (0-10 pts) ────────────────────────
        mfi = last.get('MFI', np.nan)
        if pd.notna(mfi):
            if mfi < 20:
                signals.append(10); details.append(f"✅ MFI sobreventa {mfi:.1f}")
            elif mfi > 80:
                signals.append(-8); details.append(f"⚠️ MFI sobrecompra {mfi:.1f}")
            elif mfi > 50:
                signals.append(3)

        # ── Score final normalizado 0-100 ────────────────────
        raw = sum(signals)
        # Rango teórico aprox -75 a +100
        normalized = max(0, min(100, int((raw + 75) / 175 * 100)))
        return normalized, details


def get_col(df, prefixes):
    for p in prefixes:
        for c in df.columns:
            if c.startswith(p):
                return c
    return None


# ══════════════════════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown('<div class="terminal-logo" style="font-size:22px; margin-bottom:16px;">⬡ NAPOLITANO<br>TERMINAL PRO</div>', unsafe_allow_html=True)

    st.markdown("**INDICADORES**")
    show_st = st.toggle("SuperTrend", value=True)
    show_ema9 = st.toggle("EMA 9/21", value=False)
    show_ema50 = st.toggle("EMA 50", value=True)
    show_ema100 = st.toggle("EMA 100", value=True)
    show_ema200 = st.toggle("EMA 200", value=True)
    show_vwap = st.toggle("VWAP", value=False)
    show_bbands = st.toggle("Bollinger Bands", value=True)
    show_ichimoku = st.toggle("Ichimoku Cloud", value=False)
    show_rsi = st.toggle("RSI", value=True)
    show_macd = st.toggle("MACD", value=False)
    show_volume = st.toggle("Volumen", value=True)
    show_fib = st.toggle("Fibonacci", value=True)

    st.divider()
    st.markdown("**PERÍODO**")
    period = st.select_slider("", options=["1mo", "3mo", "6mo", "1y", "2y", "5y"], value="2y")

    st.divider()
    st.markdown("**WATCHLIST**")
    for fav in st.session_state.favoritos[:8]:
        price, pct = StockData.get_quick_price(fav)
        if price:
            color = "#00FF88" if pct and pct >= 0 else "#FF3366"
            pct_str = f"{pct:+.2f}%" if pct else "—"
            st.markdown(
                f'<div class="watchlist-item">'
                f'<span style="color:#E8EDF5; font-size:12px;">{fav}</span>'
                f'<div style="text-align:right">'
                f'<div style="font-size:13px; color:#E8EDF5;">{price:,.2f}</div>'
                f'<div style="font-size:10px; color:{color};">{pct_str}</div>'
                f'</div></div>',
                unsafe_allow_html=True
            )

    st.divider()
    st.markdown("*Vaca Muerta & Tech · 2026*", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════
# HEADER PRINCIPAL
# ══════════════════════════════════════════════════════════════
now = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
st.markdown(
    f'<div class="status-bar">'
    f'<span><span class="live-dot"></span>LIVE</span>'
    f'<span>⏱ {now}</span>'
    f'<span style="color:#FF6B1A;">NAPOLITANO TERMINAL PRO v3.0</span>'
    f'<span>Análisis Técnico Multi-Fuente</span>'
    f'</div>',
    unsafe_allow_html=True
)

# ── Barra de búsqueda ────────────────────────────────────────
c_busq, c_fav, c_add, c_del, c_upd = st.columns([2, 2, 0.5, 0.5, 0.5])

with c_busq:
    ticker_manual = st.text_input("", placeholder="🔍  Buscar ticker  (AAPL · GGAL.BA · BTC-USD)", label_visibility="collapsed").upper().strip()

with c_fav:
    ticker_fav = st.selectbox("", ["— WATCHLIST —"] + sorted(st.session_state.favoritos), label_visibility="collapsed")

ticker_final = ticker_manual if ticker_manual else (ticker_fav if ticker_fav != "— WATCHLIST —" else "GGAL.BA")

with c_add:
    if st.button("⭐", help="Agregar a watchlist"):
        if ticker_final and ticker_final not in st.session_state.favoritos:
            st.session_state.favoritos.append(ticker_final)
            st.rerun()

with c_del:
    if st.button("🗑", help="Quitar de watchlist"):
        if ticker_final in st.session_state.favoritos:
            st.session_state.favoritos.remove(ticker_final)
            st.rerun()

with c_upd:
    if st.button("⟳", help="Actualizar datos"):
        st.cache_data.clear()
        st.rerun()

# ══════════════════════════════════════════════════════════════
# CARGA DE DATOS
# ══════════════════════════════════════════════════════════════
if ticker_final:
    with st.spinner(f"📡 Cargando {ticker_final}..."):
        df, info, fib_levels = StockData.get_data(ticker_final, period)

    if df is not None and not df.empty:
        ultimo = df['Close'].iloc[-1]
        anterior = df['Close'].iloc[-2]
        variacion = ultimo - anterior
        variacion_pct = variacion / anterior * 100
        color_v = "#00FF88" if variacion >= 0 else "#FF3366"
        flecha = "▲" if variacion >= 0 else "▼"

        # ── Score técnico ─────────────────────────────────────
        score, score_details = TechnicalScore.calculate(df, fib_levels, info)

        # ══════════════════════════════════════════════════════
        # FILA DE PRECIO + SCORE
        # ══════════════════════════════════════════════════════
        col_info, col_metrics, col_score = st.columns([2, 3, 1.5])

        with col_info:
            name = info.get('longName', ticker_final) if info else ticker_final
            sector = info.get('sector', '') if info else ''
            currency = info.get('currency', '') if info else ''
            st.markdown(f'<p class="company-name">{name}</p>', unsafe_allow_html=True)
            st.markdown(f'<p style="font-size:10px;color:#7A8BA0;">{sector} · {currency}</p>', unsafe_allow_html=True)
            st.markdown(f'<p class="price-giant">{ultimo:,.2f}</p>', unsafe_allow_html=True)
            st.markdown(
                f'<p class="{"delta-up" if variacion>=0 else "delta-down"}">'
                f'{flecha} {abs(variacion):,.2f} &nbsp; ({variacion_pct:.2f}%)'
                f'</p>',
                unsafe_allow_html=True
            )

        with col_metrics:
            m1, m2, m3, m4 = st.columns(4)
            # 52-week hi/lo
            high52 = info.get('fiftyTwoWeekHigh', df['High'].max()) if info else df['High'].max()
            low52 = info.get('fiftyTwoWeekLow', df['Low'].min()) if info else df['Low'].min()
            mktcap = info.get('marketCap', None) if info else None
            pe = info.get('trailingPE', None) if info else None

            with m1:
                st.markdown(
                    f'<div class="metric-card"><div class="metric-label">MÁX DÍA</div>'
                    f'<div class="metric-value">{df["High"].iloc[-1]:,.2f}</div></div>', unsafe_allow_html=True)
                st.markdown(
                    f'<div class="metric-card"><div class="metric-label">MÁX 52S</div>'
                    f'<div class="metric-value">{high52:,.2f}</div></div>', unsafe_allow_html=True)

            with m2:
                st.markdown(
                    f'<div class="metric-card"><div class="metric-label">MÍN DÍA</div>'
                    f'<div class="metric-value">{df["Low"].iloc[-1]:,.2f}</div></div>', unsafe_allow_html=True)
                st.markdown(
                    f'<div class="metric-card"><div class="metric-label">MÍN 52S</div>'
                    f'<div class="metric-value">{low52:,.2f}</div></div>', unsafe_allow_html=True)

            with m3:
                vol_fmt = f"{df['Volume'].iloc[-1]/1e6:.2f}M" if df['Volume'].iloc[-1] > 1e6 else f"{df['Volume'].iloc[-1]:,.0f}"
                cap_fmt = f"${mktcap/1e9:.1f}B" if mktcap else "—"
                st.markdown(
                    f'<div class="metric-card"><div class="metric-label">VOLUMEN</div>'
                    f'<div class="metric-value">{vol_fmt}</div></div>', unsafe_allow_html=True)
                st.markdown(
                    f'<div class="metric-card"><div class="metric-label">MARKET CAP</div>'
                    f'<div class="metric-value">{cap_fmt}</div></div>', unsafe_allow_html=True)

            with m4:
                atr_val = df['ATR'].iloc[-1] if 'ATR' in df.columns else 0
                pe_fmt = f"{pe:.1f}x" if pe and pe > 0 else "—"
                vol_ratio = df['VOL_RATIO'].iloc[-1] if 'VOL_RATIO' in df.columns else 1
                st.markdown(
                    f'<div class="metric-card"><div class="metric-label">ATR (14)</div>'
                    f'<div class="metric-value">{atr_val:.2f}</div></div>', unsafe_allow_html=True)
                st.markdown(
                    f'<div class="metric-card"><div class="metric-label">P/E RATIO</div>'
                    f'<div class="metric-value">{pe_fmt}</div></div>', unsafe_allow_html=True)

        with col_score:
            if score >= 65:
                score_class = "score-bullish"
                score_label = "ALCISTA"
                score_emoji = "🟢"
            elif score <= 35:
                score_class = "score-bearish"
                score_label = "BAJISTA"
                score_emoji = "🔴"
            else:
                score_class = "score-neutral"
                score_label = "NEUTRAL"
                score_emoji = "🟡"

            st.markdown(
                f'<div class="score-container">'
                f'<div style="font-size:9px;color:#7A8BA0;letter-spacing:2px;margin-bottom:4px;">SCORE TÉCNICO</div>'
                f'<div class="score-number {score_class}">{score}</div>'
                f'<div style="font-size:11px;color:#7A8BA0;">/ 100</div>'
                f'<div style="font-size:14px;margin-top:8px;">{score_emoji} <b>{score_label}</b></div>'
                f'</div>',
                unsafe_allow_html=True
            )

        st.divider()

        # ══════════════════════════════════════════════════════
        # TABS PRINCIPALES
        # ══════════════════════════════════════════════════════
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "📈  GRÁFICO", "🔔  SEÑALES & ANÁLISIS", "📰  NOTICIAS", "📊  FUNDAMENTALES", "⚙️  ALERTAS"
        ])

        # ────────────────────────────────────────────────────
        # TAB 1: GRÁFICO
        # ────────────────────────────────────────────────────
        with tab1:

            # ── Controles de rango ───────────────────────────
            rc1, rc2, rc3 = st.columns([2, 3, 1])
            with rc1:
                rango_botones = st.radio(
                    "Rango rápido",
                    ["1S", "1M", "3M", "6M", "1A", "2A", "TODO"],
                    index=4,
                    horizontal=True,
                    label_visibility="collapsed"
                )
            with rc3:
                altura_grafico = st.select_slider(
                    "Alto",
                    options=[600, 700, 800, 900, 1000, 1100, 1200],
                    value=900,
                    label_visibility="collapsed"
                )

            # Calcular fechas según rango seleccionado
            fecha_fin = df.index[-1]
            rangos = {
                "1S": fecha_fin - pd.Timedelta(weeks=1),
                "1M": fecha_fin - pd.Timedelta(days=30),
                "3M": fecha_fin - pd.Timedelta(days=90),
                "6M": fecha_fin - pd.Timedelta(days=180),
                "1A": fecha_fin - pd.Timedelta(days=365),
                "2A": fecha_fin - pd.Timedelta(days=730),
                "TODO": df.index[0],
            }
            fecha_inicio_zoom = rangos[rango_botones]

            bb_upper = get_col(df, ["BBU_20"])
            bb_middle = get_col(df, ["BBM_20"])
            bb_lower = get_col(df, ["BBL_20"])
            st_val_col = get_col(df, ["SUPERT_7_3"])
            st_dir_col = get_col(df, ["SUPERTd_7_3"])
            macd_col = get_col(df, ["MACD_12"])
            macdh_col = get_col(df, ["MACDh_12"])
            macds_col = get_col(df, ["MACDs_12"])

            # Definir subplots
            row_specs = [1]
            heights = [0.55]
            if show_volume:
                row_specs.append(len(row_specs) + 1)
                heights.append(0.12)
            if show_rsi:
                row_specs.append(len(row_specs) + 1)
                heights.append(0.17)
            if show_macd:
                row_specs.append(len(row_specs) + 1)
                heights.append(0.16)

            total_rows = len(heights)
            fig = make_subplots(
                rows=total_rows, cols=1,
                shared_xaxes=True,
                vertical_spacing=0.02,
                row_heights=heights
            )

            # VELAS
            fig.add_trace(go.Candlestick(
                x=df.index, open=df['Open'], high=df['High'],
                low=df['Low'], close=df['Close'],
                name="Precio",
                increasing_line_color='#00FF88',
                decreasing_line_color='#FF3366',
                increasing_fillcolor='rgba(0,255,136,0.27)',
                decreasing_fillcolor='rgba(255,51,102,0.27)',
            ), row=1, col=1)

            # EMAs
            ema_colors = {'EMA_9': '#FF69B4', 'EMA_21': '#FF8C00', 'EMA_50': '#00CED1', 'EMA_100': '#FFD700', 'EMA_200': '#FF6B1A'}
            if show_ema9:
                for e in ['EMA_9', 'EMA_21']:
                    if e in df.columns:
                        fig.add_trace(go.Scatter(x=df.index, y=df[e], name=e, line=dict(color=ema_colors[e], width=1, dash='dot')), row=1, col=1)
            if show_ema50 and 'EMA_50' in df.columns:
                fig.add_trace(go.Scatter(x=df.index, y=df['EMA_50'], name="EMA 50", line=dict(color=ema_colors['EMA_50'], width=1.5)), row=1, col=1)
            if show_ema100 and 'EMA_100' in df.columns:
                fig.add_trace(go.Scatter(x=df.index, y=df['EMA_100'], name="EMA 100", line=dict(color=ema_colors['EMA_100'], width=1.5)), row=1, col=1)
            if show_ema200 and 'EMA_200' in df.columns:
                fig.add_trace(go.Scatter(x=df.index, y=df['EMA_200'], name="EMA 200", line=dict(color=ema_colors['EMA_200'], width=2)), row=1, col=1)

            # VWAP
            if show_vwap and 'VWAP' in df.columns:
                fig.add_trace(go.Scatter(x=df.index, y=df['VWAP'], name="VWAP", line=dict(color='#9B59B6', width=1.5, dash='dash')), row=1, col=1)

            # Bollinger
            if show_bbands and bb_upper and bb_middle and bb_lower:
                fig.add_trace(go.Scatter(x=df.index, y=df[bb_upper], name="BB Upper", line=dict(color='#555', width=1, dash='dot'), showlegend=False), row=1, col=1)
                fig.add_trace(go.Scatter(x=df.index, y=df[bb_lower], name="BB Lower", line=dict(color='#555', width=1, dash='dot'),
                    fill='tonexty', fillcolor='rgba(100,100,100,0.08)', showlegend=False), row=1, col=1)
                fig.add_trace(go.Scatter(x=df.index, y=df[bb_middle], name="BB Media", line=dict(color='#888', width=1)), row=1, col=1)

            # SuperTrend
            if show_st and st_val_col and st_dir_col:
                df['st_alc'] = np.where(df[st_dir_col] == 1, df[st_val_col], np.nan)
                df['st_baj'] = np.where(df[st_dir_col] == -1, df[st_val_col], np.nan)
                fig.add_trace(go.Scatter(x=df.index, y=df['st_alc'], name="ST ▲", line=dict(color='#00FF88', width=2.5)), row=1, col=1)
                fig.add_trace(go.Scatter(x=df.index, y=df['st_baj'], name="ST ▼", line=dict(color='#FF3366', width=2.5)), row=1, col=1)

            # Ichimoku
            if show_ichimoku:
                ichi_cols = {
                    'ISA_9': ('#00FF8820', 'ITS_9', '#FF336620'),
                }
                isa = get_col(df, ['ISA_9'])
                isb = get_col(df, ['ISB_26'])
                if isa and isb:
                    fig.add_trace(go.Scatter(x=df.index, y=df[isa], name="Kumo A", line=dict(color='#00FF88', width=0.5), showlegend=False), row=1, col=1)
                    fig.add_trace(go.Scatter(x=df.index, y=df[isb], name="Kumo B", line=dict(color='#FF3366', width=0.5),
                        fill='tonexty', fillcolor='rgba(0,255,136,0.07)', showlegend=False), row=1, col=1)

            # Fibonacci
            if show_fib:
                fib_palette = ['#FFD700', '#FFA500', '#FF8C00', '#00CED1', '#20B2AA', '#4169E1', '#9370DB', '#C0C0C0', '#808080']
                for i, (level, price) in enumerate(fib_levels.items()):
                    fig.add_hline(
                        y=price, line_dash="dot",
                        line_color=fib_palette[i % len(fib_palette)],
                        line_width=1,
                        annotation_text=f"Fib {level}: {price:.2f}",
                        annotation_font_size=10,
                        annotation_font_color=fib_palette[i % len(fib_palette)],
                        row=1, col=1
                    )

            curr_row = 2

            # VOLUMEN
            if show_volume:
                vol_colors = ['rgba(0,255,136,0.53)' if df['Close'].iloc[i] >= df['Open'].iloc[i] else 'rgba(255,51,102,0.53)'
                              for i in range(len(df))]
                fig.add_trace(go.Bar(x=df.index, y=df['Volume'], name="Volumen",
                    marker_color=vol_colors, showlegend=False), row=curr_row, col=1)
                if 'VOL_MA20' in df.columns:
                    fig.add_trace(go.Scatter(x=df.index, y=df['VOL_MA20'], name="Vol MA20",
                        line=dict(color='#FF6B1A', width=1.5)), row=curr_row, col=1)
                curr_row += 1

            # RSI
            if show_rsi:
                fig.add_trace(go.Scatter(x=df.index, y=df['RSI'], name="RSI(14)",
                    line=dict(color='#00D4FF', width=1.5)), row=curr_row, col=1)
                fig.add_hrect(y0=70, y1=100, fillcolor="rgba(255,51,102,0.06)", line_width=0, row=curr_row, col=1)
                fig.add_hrect(y0=0, y1=30, fillcolor="rgba(0,255,136,0.06)", line_width=0, row=curr_row, col=1)
                fig.add_hline(y=70, line_dash="dot", line_color="#FF3366", line_width=1,
                    annotation_text="70", annotation_font_size=9, row=curr_row, col=1)
                fig.add_hline(y=30, line_dash="dot", line_color="#00FF88", line_width=1,
                    annotation_text="30", annotation_font_size=9, row=curr_row, col=1)
                fig.add_hline(y=50, line_dash="dot", line_color="#555", line_width=1, row=curr_row, col=1)
                curr_row += 1

            # MACD
            if show_macd and macd_col and macdh_col:
                colors_hist = ['#00FF88' if v >= 0 else '#FF3366' for v in df[macdh_col].fillna(0)]
                fig.add_trace(go.Bar(x=df.index, y=df[macdh_col], name="MACD Hist",
                    marker_color=colors_hist, showlegend=False), row=curr_row, col=1)
                fig.add_trace(go.Scatter(x=df.index, y=df[macd_col], name="MACD",
                    line=dict(color='#FF6B1A', width=1.5)), row=curr_row, col=1)
                if macds_col:
                    fig.add_trace(go.Scatter(x=df.index, y=df[macds_col], name="Signal",
                        line=dict(color='#00D4FF', width=1.5)), row=curr_row, col=1)

            fig.update_layout(
                height=altura_grafico,
                template="plotly_dark",
                paper_bgcolor='#060A0F',
                plot_bgcolor='#0D1520',
                xaxis_rangeslider_visible=False,
                showlegend=True,
                legend=dict(
                    bgcolor='#0D1520',
                    bordercolor='#1E2D3D',
                    borderwidth=1,
                    font=dict(family='JetBrains Mono', size=10, color='#7A8BA0')
                ),
                font=dict(family='JetBrains Mono', color='#7A8BA0'),
                margin=dict(l=60, r=60, t=30, b=30),
                xaxis=dict(range=[fecha_inicio_zoom, fecha_fin]),
            )

            for i in range(1, total_rows + 1):
                fig.update_xaxes(
                    gridcolor='#1E2D3D', showgrid=True,
                    zeroline=False, row=i, col=1,
                    range=[fecha_inicio_zoom, fecha_fin] if i == 1 else None
                )
                fig.update_yaxes(
                    gridcolor='#1E2D3D', showgrid=True,
                    zeroline=False, row=i, col=1,
                    side='right'
                )

            # Barra deslizante de navegación temporal
            st.markdown("<div style='margin-top:-10px;'></div>", unsafe_allow_html=True)
            fechas_disponibles = df.index.tolist()
            if len(fechas_disponibles) > 10:
                idx_min = 0
                idx_max = len(fechas_disponibles) - 1
                idx_inicio_default = max(0, fechas_disponibles.index(
                    min(fechas_disponibles, key=lambda x: abs((x.tz_localize(None) if x.tzinfo else x) - (fecha_inicio_zoom.tz_localize(None) if hasattr(fecha_inicio_zoom, 'tzinfo') and fecha_inicio_zoom.tzinfo else fecha_inicio_zoom)))
                ))
                rango_idx = st.slider(
                    "📅 Navegar en el tiempo",
                    min_value=0,
                    max_value=idx_max,
                    value=(idx_inicio_default, idx_max),
                    label_visibility="visible"
                )
                fecha_slider_ini = fechas_disponibles[rango_idx[0]]
                fecha_slider_fin = fechas_disponibles[rango_idx[1]]
                fig.update_xaxes(range=[fecha_slider_ini, fecha_slider_fin], row=1, col=1)

            st.plotly_chart(fig, use_container_width=True)

        # ────────────────────────────────────────────────────
        # TAB 2: SEÑALES & ANÁLISIS
        # ────────────────────────────────────────────────────
        with tab2:
            s_col1, s_col2 = st.columns([1, 1])

            with s_col1:
                st.markdown('<p class="section-hdr">SEÑAL CONSOLIDADA</p>', unsafe_allow_html=True)

                last = df.iloc[-1]
                rsi_val = last.get('RSI', np.nan)
                st_dir_c = get_col(df, ["SUPERTd_7_3"])
                st_dir = last.get(st_dir_c, 0) if st_dir_c else 0
                macd_h = last.get(get_col(df, ["MACDh_12"]) or 'X', 0)
                mfi_val = last.get('MFI', 50)
                close = last['Close']

                # Señal principal
                if score >= 70:
                    signal_html = f'<div class="signal-buy">🟢 COMPRA FUERTE — Score {score}/100<br><small>Múltiples indicadores alineados alcistas</small></div>'
                elif score >= 55:
                    signal_html = f'<div class="signal-buy">🟡 COMPRA MODERADA — Score {score}/100<br><small>Sesgo alcista con cautela</small></div>'
                elif score <= 30:
                    signal_html = f'<div class="signal-sell">🔴 VENTA — Score {score}/100<br><small>Señales bajistas predominantes</small></div>'
                elif score <= 45:
                    signal_html = f'<div class="signal-sell">🟠 CAUTELA — Score {score}/100<br><small>Presión vendedora presente</small></div>'
                else:
                    signal_html = f'<div class="signal-hold">⏸ ESPERAR — Score {score}/100<br><small>Sin señal clara definida</small></div>'

                st.markdown(signal_html, unsafe_allow_html=True)

                st.markdown('<p class="section-hdr" style="margin-top:20px;">DETALLE DE SEÑALES</p>', unsafe_allow_html=True)
                for det in score_details:
                    st.markdown(f"- {det}")

                st.markdown('<p class="section-hdr" style="margin-top:20px;">NIVELES FIBONACCI</p>', unsafe_allow_html=True)
                fib_html = '<div style="background:#111B27;border:1px solid #1E2D3D;border-radius:6px;overflow:hidden;">'
                colors_fib = ['#FFD700', '#FFA500', '#FF8C00', '#00CED1', '#20B2AA', '#4169E1', '#9370DB', '#C0C0C0', '#808080']
                for i, (level, price) in enumerate(fib_levels.items()):
                    is_near = abs(close - price) / close < 0.015
                    bg = '#1E3A2A' if is_near else 'transparent'
                    fib_html += (
                        f'<div class="fib-row" style="background:{bg};">'
                        f'<span style="color:{colors_fib[i%len(colors_fib)]};">{level}</span>'
                        f'<span style="color:#E8EDF5;font-weight:{"700" if is_near else "400"};">'
                        f'{price:,.2f} {"◄ PRECIO ACTUAL" if is_near else ""}</span>'
                        f'</div>'
                    )
                fib_html += '</div>'
                st.markdown(fib_html, unsafe_allow_html=True)

            with s_col2:
                st.markdown('<p class="section-hdr">INDICADORES CLAVE</p>', unsafe_allow_html=True)

                indicators = [
                    ("RSI (14)", f"{rsi_val:.1f}" if pd.notna(rsi_val) else "—",
                     "#FF3366" if pd.notna(rsi_val) and rsi_val > 70 else "#00FF88" if pd.notna(rsi_val) and rsi_val < 30 else "#E8EDF5"),
                    ("MFI (14)", f"{mfi_val:.1f}" if pd.notna(mfi_val) else "—",
                     "#FF3366" if pd.notna(mfi_val) and mfi_val > 80 else "#00FF88" if pd.notna(mfi_val) and mfi_val < 20 else "#E8EDF5"),
                    ("ATR (14)", f"{last.get('ATR', 0):.2f}", "#E8EDF5"),
                    ("Williams %R", f"{last.get('WR', 0):.1f}%", "#E8EDF5"),
                    ("CCI (20)", f"{last.get('CCI', 0):.1f}",
                     "#FF3366" if last.get('CCI', 0) > 100 else "#00FF88" if last.get('CCI', 0) < -100 else "#E8EDF5"),
                    ("Vol / MA20", f"{last.get('VOL_RATIO', 1):.2f}x",
                     "#00FF88" if last.get('VOL_RATIO', 1) > 1.5 else "#E8EDF5"),
                    ("SuperTrend", "🟢 ALCISTA" if st_dir == 1 else "🔴 BAJISTA",
                     "#00FF88" if st_dir == 1 else "#FF3366"),
                    ("EMA 50 vs 200",
                     "✅ Golden Cross" if (pd.notna(last.get('EMA_50')) and pd.notna(last.get('EMA_200')) and last['EMA_50'] > last['EMA_200']) else "⚠️ Death Cross",
                     "#00FF88" if (pd.notna(last.get('EMA_50')) and pd.notna(last.get('EMA_200')) and last['EMA_50'] > last['EMA_200']) else "#FF3366"),
                ]

                for name_ind, val, color in indicators:
                    st.markdown(
                        f'<div class="metric-card" style="display:flex;justify-content:space-between;align-items:center;">'
                        f'<span style="font-size:11px;color:#7A8BA0;">{name_ind}</span>'
                        f'<span style="font-size:14px;font-weight:600;color:{color};">{val}</span>'
                        f'</div>',
                        unsafe_allow_html=True
                    )

                # Soporte / Resistencia dinámico
                st.markdown('<p class="section-hdr" style="margin-top:20px;">SOPORTE & RESISTENCIA</p>', unsafe_allow_html=True)
                highs = df['High'].tail(60)
                lows = df['Low'].tail(60)
                r1 = highs.nlargest(3).mean()
                r2 = highs.max()
                s1 = lows.nsmallest(3).mean()
                s2 = lows.min()

                for label, val, color in [
                    ("Resistencia 2", r2, "#FF3366"),
                    ("Resistencia 1", r1, "#FF8C00"),
                    ("PRECIO ACTUAL", close, "#00D4FF"),
                    ("Soporte 1", s1, "#00FF88"),
                    ("Soporte 2", s2, "#00A855"),
                ]:
                    bold = "bold" if "ACTUAL" in label else "normal"
                    st.markdown(
                        f'<div class="fib-row" style="background:#111B27;border-radius:4px;margin:2px 0;">'
                        f'<span style="color:#7A8BA0;font-size:11px;">{label}</span>'
                        f'<span style="color:{color};font-weight:{bold};font-size:13px;">{val:,.2f}</span>'
                        f'</div>',
                        unsafe_allow_html=True
                    )

                # Tabla reciente
                st.markdown('<p class="section-hdr" style="margin-top:20px;">ÚLTIMAS VELAS</p>', unsafe_allow_html=True)
                cols_show = ['Open', 'High', 'Low', 'Close', 'Volume', 'RSI', 'ATR', 'MFI']
                cols_show = [c for c in cols_show if c in df.columns]
                st.dataframe(df[cols_show].tail(8).round(2), use_container_width=True)

        # ────────────────────────────────────────────────────
        # TAB 3: NOTICIAS
        # ────────────────────────────────────────────────────
        with tab3:
            n_col1, n_col2 = st.columns([2, 1])

            with n_col1:
                st.markdown('<p class="section-hdr">NOTICIAS EN TIEMPO REAL</p>', unsafe_allow_html=True)
                company_name = info.get('longName', '') if info else ''

                with st.spinner("Buscando noticias..."):
                    noticias = NewsData.get_rss_news(ticker_final, company_name)

                if noticias:
                    for n in noticias[:12]:
                        st.markdown(
                            f'<div class="news-item">'
                            f'<div class="news-source">📡 {n["source"]}</div>'
                            f'<div class="news-title"><a href="{n["link"]}" target="_blank" style="color:#E8EDF5;text-decoration:none;">{n["title"]}</a></div>'
                            f'<div class="news-time">🕐 {n.get("published","")[:20]}</div>'
                            f'{"<div style=font-size:11px;color:#7A8BA0;margin-top:4px;>" + n["summary"] + "</div>" if n.get("summary") else ""}'
                            f'</div>',
                            unsafe_allow_html=True
                        )
                else:
                    st.info("No se encontraron noticias recientes. Intente con otro ticker.")

            with n_col2:
                st.markdown('<p class="section-hdr">FEAR & GREED</p>', unsafe_allow_html=True)
                fg_data = NewsData.get_fear_greed()
                if fg_data:
                    latest = fg_data[0]
                    fg_val = int(latest['value'])
                    fg_class = latest['value_classification']
                    fg_color = "#00FF88" if fg_val > 60 else "#FF3366" if fg_val < 40 else "#FFD700"
                    st.markdown(
                        f'<div class="score-container">'
                        f'<div style="font-size:9px;color:#7A8BA0;letter-spacing:2px;">CRYPTO FEAR & GREED</div>'
                        f'<div class="score-number" style="color:{fg_color};text-shadow:0 0 20px {fg_color}44;">{fg_val}</div>'
                        f'<div style="font-size:13px;color:{fg_color};font-weight:600;">{fg_class.upper()}</div>'
                        f'</div>',
                        unsafe_allow_html=True
                    )
                    st.markdown("**Historial 7 días:**")
                    for d in fg_data[:7]:
                        v = int(d['value'])
                        c = "#00FF88" if v > 60 else "#FF3366" if v < 40 else "#FFD700"
                        ts = datetime.fromtimestamp(int(d['timestamp'])).strftime("%d/%m")
                        st.markdown(f'<div style="display:flex;justify-content:space-between;font-size:11px;padding:3px 0;border-bottom:1px solid #1E2D3D;">'
                                    f'<span style="color:#7A8BA0;">{ts}</span>'
                                    f'<span style="color:{c};font-weight:600;">{v} — {d["value_classification"]}</span>'
                                    f'</div>', unsafe_allow_html=True)

                st.markdown('<p class="section-hdr" style="margin-top:20px;">ANALISTAS</p>', unsafe_allow_html=True)
                try:
                    stock_obj = yf.Ticker(ticker_final)
                    rec = stock_obj.recommendations_summary
                    if rec is not None and not rec.empty:
                        st.dataframe(rec.head(5), use_container_width=True)
                    else:
                        st.info("Sin datos de analistas.")
                except:
                    st.info("Sin datos de analistas.")

                st.markdown('<p class="section-hdr" style="margin-top:20px;">PRÓXIMOS EARNINGS</p>', unsafe_allow_html=True)
                try:
                    stock_obj = yf.Ticker(ticker_final)
                    cal = stock_obj.calendar
                    if cal is not None and not cal.empty:
                        st.dataframe(cal, use_container_width=True)
                    else:
                        st.info("Sin fecha de earnings.")
                except:
                    st.info("Sin fecha de earnings.")

        # ────────────────────────────────────────────────────
        # TAB 4: FUNDAMENTALES
        # ────────────────────────────────────────────────────
        with tab4:
            if info:
                f_col1, f_col2, f_col3 = st.columns(3)

                fundamentals = {
                    "VALORACIÓN": {
                        "P/E (trailing)": info.get('trailingPE'),
                        "P/E (forward)": info.get('forwardPE'),
                        "P/B Ratio": info.get('priceToBook'),
                        "P/S Ratio": info.get('priceToSalesTrailing12Months'),
                        "EV/EBITDA": info.get('enterpriseToEbitda'),
                        "EV/Revenue": info.get('enterpriseToRevenue'),
                    },
                    "RENTABILIDAD": {
                        "Margen bruto": info.get('grossMargins'),
                        "Margen operativo": info.get('operatingMargins'),
                        "Margen neto": info.get('profitMargins'),
                        "ROE": info.get('returnOnEquity'),
                        "ROA": info.get('returnOnAssets'),
                        "EBITDA": info.get('ebitda'),
                    },
                    "CRECIMIENTO": {
                        "Revenue (anual)": info.get('revenueGrowth'),
                        "Ganancias (QoQ)": info.get('earningsQuarterlyGrowth'),
                        "Revenue total": info.get('totalRevenue'),
                        "Free Cash Flow": info.get('freeCashflow'),
                        "Beta": info.get('beta'),
                        "Dividendo yield": info.get('dividendYield'),
                    }
                }

                for col, (category, metrics) in zip([f_col1, f_col2, f_col3], fundamentals.items()):
                    with col:
                        st.markdown(f'<p class="section-hdr">{category}</p>', unsafe_allow_html=True)
                        for metric, value in metrics.items():
                            if value is not None:
                                if isinstance(value, float) and value < 1 and value != 0:
                                    display = f"{value*100:.2f}%"
                                elif isinstance(value, float) and abs(value) > 1e9:
                                    display = f"${value/1e9:.2f}B"
                                elif isinstance(value, float):
                                    display = f"{value:.2f}x"
                                else:
                                    display = str(value)
                            else:
                                display = "—"

                            st.markdown(
                                f'<div class="metric-card" style="display:flex;justify-content:space-between;">'
                                f'<span style="font-size:10px;color:#7A8BA0;">{metric}</span>'
                                f'<span style="font-size:13px;color:#E8EDF5;font-weight:600;">{display}</span>'
                                f'</div>',
                                unsafe_allow_html=True
                            )

                # Earnings
                st.markdown('<p class="section-hdr" style="margin-top:20px;">HISTORIAL DE GANANCIAS</p>', unsafe_allow_html=True)
                try:
                    stock_obj = yf.Ticker(ticker_final)
                    earnings = stock_obj.earnings_dates
                    if earnings is not None and not earnings.empty:
                        st.dataframe(earnings.head(10), use_container_width=True)
                except:
                    st.info("Sin datos de ganancias.")
            else:
                st.info("Datos fundamentales no disponibles para este instrumento.")

        # ────────────────────────────────────────────────────
        # TAB 5: ALERTAS
        # ────────────────────────────────────────────────────
        with tab5:
            a_col1, a_col2 = st.columns([1, 1])

            with a_col1:
                st.markdown('<p class="section-hdr">CONFIGURAR ALERTA</p>', unsafe_allow_html=True)
                alert_price = st.number_input(
                    "Precio objetivo", value=float(f"{ultimo:.2f}"),
                    step=float(f"{ultimo*0.01:.4f}"), format="%.4f"
                )
                alert_type = st.radio("Tipo", ["🔔 Precio supera", "🔔 Precio cae bajo"])
                alert_note = st.text_input("Nota (opcional)", placeholder="Ej: TP1, Stop Loss, Soporte clave")

                if st.button("➕ Agregar Alerta", use_container_width=True):
                    if ticker_final not in st.session_state.alertas:
                        st.session_state.alertas[ticker_final] = []
                    st.session_state.alertas[ticker_final].append({
                        'price': alert_price,
                        'type': alert_type,
                        'note': alert_note,
                        'created': datetime.now().strftime("%d/%m %H:%M"),
                        'triggered': False
                    })
                    st.success(f"✅ Alerta creada para {ticker_final} @ {alert_price:.4f}")

            with a_col2:
                st.markdown('<p class="section-hdr">ALERTAS ACTIVAS</p>', unsafe_allow_html=True)

                all_alerts = []
                for t, alerts in st.session_state.alertas.items():
                    for a in alerts:
                        all_alerts.append({'ticker': t, **a})

                if all_alerts:
                    for i, alert in enumerate(all_alerts):
                        price_now, _ = StockData.get_quick_price(alert['ticker'])
                        triggered = False
                        if price_now:
                            if "supera" in alert['type'] and price_now >= alert['price']:
                                triggered = True
                            elif "cae" in alert['type'] and price_now <= alert['price']:
                                triggered = True

                        card_class = "alert-triggered" if triggered else "metric-card"
                        st.markdown(
                            f'<div class="{card_class}">'
                            f'<div style="display:flex;justify-content:space-between;">'
                            f'<span style="color:#FF6B1A;font-weight:700;">{alert["ticker"]}</span>'
                            f'<span style="font-size:10px;color:#7A8BA0;">{alert["created"]}</span>'
                            f'</div>'
                            f'<div style="font-size:13px;color:#E8EDF5;">{alert["type"]} <b>{alert["price"]:.4f}</b></div>'
                            f'{"<div style=color:#FF6B1A;font-weight:700;>🔔 ¡ALERTA DISPARADA!</div>" if triggered else ""}'
                            f'{"<div style=font-size:11px;color:#7A8BA0;>" + alert["note"] + "</div>" if alert.get("note") else ""}'
                            f'</div>',
                            unsafe_allow_html=True
                        )
                else:
                    st.info("Sin alertas configuradas.")

                st.markdown('<p class="section-hdr" style="margin-top:20px;">NOTAS DEL ANALISTA</p>', unsafe_allow_html=True)
                nota_actual = st.session_state.notas.get(ticker_final, "")
                nueva_nota = st.text_area(
                    f"Notas para {ticker_final}",
                    value=nota_actual,
                    height=150,
                    placeholder="Tesis de inversión, niveles clave, catalizadores..."
                )
                if st.button("💾 Guardar nota"):
                    st.session_state.notas[ticker_final] = nueva_nota
                    st.success("✅ Nota guardada")

        # ── Export ────────────────────────────────────────────
        st.divider()
        exp_col1, exp_col2, exp_col3 = st.columns(3)
        with exp_col1:
            st.download_button(
                "💾 Exportar CSV",
                df.to_csv().encode('utf-8'),
                f"{ticker_final}_{period}.csv",
                "text/csv",
                use_container_width=True
            )
        with exp_col2:
            # Reporte texto
            reporte = f"""NAPOLITANO TERMINAL PRO — REPORTE {ticker_final}
Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M')}
Precio: {ultimo:,.4f} ({variacion_pct:+.2f}%)
Score Técnico: {score}/100 — {score_label}

SEÑALES:
{chr(10).join(score_details)}

FIBONACCI:
{chr(10).join([f'{k}: {v:,.2f}' for k,v in fib_levels.items()])}
"""
            st.download_button(
                "📄 Exportar Reporte",
                reporte.encode('utf-8'),
                f"{ticker_final}_reporte.txt",
                "text/plain",
                use_container_width=True
            )
        with exp_col3:
            st.markdown(f'<div style="text-align:center;font-size:10px;color:#7A8BA0;padding:8px;">Auto-refresh en 45s<br><span class="live-dot"></span>DATOS EN VIVO</div>', unsafe_allow_html=True)

    else:
        st.markdown(
            f'<div style="background:#1A0A00;border:2px solid #FF6B1A;border-radius:8px;padding:30px;text-align:center;">'
            f'<div style="font-size:40px;">⚠️</div>'
            f'<div style="color:#FF6B1A;font-size:18px;font-weight:700;">No se encontraron datos para {ticker_final}</div>'
            f'<div style="color:#7A8BA0;font-size:12px;margin-top:8px;">Verifique el símbolo · Ejemplos: GGAL.BA · AAPL · BTC-USD · GC=F</div>'
            f'</div>',
            unsafe_allow_html=True
        )

st.markdown(
    '<div style="text-align:center;padding:20px;font-size:10px;color:#1E2D3D;border-top:1px solid #1E2D3D;margin-top:40px;">'
    '⬡ NAPOLITANO TERMINAL PRO · Desarrollado para Jorge Napolitano · Análisis Vaca Muerta & Tech · 2026'
    '</div>',
    unsafe_allow_html=True
)
