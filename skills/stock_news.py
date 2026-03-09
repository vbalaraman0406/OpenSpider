"""
stock_news.py — Stock news with keyword-based sentiment.
Uses yfinance news feed. Sentiment is derived from headline keywords.
"""
try:
    import yfinance as yf
    HAS_YF = True
except ImportError:
    HAS_YF = False

from datetime import datetime


# Simple keyword-based sentiment scoring
POSITIVE_KEYWORDS = [
    "beat", "surge", "rally", "gain", "rise", "soar", "upgrade", "bullish", "record",
    "growth", "profit", "strong", "boom", "breakout", "optimism", "upbeat", "buy",
    "outperform", "exceed", "positive", "robust", "momentum", "accelerat",
]
NEGATIVE_KEYWORDS = [
    "crash", "plunge", "drop", "fall", "decline", "loss", "miss", "downgrade", "bearish",
    "slump", "weak", "warning", "concern", "fear", "risk", "cut", "layoff", "sell",
    "underperform", "negative", "recession", "inflation", "default", "fraud",
]


def score_headline(title: str) -> dict:
    """Score a headline as positive, negative, or neutral based on keywords."""
    lower = title.lower()
    pos = sum(1 for w in POSITIVE_KEYWORDS if w in lower)
    neg = sum(1 for w in NEGATIVE_KEYWORDS if w in lower)

    if pos > neg:
        return {"sentiment": "positive", "score": min(pos * 20, 100)}
    elif neg > pos:
        return {"sentiment": "negative", "score": -min(neg * 20, 100)}
    return {"sentiment": "neutral", "score": 0}


def execute(args: dict) -> dict:
    if not HAS_YF:
        return {"error": "yfinance not installed. Run: pip install yfinance"}

    ticker = (args.get("ticker", "") or "").strip().upper().replace("$", "")
    limit = min(int(args.get("limit", 10)), 25)

    if not ticker:
        return {"error": "Missing 'ticker' parameter. Example: {\"ticker\": \"TSLA\"}"}

    try:
        stock = yf.Ticker(ticker)
        info = stock.info or {}
        news_items = stock.news or []

        articles = []
        pos_count = 0
        neg_count = 0
        neutral_count = 0

        for item in news_items[:limit]:
            title = item.get("title", "")
            sentiment = score_headline(title)

            if sentiment["sentiment"] == "positive":
                pos_count += 1
            elif sentiment["sentiment"] == "negative":
                neg_count += 1
            else:
                neutral_count += 1

            article = {
                "title": title,
                "publisher": item.get("publisher", "Unknown"),
                "link": item.get("link", ""),
                "published": "",
                "sentiment": sentiment["sentiment"],
                "sentiment_score": sentiment["score"],
            }

            # Parse timestamp
            ts = item.get("providerPublishTime")
            if ts:
                try:
                    article["published"] = datetime.utcfromtimestamp(ts).strftime("%Y-%m-%d %H:%M UTC")
                except Exception:
                    pass

            articles.append(article)

        # Overall sentiment
        total = pos_count + neg_count + neutral_count
        if total == 0:
            overall = "no_data"
        elif pos_count > neg_count * 1.5:
            overall = "bullish"
        elif neg_count > pos_count * 1.5:
            overall = "bearish"
        else:
            overall = "mixed"

        return {
            "ticker": ticker,
            "name": info.get("shortName", ticker),
            "articles": articles,
            "sentiment_summary": {
                "overall": overall,
                "positive_count": pos_count,
                "negative_count": neg_count,
                "neutral_count": neutral_count,
                "total_articles": total,
            },
            "timestamp": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC"),
            "disclaimer": "Sentiment is keyword-based and may not reflect true market sentiment. Not financial advice."
        }

    except Exception as e:
        return {"error": f"Failed to fetch news for {ticker}: {str(e)}"}
