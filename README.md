# 📊 AI Stock Dashboard

An interactive AI-powered stock analysis dashboard built with Streamlit.

## 🚀 Features

- 📈 Real-time stock data (yfinance)
- ⚡ Technical analysis (SMA crossover signals)
- 🧠 AI-powered news sentiment analysis (OpenAI)
- ⏱️ Smart refresh (live prices update automatically)
- 🔔 On-demand AI analysis (cost-efficient)
- 📊 Stock ranking system
- ➕ Add any stock ticker dynamically
- 🧠 Persistent AI results with freshness timer

---

## 🧠 How It Works

### Technical Analysis
- 5-day vs 20-day moving averages
- Detects BUY / SELL crossover signals
- Generates a weighted technical score

### AI Analysis
- Pulls latest news headlines
- Uses AI to determine:
  - Sentiment (Bullish / Bearish / Neutral)
  - Confidence level
  - Summary explanation

---

## ⚙️ Requirements
streamlit
yfinance
feedparser
pandas
openai
streamlit-autorefresh
