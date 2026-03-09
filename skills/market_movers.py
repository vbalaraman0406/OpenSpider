"""
market_movers.py — Today's top gainers, losers, and volume leaders.
Scans a broad universe via yfinance for largest daily moves.
"""
try:
    import yfinance as yf
    HAS_YF = True
except ImportError:
    HAS_YF = False

from datetime import datetime


# Broad scanning universe (~100 popular and volatile tickers)
SCAN_UNIVERSE = [
    # Mega-cap tech
    "AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "META", "TSLA", "AVGO", "ORCL", "CRM",
    "AMD", "INTC", "QCOM", "ADBE", "NFLX", "PYPL",
    # Financials
    "JPM", "BAC", "GS", "MS", "WFC", "C", "AXP", "V", "MA", "SOFI",
    # Healthcare
    "JNJ", "UNH", "PFE", "LLY", "ABBV", "MRK", "TMO", "ABT", "AMGN", "HIMS",
    # Consumer + Retail
    "WMT", "COST", "HD", "NKE", "SBUX", "MCD", "PG", "KO", "PEP", "DIS",
    # Energy
    "XOM", "CVX", "COP", "SLB", "EOG", "MPC", "OXY",
    # Industrials + Transport
    "CAT", "BA", "HON", "UPS", "GE", "LMT", "RTX", "DE",
    # High-beta / Volatile
    "PLTR", "COIN", "MARA", "RIVN", "LCID", "NIO", "PLUG", "RBLX", "DKNG",
    "SHOP", "SNAP", "PINS", "UBER", "LYFT", "ABNB", "DASH", "ROKU", "SQ",
    "SMCI", "ARM", "IONQ", "RGTI", "BBAI", "ONDS", "KULR",
    # ETFs
    "SPY", "QQQ", "IWM", "DIA", "VTI", "ARKK",
    # Airlines
    "AAL", "DAL", "UAL", "LUV", "JBLU",
]


def execute(args: dict) -> dict:
    if not HAS_YF:
        return {"error": "yfinance not installed. Run: pip install yfinance"}

    category = (args.get("category", "all") or "all").lower()
    limit = min(int(args.get("limit", 10)), 20)

    results = []
    for ticker in SCAN_UNIVERSE:
        try:
            stock = yf.Ticker(ticker)
            info = stock.info or {}
            price = info.get("regularMarketPrice") or info.get("currentPrice", 0)
            prev_close = info.get("regularMarketPreviousClose") or info.get("previousClose", 0)

            if not price or not prev_close:
                continue

            change = round(price - prev_close, 2)
            change_pct = round((change / prev_close) * 100, 2)
            volume = info.get("regularMarketVolume") or info.get("volume", 0)

            results.append({
                "ticker": ticker,
                "name": info.get("shortName", ticker),
                "price": price,
                "change": change,
                "change_pct": change_pct,
                "volume": volume,
                "market_cap": info.get("marketCap"),
            })
        except Exception:
            continue

    output = {
        "timestamp": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC"),
        "scanned": len(results),
        "disclaimer": "For informational purposes only. Not financial advice."
    }

    if category in ("gainers", "all"):
        gainers = sorted(results, key=lambda x: x["change_pct"], reverse=True)
        output["top_gainers"] = gainers[:limit]

    if category in ("losers", "all"):
        losers = sorted(results, key=lambda x: x["change_pct"])
        output["top_losers"] = losers[:limit]

    if category in ("volume", "active", "all"):
        by_volume = sorted(results, key=lambda x: x.get("volume", 0), reverse=True)
        output["most_active"] = by_volume[:limit]

    # Major indices summary
    try:
        indices = {"^GSPC": "S&P 500", "^IXIC": "NASDAQ", "^DJI": "Dow Jones"}
        index_data = []
        for sym, name in indices.items():
            idx = yf.Ticker(sym)
            iinfo = idx.info or {}
            ip = iinfo.get("regularMarketPrice") or iinfo.get("currentPrice", 0)
            ipc = iinfo.get("regularMarketPreviousClose") or iinfo.get("previousClose", 0)
            if ip and ipc:
                index_data.append({
                    "index": name,
                    "price": round(ip, 2),
                    "change_pct": round(((ip - ipc) / ipc) * 100, 2)
                })
        output["indices"] = index_data
    except Exception:
        pass

    return output
