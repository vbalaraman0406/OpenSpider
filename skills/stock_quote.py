"""
stock_quote.py — Real-time stock price snapshot using yfinance.
Returns current price, change, volume, 52-week range, market cap, and key stats.
"""
try:
    import yfinance as yf
    HAS_YF = True
except ImportError:
    HAS_YF = False

from datetime import datetime


def execute(args: dict) -> dict:
    if not HAS_YF:
        return {"error": "yfinance not installed. Run: pip install yfinance"}

    ticker = (args.get("ticker", "") or "").strip().upper().replace("$", "")
    if not ticker:
        return {"error": "Missing 'ticker' parameter. Example: {\"ticker\": \"AAPL\"}"}

    try:
        stock = yf.Ticker(ticker)
        info = stock.info or {}

        if not info.get("regularMarketPrice") and not info.get("currentPrice"):
            return {"error": f"No data found for ticker '{ticker}'. Verify the symbol."}

        price = info.get("regularMarketPrice") or info.get("currentPrice", 0)
        prev_close = info.get("regularMarketPreviousClose") or info.get("previousClose", 0)
        change = round(price - prev_close, 2) if price and prev_close else None
        change_pct = round((change / prev_close) * 100, 2) if change and prev_close else None

        result = {
            "ticker": ticker,
            "name": info.get("shortName") or info.get("longName", ticker),
            "price": price,
            "change": change,
            "change_percent": change_pct,
            "currency": info.get("currency", "USD"),
            "volume": info.get("regularMarketVolume") or info.get("volume"),
            "avg_volume": info.get("averageVolume"),
            "market_cap": info.get("marketCap"),
            "pe_ratio": info.get("trailingPE"),
            "forward_pe": info.get("forwardPE"),
            "dividend_yield": round(info.get("dividendYield", 0) * 100, 2) if info.get("dividendYield") else None,
            "52_week_high": info.get("fiftyTwoWeekHigh"),
            "52_week_low": info.get("fiftyTwoWeekLow"),
            "50_day_avg": info.get("fiftyDayAverage"),
            "200_day_avg": info.get("twoHundredDayAverage"),
            "beta": info.get("beta"),
            "sector": info.get("sector"),
            "industry": info.get("industry"),
            "exchange": info.get("exchange"),
            "timestamp": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC"),
            "disclaimer": "For informational purposes only. Not financial advice."
        }

        # After-hours / pre-market data if available
        pre_price = info.get("preMarketPrice")
        post_price = info.get("postMarketPrice")
        if pre_price:
            result["pre_market_price"] = pre_price
            result["pre_market_change_pct"] = round(((pre_price - price) / price) * 100, 2) if price else None
        if post_price:
            result["post_market_price"] = post_price
            result["post_market_change_pct"] = round(((post_price - price) / price) * 100, 2) if price else None

        return result

    except Exception as e:
        return {"error": f"Failed to fetch quote for {ticker}: {str(e)}"}
