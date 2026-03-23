import streamlit as st
import yfinance as yf
import feedparser
import pandas as pd
import time
from openai import OpenAI
from streamlit_autorefresh import st_autorefresh

# ------------------------
# 🔑 CONFIG
# ------------------------
OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]
client = OpenAI(api_key=OPENAI_API_KEY)

# ------------------------
# 🧠 SESSION STATE
# ------------------------
if "ai_results" not in st.session_state:
    st.session_state.ai_results = None

if "ai_timestamp" not in st.session_state:
    st.session_state.ai_timestamp = None

if "tickers" not in st.session_state:
    st.session_state.tickers = ["AAPL", "TSLA", "MSFT", "NVDA", "SPY"]

# ------------------------
# UI
# ------------------------
st.set_page_config(layout="wide")
st.title("📊 AI Stock Dashboard (Pro Version)")

# 🔄 Auto refresh (2 min)
st_autorefresh(interval=120000, key="refresh")

st.caption(f"Last market refresh: {time.strftime('%H:%M:%S')}")

# ------------------------
# ➕ ADD STOCK INPUT
# ------------------------
new_ticker = st.text_input("➕ Add Stock Ticker (e.g., AMD, META)")

if new_ticker:
    new_ticker = new_ticker.upper()
    if new_ticker not in st.session_state.tickers:
        st.session_state.tickers.append(new_ticker)
        st.success(f"{new_ticker} added!")
        st.rerun()

# ------------------------
# 📊 ANALYSIS FUNCTIONS
# ------------------------
def analyze_stock(ticker):
    df = yf.Ticker(ticker).history(period="1mo")

    df['SMA5'] = df['Close'].rolling(5).mean()
    df['SMA20'] = df['Close'].rolling(20).mean()

    price = df['Close'].iloc[-1]
    sma5 = df['SMA5'].iloc[-1]
    sma20 = df['SMA20'].iloc[-1]

    prev_sma5 = df['SMA5'].iloc[-2]
    prev_sma20 = df['SMA20'].iloc[-2]

    trend = "Bullish" if sma5 > sma20 else "Bearish"

    if prev_sma5 < prev_sma20 and sma5 > sma20:
        signal = "BUY 🚀"
        score = 2
    elif prev_sma5 > prev_sma20 and sma5 < sma20:
        signal = "SELL ⚠️"
        score = -2
    else:
        signal = "HOLD"
        score = 0

    return price, trend, signal, score

def get_news(ticker):
    url = f"https://news.google.com/rss/search?q={ticker}+stock"
    feed = feedparser.parse(url)
    return [(entry.title, entry.link) for entry in feed.entries[:5]]

@st.cache_data(ttl=900)
def get_ai_analysis(ticker, headlines):
    prompt = f"""
    Headlines for {ticker}:
    {headlines}

    Return:
    - Sentiment (Bullish/Bearish/Neutral)
    - Confidence (0-100%)
    - Short explanation
    """

    response = client.responses.create(
        model="gpt-5-nano",
        input=prompt
    )

    return response.output_text

def calculate_score(trend, signal, sentiment):
    trend_score = 1 if trend == "Bullish" else -1

    if "BUY" in signal:
        signal_score = 2
    elif "SELL" in signal:
        signal_score = -2
    else:
        signal_score = 0

    if "Bullish" in sentiment:
        sentiment_score = 1
    elif "Bearish" in sentiment:
        sentiment_score = -1
    else:
        sentiment_score = 0

    return round(
        (trend_score * 0.4) +
        (signal_score * 0.3) +
        (sentiment_score * 0.3),
        2
    )

# ------------------------
# ⚡ TECHNICAL RANKING
# ------------------------
results = []
stock_data = {}

for ticker in st.session_state.tickers:
    price, trend, signal, score = analyze_stock(ticker)

    results.append((ticker, score, signal, price, trend))

    stock_data[ticker] = {
        "price": price,
        "trend": trend,
        "signal": signal
    }

results.sort(key=lambda x: x[1], reverse=True)

st.subheader("⚡ Technical Rankings (Instant)")
st.dataframe(pd.DataFrame(
    results,
    columns=["Ticker","Score","Signal","Price","Trend"]
))

# ------------------------
# 🔘 INDIVIDUAL ANALYSIS
# ------------------------
st.subheader("🔍 Analyze Individual Stock")

selected_stock = st.selectbox(
    "Choose a stock",
    st.session_state.tickers
)

if st.button("Analyze Selected Stock"):

    headlines = get_news(selected_stock)
    ai_text = get_ai_analysis(selected_stock, headlines)

    st.session_state.ai_results = {
        selected_stock: (headlines, ai_text)
    }
    st.session_state.ai_timestamp = time.time()

# ------------------------
# 🔘 ANALYZE ALL
# ------------------------
if st.button("🧠 Analyze ALL Stocks"):

    enhanced_results = []
    news_cache = {}

    for ticker in st.session_state.tickers:

        headlines = get_news(ticker)
        ai_text = get_ai_analysis(ticker, headlines)

        data = stock_data[ticker]

        new_score = calculate_score(
            data["trend"],
            data["signal"],
            ai_text
        )

        enhanced_results.append(
            (ticker, new_score, data["signal"], data["price"], data["trend"])
        )

        news_cache[ticker] = (headlines, ai_text)

    enhanced_results.sort(key=lambda x: x[1], reverse=True)

    st.session_state.ai_results = (enhanced_results, news_cache)
    st.session_state.ai_timestamp = time.time()

# ------------------------
# 🧠 PERSISTENT DISPLAY
# ------------------------
if st.session_state.ai_results:

    st.subheader("🧠 AI Results")

    elapsed = time.time() - st.session_state.ai_timestamp
    remaining = max(0, 900 - elapsed)

    minutes = int(remaining // 60)
    seconds = int(remaining % 60)

    if remaining > 0:
        st.info(f"⏱️ Fresh for: {minutes}m {seconds}s")
    else:
        st.warning("⚠️ AI data is stale — click analyze again")

    # HANDLE BOTH MODES
    if isinstance(st.session_state.ai_results, tuple):

        enhanced_results, news_cache = st.session_state.ai_results

        st.dataframe(pd.DataFrame(
            enhanced_results,
            columns=["Ticker","Score","Signal","Price","Trend"]
        ))

        selected = st.selectbox(
            "View details",
            [r[0] for r in enhanced_results]
        )

        headlines, ai_text = news_cache[selected]

    else:
        selected = list(st.session_state.ai_results.keys())[0]
        headlines, ai_text = st.session_state.ai_results[selected]

    st.subheader(f"{selected} News")
    for title, link in headlines:
        st.markdown(f"[{title}]({link})")

    st.subheader("🤖 AI Analysis")
    st.write(ai_text)