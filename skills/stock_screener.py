"""
stock_screener.py — Multi-criteria stock scanner.
Screens a universe of popular tickers against user-defined filters.
Uses yfinance for data — no API key required.
"""
try:
    import yfinance as yf
    HAS_YF = True
except ImportError:
    HAS_YF = False

from datetime import datetime
import json


# Default screening universe: S&P 500 top constituents + popular tickers
SCREEN_UNIVERSE = [
    "AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "META", "TSLA", "BRK-B", "JPM", "V",
    "JNJ", "WMT", "PG", "MA", "UNH", "HD", "DIS", "BAC", "ADBE", "CRM",
    "NFLX", "COST", "PEP", "TMO", "AVGO", "MRK", "ACN", "CSCO", "ABT", "LLY",
    "AMD", "INTC", "QCOM", "TXN", "PYPL", "ORCL", "AMGN", "PM", "IBM", "GE",
    "CAT", "HON", "UPS", "BA", "MMM", "GS", "AXP", "MS", "C", "WFC",
    "XOM", "CVX", "COP", "SLB", "EOG", "MPC", "VLO", "PSX", "OXY", "HAL",
    "PLTR", "SOFI", "RIVN", "LCID", "NIO", "PLUG", "COIN", "MARA", "SQ", "SHOP",
    "ROKU", "SNAP", "PINS", "UBER", "LYFT", "ABNB", "DASH", "RBLX", "U", "DKNG"
]


def calculate_rsi(prices: list, period: int = 14) -> float:
    """Calculate RSI from a list of closing prices."""
    if len(prices) < period + 1:
        return 50.0
    deltas = [prices[i] - prices[i - 1] for i in range(1, len(prices))]
    gains = [d if d > 0 else 0 for d in deltas[-period:]]
    losses = [-d if d < 0 else 0 for d in deltas[-period:]]
    avg_gain = sum(gains) / period
    avg_loss = sum(losses) / period
    if avg_loss == 0:
        return 100.0
    rs = avg_gain / avg_loss
    return round(100 - (100 / (1 + rs)), 2)


def execute(args: dict) -> dict:
    if not HAS_YF:
        return {"error": "yfinance not installed. Run: pip install yfinance"}

    # Parse filters
    min_market_cap = args.get("min_market_cap")
    max_market_cap = args.get("max_market_cap")
    sector = (args.get("sector", "") or "").strip()
    max_pe = args.get("max_pe")
    min_pe = args.get("min_pe")
    max_rsi = args.get("max_rsi")
    min_rsi = args.get("min_rsi")
    min_volume = args.get("min_volume")
    min_change_pct = args.get("min_change_pct")
    max_change_pct = args.get("max_change_pct")
    limit = min(int(args.get("limit", 15)), 30)

    # Natural language criteria parsing
    criteria = (args.get("criteria", "") or "").lower()
    if criteria:
        if "oversold" in criteria:
            max_rsi = max_rsi or 30
        if "overbought" in criteria:
            min_rsi = min_rsi or 70
        if "large" in criteria or "large-cap" in criteria:
            min_market_cap = min_market_cap or 10_000_000_000
        if "mid" in criteria or "mid-cap" in criteria:
            min_market_cap = min_market_cap or 2_000_000_000
            max_market_cap = max_market_cap or 10_000_000_000
        if "small" in criteria or "small-cap" in criteria:
            max_market_cap = max_market_cap or 2_000_000_000
        if "tech" in criteria:
            sector = sector or "Technology"
        if "health" in criteria:
            sector = sector or "Healthcare"
        if "energy" in criteria:
            sector = sector or "Energy"
        if "financ" in criteria:
            sector = sector or "Financial Services"
        if "high volume" in criteria:
            min_volume = min_volume or 10_000_000

    custom_tickers = args.get("tickers")
    universe = custom_tickers if custom_tickers and isinstance(custom_tickers, list) else SCREEN_UNIVERSE

    matches = []
    errors = 0

    for ticker in universe:
        try:
            stock = yf.Ticker(ticker)
            info = stock.info or {}
            if not info.get("regularMarketPrice") and not info.get("currentPrice"):
                continue

            price = info.get("regularMarketPrice") or info.get("currentPrice", 0)
            mcap = info.get("marketCap", 0)
            pe = info.get("trailingPE")
            vol = info.get("regularMarketVolume") or info.get("volume", 0)
            stk_sector = info.get("sector", "")
            prev_close = info.get("regularMarketPreviousClose") or info.get("previousClose", 0)
            change_pct = round(((price - prev_close) / prev_close) * 100, 2) if prev_close else 0

            # Apply filters
            if min_market_cap and mcap < min_market_cap:
                continue
            if max_market_cap and mcap > max_market_cap:
                continue
            if sector and sector.lower() not in stk_sector.lower():
                continue
            if max_pe and pe and pe > max_pe:
                continue
            if min_pe and pe and pe < min_pe:
                continue
            if min_volume and vol < min_volume:
                continue
            if min_change_pct is not None and change_pct < min_change_pct:
                continue
            if max_change_pct is not None and change_pct > max_change_pct:
                continue

            # RSI filter (requires price history)
            rsi = None
            if max_rsi or min_rsi:
                hist = stock.history(period="1mo")
                if not hist.empty and len(hist) > 14:
                    rsi = calculate_rsi(hist["Close"].tolist())
                    if max_rsi and rsi > max_rsi:
                        continue
                    if min_rsi and rsi < min_rsi:
                        continue

            matches.append({
                "ticker": ticker,
                "name": info.get("shortName", ticker),
                "price": price,
                "change_pct": change_pct,
                "market_cap": mcap,
                "pe_ratio": pe,
                "volume": vol,
                "rsi": rsi,
                "sector": stk_sector
            })

        except Exception:
            errors += 1
            continue

    # Sort by absolute change % (most volatile first)
    matches.sort(key=lambda x: abs(x.get("change_pct", 0)), reverse=True)

    return {
        "matches": matches[:limit],
        "total_found": len(matches),
        "universe_size": len(universe),
        "errors": errors,
        "filters_applied": {k: v for k, v in {
            "min_market_cap": min_market_cap, "max_market_cap": max_market_cap,
            "sector": sector, "max_pe": max_pe, "min_pe": min_pe,
            "max_rsi": max_rsi, "min_rsi": min_rsi, "min_volume": min_volume
        }.items() if v},
        "timestamp": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC"),
        "disclaimer": "For informational purposes only. Not financial advice."
    }
