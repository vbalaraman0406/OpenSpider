"""
stock_compare.py — Head-to-head stock comparison.
Compares 2-10 tickers across price, fundamentals, technicals, and valuation.
"""
try:
    import yfinance as yf
    HAS_YF = True
except ImportError:
    HAS_YF = False

from datetime import datetime


def calculate_rsi(prices: list, period: int = 14) -> float:
    if len(prices) < period + 1:
        return 50.0
    deltas = [prices[i] - prices[i - 1] for i in range(1, len(prices))]
    gains = [d if d > 0 else 0 for d in deltas[-period:]]
    losses = [-d if d < 0 else 0 for d in deltas[-period:]]
    avg_gain = sum(gains) / period
    avg_loss = sum(losses) / period
    if avg_loss == 0:
        return 100.0
    return round(100 - (100 / (1 + (avg_gain / avg_loss))), 2)


def execute(args: dict) -> dict:
    if not HAS_YF:
        return {"error": "yfinance not installed. Run: pip install yfinance"}

    tickers = args.get("tickers", [])
    if not tickers or not isinstance(tickers, list):
        return {"error": "Provide 'tickers' as a list. Example: {\"tickers\": [\"AAPL\", \"MSFT\"]}"}

    tickers = [t.strip().upper().replace("$", "") for t in tickers[:10]]

    comparisons = []
    for ticker in tickers:
        try:
            stock = yf.Ticker(ticker)
            info = stock.info or {}
            price = info.get("regularMarketPrice") or info.get("currentPrice", 0)
            prev_close = info.get("regularMarketPreviousClose") or info.get("previousClose", 0)
            change_pct = round(((price - prev_close) / prev_close) * 100, 2) if prev_close else 0

            # Get RSI
            rsi = None
            try:
                hist = stock.history(period="1mo")
                if not hist.empty and len(hist) > 14:
                    rsi = calculate_rsi(hist["Close"].tolist())
            except Exception:
                pass

            # YTD performance
            ytd_pct = None
            try:
                ytd_hist = stock.history(period="ytd")
                if not ytd_hist.empty and len(ytd_hist) > 1:
                    first = ytd_hist["Close"].iloc[0]
                    last = ytd_hist["Close"].iloc[-1]
                    ytd_pct = round(((last - first) / first) * 100, 2)
            except Exception:
                pass

            comparisons.append({
                "ticker": ticker,
                "name": info.get("shortName", ticker),
                "price": price,
                "change_pct": change_pct,
                "market_cap": info.get("marketCap"),
                "pe_ratio": info.get("trailingPE"),
                "forward_pe": info.get("forwardPE"),
                "peg_ratio": info.get("pegRatio"),
                "price_to_book": info.get("priceToBook"),
                "revenue_growth": round(info.get("revenueGrowth", 0) * 100, 2) if info.get("revenueGrowth") else None,
                "profit_margin": round(info.get("profitMargins", 0) * 100, 2) if info.get("profitMargins") else None,
                "debt_to_equity": info.get("debtToEquity"),
                "dividend_yield": round(info.get("dividendYield", 0) * 100, 2) if info.get("dividendYield") else None,
                "beta": info.get("beta"),
                "rsi": rsi,
                "52_week_high": info.get("fiftyTwoWeekHigh"),
                "52_week_low": info.get("fiftyTwoWeekLow"),
                "ytd_return_pct": ytd_pct,
                "sector": info.get("sector"),
                "analyst_rating": info.get("recommendationKey"),
            })
        except Exception as e:
            comparisons.append({"ticker": ticker, "error": str(e)})

    # Determine winners per metric
    winners = {}
    numeric_metrics = ["market_cap", "revenue_growth", "profit_margin", "ytd_return_pct"]
    lower_is_better = ["pe_ratio", "debt_to_equity"]

    valid = [c for c in comparisons if "error" not in c]
    for metric in numeric_metrics:
        vals = [(c["ticker"], c.get(metric)) for c in valid if c.get(metric) is not None]
        if vals:
            winners[metric] = max(vals, key=lambda x: x[1])[0]
    for metric in lower_is_better:
        vals = [(c["ticker"], c.get(metric)) for c in valid if c.get(metric) is not None]
        if vals:
            winners[metric] = min(vals, key=lambda x: x[1])[0]

    return {
        "comparison": comparisons,
        "winners": winners,
        "tickers_compared": len(comparisons),
        "timestamp": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC"),
        "disclaimer": "For informational purposes only. Not financial advice."
    }
