import json
import math
from datetime import datetime, timedelta

try:
    import yfinance as yf
    HAS_YFINANCE = True
except ImportError:
    HAS_YFINANCE = False

try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False


def _safe_get(d, key, default=None):
    """Safely retrieve a value from a dict or object attribute."""
    if isinstance(d, dict):
        return d.get(key, default)
    return getattr(d, key, default)


def get_stock_price(ticker: str, period: str = "6mo") -> dict:
    """Returns OHLCV data for the given ticker and period."""
    if not HAS_YFINANCE:
        return {"error": "yfinance library not installed. Install with: pip install yfinance"}
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period=period)
        if hist.empty:
            return {"error": f"No price data found for ticker '{ticker}'."}
        records = []
        for idx, row in hist.iterrows():
            records.append({
                "date": idx.strftime("%Y-%m-%d"),
                "open": round(float(row["Open"]), 2),
                "high": round(float(row["High"]), 2),
                "low": round(float(row["Low"]), 2),
                "close": round(float(row["Close"]), 2),
                "volume": int(row["Volume"])
            })
        return {
            "ticker": ticker.upper(),
            "period": period,
            "data_points": len(records),
            "latest_close": records[-1]["close"] if records else None,
            "earliest_date": records[0]["date"] if records else None,
            "latest_date": records[-1]["date"] if records else None,
            "prices": records
        }
    except Exception as e:
        return {"error": f"Failed to fetch price data: {str(e)}"}


def get_company_financials(ticker: str) -> dict:
    """Returns key fundamental metrics for the given ticker."""
    if not HAS_YFINANCE:
        return {"error": "yfinance library not installed."}
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        if not info or len(info) < 5:
            return {"error": f"No financial data found for ticker '{ticker}'."}

        pe_ratio = info.get("trailingPE") or info.get("forwardPE")
        forward_pe = info.get("forwardPE")
        debt_to_equity = info.get("debtToEquity")
        revenue_growth = info.get("revenueGrowth")
        earnings_growth = info.get("earningsGrowth")
        profit_margin = info.get("profitMargins")
        market_cap = info.get("marketCap")
        sector = info.get("sector", "Data Unavailable")
        industry = info.get("industry", "Data Unavailable")
        company_name = info.get("longName") or info.get("shortName", ticker.upper())
        current_price = info.get("currentPrice") or info.get("regularMarketPrice")
        fifty_two_week_high = info.get("fiftyTwoWeekHigh")
        fifty_two_week_low = info.get("fiftyTwoWeekLow")
        dividend_yield = info.get("dividendYield")
        beta = info.get("beta")
        eps_trailing = info.get("trailingEps")
        eps_forward = info.get("forwardEps")
        free_cash_flow = info.get("freeCashflow")
        return_on_equity = info.get("returnOnEquity")
        book_value = info.get("bookValue")
        price_to_book = info.get("priceToBook")

        return {
            "ticker": ticker.upper(),
            "company_name": company_name,
            "sector": sector,
            "industry": industry,
            "market_cap": market_cap,
            "current_price": current_price,
            "pe_ratio": round(pe_ratio, 2) if pe_ratio else "Data Unavailable",
            "forward_pe": round(forward_pe, 2) if forward_pe else "Data Unavailable",
            "debt_to_equity": round(debt_to_equity, 2) if debt_to_equity else "Data Unavailable",
            "revenue_growth": round(revenue_growth * 100, 2) if revenue_growth else "Data Unavailable",
            "earnings_growth": round(earnings_growth * 100, 2) if earnings_growth else "Data Unavailable",
            "profit_margin": round(profit_margin * 100, 2) if profit_margin else "Data Unavailable",
            "eps_trailing": eps_trailing if eps_trailing else "Data Unavailable",
            "eps_forward": eps_forward if eps_forward else "Data Unavailable",
            "dividend_yield": round(dividend_yield * 100, 2) if dividend_yield else "Data Unavailable",
            "beta": round(beta, 2) if beta else "Data Unavailable",
            "52_week_high": fifty_two_week_high,
            "52_week_low": fifty_two_week_low,
            "free_cash_flow": free_cash_flow if free_cash_flow else "Data Unavailable",
            "return_on_equity": round(return_on_equity * 100, 2) if return_on_equity else "Data Unavailable",
            "book_value": book_value if book_value else "Data Unavailable",
            "price_to_book": round(price_to_book, 2) if price_to_book else "Data Unavailable"
        }
    except Exception as e:
        return {"error": f"Failed to fetch financials: {str(e)}"}


def get_market_news(ticker: str) -> dict:
    """Fetches recent news headlines for the given ticker."""
    if not HAS_YFINANCE:
        return {"error": "yfinance library not installed."}
    try:
        stock = yf.Ticker(ticker)
        news = stock.news
        if not news:
            return {"ticker": ticker.upper(), "news": [], "count": 0, "note": "No recent news found."}

        articles = []
        for item in news[:10]:
            # yfinance news format can vary across versions
            title = item.get("title", item.get("content", {}).get("title", "No title")) if isinstance(item, dict) else "No title"
            publisher = item.get("publisher", item.get("content", {}).get("provider", {}).get("displayName", "Unknown")) if isinstance(item, dict) else "Unknown"
            link = item.get("link", item.get("content", {}).get("canonicalUrl", {}).get("url", "")) if isinstance(item, dict) else ""
            pub_date = item.get("providerPublishTime", "") if isinstance(item, dict) else ""
            if isinstance(pub_date, (int, float)):
                try:
                    pub_date = datetime.utcfromtimestamp(pub_date).strftime("%Y-%m-%d %H:%M UTC")
                except:
                    pub_date = str(pub_date)

            articles.append({
                "title": title,
                "publisher": publisher,
                "link": link,
                "published": str(pub_date)
            })
        return {
            "ticker": ticker.upper(),
            "count": len(articles),
            "news": articles
        }
    except Exception as e:
        return {"error": f"Failed to fetch news: {str(e)}"}


def calculate_technical_indicators(price_data: list) -> dict:
    """Computes RSI, SMA, EMA, Bollinger Bands, MACD, support/resistance from price records."""
    if not price_data or len(price_data) < 20:
        return {"error": "Insufficient price data for technical analysis (need at least 20 data points)."}

    try:
        closes = [p["close"] for p in price_data]
        highs = [p["high"] for p in price_data]
        lows = [p["low"] for p in price_data]
        n = len(closes)

        # --- Simple Moving Averages ---
        def sma(data, window):
            if len(data) < window:
                return None
            return round(sum(data[-window:]) / window, 2)

        sma_20 = sma(closes, 20)
        sma_50 = sma(closes, 50)
        sma_200 = sma(closes, 200)

        # --- Exponential Moving Averages ---
        def ema(data, window):
            if len(data) < window:
                return None
            multiplier = 2.0 / (window + 1)
            ema_val = sum(data[:window]) / window
            for price in data[window:]:
                ema_val = (price - ema_val) * multiplier + ema_val
            return round(ema_val, 2)

        ema_12 = ema(closes, 12)
        ema_26 = ema(closes, 26)
        ema_50 = ema(closes, 50)

        # --- MACD ---
        macd_line = None
        macd_signal = None
        macd_histogram = None
        if ema_12 is not None and ema_26 is not None:
            # Compute full MACD series for signal line
            def ema_series(data, window):
                if len(data) < window:
                    return []
                multiplier = 2.0 / (window + 1)
                result = [sum(data[:window]) / window]
                for price in data[window:]:
                    result.append((price - result[-1]) * multiplier + result[-1])
                return result

            ema12_series = ema_series(closes, 12)
            ema26_series = ema_series(closes, 26)
            # Align lengths
            offset = len(ema12_series) - len(ema26_series)
            if offset >= 0 and len(ema26_series) > 0:
                macd_series = [ema12_series[i + offset] - ema26_series[i] for i in range(len(ema26_series))]
                macd_line = round(macd_series[-1], 4) if macd_series else None
                # Signal line is 9-period EMA of MACD
                if len(macd_series) >= 9:
                    signal_series = ema_series(macd_series, 9)
                    if signal_series:
                        macd_signal = round(signal_series[-1], 4)
                        macd_histogram = round(macd_line - macd_signal, 4)

        # --- RSI (14-period) ---
        rsi = None
        rsi_period = 14
        if n > rsi_period:
            gains = []
            losses = []
            for i in range(1, n):
                change = closes[i] - closes[i - 1]
                gains.append(max(0, change))
                losses.append(max(0, -change))
            if len(gains) >= rsi_period:
                avg_gain = sum(gains[:rsi_period]) / rsi_period
                avg_loss = sum(losses[:rsi_period]) / rsi_period
                for i in range(rsi_period, len(gains)):
                    avg_gain = (avg_gain * (rsi_period - 1) + gains[i]) / rsi_period
                    avg_loss = (avg_loss * (rsi_period - 1) + losses[i]) / rsi_period
                if avg_loss == 0:
                    rsi = 100.0
                else:
                    rs = avg_gain / avg_loss
                    rsi = round(100 - (100 / (1 + rs)), 2)

        # --- Bollinger Bands (20-period, 2 std dev) ---
        bb_upper = None
        bb_lower = None
        bb_middle = None
        bb_width = None
        bb_position = None
        if n >= 20:
            bb_middle = sma_20
            window_data = closes[-20:]
            mean = sum(window_data) / 20
            variance = sum((x - mean) ** 2 for x in window_data) / 20
            std_dev = math.sqrt(variance)
            bb_upper = round(mean + 2 * std_dev, 2)
            bb_lower = round(mean - 2 * std_dev, 2)
            bb_width = round(bb_upper - bb_lower, 2)
            if bb_upper != bb_lower:
                bb_position = round((closes[-1] - bb_lower) / (bb_upper - bb_lower), 4)

        # --- Support and Resistance ---
        recent_lows = lows[-60:] if len(lows) >= 60 else lows
        recent_highs = highs[-60:] if len(highs) >= 60 else highs
        support = round(min(recent_lows), 2)
        resistance = round(max(recent_highs), 2)

        # Additional support/resistance using percentile
        sorted_closes_recent = sorted(closes[-60:] if len(closes) >= 60 else closes)
        support_25 = sorted_closes_recent[max(0, int(len(sorted_closes_recent) * 0.25))]
        resistance_75 = sorted_closes_recent[min(len(sorted_closes_recent) - 1, int(len(sorted_closes_recent) * 0.75))]

        # --- Trend determination ---
        current_price = closes[-1]
        trend = "Neutral"
        if sma_50 is not None and sma_200 is not None:
            if sma_50 > sma_200 and current_price > sma_50:
                trend = "Bullish"
            elif sma_50 < sma_200 and current_price < sma_50:
                trend = "Bearish"
            elif sma_50 > sma_200:
                trend = "Moderately Bullish"
            elif sma_50 < sma_200:
                trend = "Moderately Bearish"
        elif sma_50 is not None:
            if current_price > sma_50:
                trend = "Moderately Bullish"
            elif current_price < sma_50:
                trend = "Moderately Bearish"

        # --- Golden Cross / Death Cross detection ---
        cross_signal = None
        if sma_50 is not None and sma_200 is not None:
            # Check recent crossover if we have enough data
            if n >= 201:
                prev_sma50 = sum(closes[-(51):-1]) / 50
                prev_sma200 = sum(closes[-(201):-1]) / 200
                if prev_sma50 <= prev_sma200 and sma_50 > sma_200:
                    cross_signal = "Golden Cross (Bullish)"
                elif prev_sma50 >= prev_sma200 and sma_50 < sma_200:
                    cross_signal = "Death Cross (Bearish)"

        # --- RSI interpretation ---
        rsi_status = "Data Unavailable"
        if rsi is not None:
            if rsi > 70:
                rsi_status = "Overbought"
            elif rsi < 30:
                rsi_status = "Oversold"
            elif rsi > 60:
                rsi_status = "Approaching Overbought"
            elif rsi < 40:
                rsi_status = "Approaching Oversold"
            else:
                rsi_status = "Neutral"

        # --- Bollinger Band interpretation ---
        bb_status = "Data Unavailable"
        if bb_position is not None:
            if bb_position > 0.95:
                bb_status = "Near Upper Band (Potential Reversal/Breakout)"
            elif bb_position < 0.05:
                bb_status = "Near Lower Band (Potential Reversal/Bounce)"
            elif bb_position > 0.8:
                bb_status = "Upper Range"
            elif bb_position < 0.2:
                bb_status = "Lower Range"
            else:
                bb_status = "Within Normal Range"

        return {
            "current_price": current_price,
            "trend": trend,
            "cross_signal": cross_signal if cross_signal else "No recent crossover detected",
            "sma_20": sma_20 if sma_20 else "Data Unavailable",
            "sma_50": sma_50 if sma_50 else "Data Unavailable",
            "sma_200": sma_200 if sma_200 else "Data Unavailable (need 200+ data points)",
            "ema_12": ema_12 if ema_12 else "Data Unavailable",
            "ema_26": ema_26 if ema_26 else "Data Unavailable",
            "ema_50": ema_50 if ema_50 else "Data Unavailable",
            "rsi_14": rsi if rsi else "Data Unavailable",
            "rsi_status": rsi_status,
            "macd_line": macd_line if macd_line is not None else "Data Unavailable",
            "macd_signal": macd_signal if macd_signal is not None else "Data Unavailable",
            "macd_histogram": macd_histogram if macd_histogram is not None else "Data Unavailable",
            "bollinger_upper": bb_upper if bb_upper else "Data Unavailable",
            "bollinger_middle": bb_middle if bb_middle else "Data Unavailable",
            "bollinger_lower": bb_lower if bb_lower else "Data Unavailable",
            "bollinger_width": bb_width if bb_width else "Data Unavailable",
            "bollinger_position": bb_position if bb_position is not None else "Data Unavailable",
            "bollinger_status": bb_status,
            "support_level": support,
            "resistance_level": resistance,
            "support_25pct": round(support_25, 2),
            "resistance_75pct": round(resistance_75, 2)
        }
    except Exception as e:
        return {"error": f"Failed to calculate technical indicators: {str(e)}"}


def score_technicals(tech: dict) -> float:
    """Score technical indicators on a 0-100 scale."""
    if "error" in tech:
        return 50.0  # Neutral default
    score = 50.0
    # Trend
    trend = tech.get("trend", "Neutral")
    if trend == "Bullish":
        score += 15
    elif trend == "Moderately Bullish":
        score += 8
    elif trend == "Bearish":
        score -= 15
    elif trend == "Moderately Bearish":
        score -= 8

    # RSI
    rsi = tech.get("rsi_14")
    if isinstance(rsi, (int, float)):
        if 40 <= rsi <= 60:
            score += 5  # Neutral is fine
        elif 30 <= rsi < 40:
            score += 8  # Near oversold = potential buy
        elif rsi < 30:
            score += 10  # Oversold = buy signal
        elif 60 < rsi <= 70:
            score -= 3
        elif rsi > 70:
            score -= 10  # Overbought

    # MACD
    macd_hist = tech.get("macd_histogram")
    if isinstance(macd_hist, (int, float)):
        if macd_hist > 0:
            score += 8
        else:
            score -= 8

    # Bollinger position
    bb_pos = tech.get("bollinger_position")
    if isinstance(bb_pos, (int, float)):
        if 0.3 <= bb_pos <= 0.7:
            score += 5
        elif bb_pos > 0.95 or bb_pos < 0.05:
            score -= 5

    # Cross signal
    cross = tech.get("cross_signal", "")
    if "Golden Cross" in str(cross):
        score += 10
    elif "Death Cross" in str(cross):
        score -= 10

    return max(0, min(100, score))


def score_fundamentals(fin: dict) -> float:
    """Score fundamentals on a 0-100 scale."""
    if "error" in fin:
        return 50.0
    score = 50.0

    # P/E ratio
    pe = fin.get("pe_ratio")
    if isinstance(pe, (int, float)):
        if pe < 0:
            score -= 15  # Negative earnings
        elif pe < 15:
            score += 10  # Undervalued
        elif pe < 25:
            score += 5  # Fair
        elif pe < 40:
            score -= 3  # Slightly overvalued
        else:
            score -= 10  # Overvalued

    # Debt to equity
    de = fin.get("debt_to_equity")
    if isinstance(de, (int, float)):
        if de < 50:
            score += 10  # Low debt
        elif de < 100:
            score += 5
        elif de < 200:
            score -= 3
        else:
            score -= 10  # High debt

    # Revenue growth
    rg = fin.get("revenue_growth")
    if isinstance(rg, (int, float)):
        if rg > 20:
            score += 12
        elif rg > 10:
            score += 8
        elif rg > 0:
            score += 3
        elif rg > -10:
            score -= 5
        else:
            score -= 12

    # Profit margin
    pm = fin.get("profit_margin")
    if isinstance(pm, (int, float)):
        if pm > 20:
            score += 8
        elif pm > 10:
            score += 4
        elif pm > 0:
            score += 1
        else:
            score -= 8

    # ROE
    roe = fin.get("return_on_equity")
    if isinstance(roe, (int, float)):
        if roe > 20:
            score += 5
        elif roe > 10:
            score += 2
        elif roe < 0:
            score -= 5

    return max(0, min(100, score))


def score_sentiment(news: dict) -> float:
    """Basic sentiment scoring from news headlines."""
    if "error" in news:
        return 50.0
    articles = news.get("news", [])
    if not articles:
        return 50.0

    positive_words = [
        "beat", "surge", "rally", "upgrade", "growth", "profit", "record",
        "bullish", "buy", "outperform", "strong", "positive", "gain",
        "breakthrough", "innovation", "launch", "expansion", "boost",
        "exceed", "optimistic", "raise", "dividend", "beat expectations",
        "all-time high", "momentum"
    ]
    negative_words = [
        "miss", "decline", "drop", "downgrade", "loss", "lawsuit",
        "bearish", "sell", "underperform", "weak", "negative", "fall",
        "investigation", "recall", "debt", "default", "bankruptcy",
        "layoff", "cut", "warning", "risk", "concern", "trouble",
        "slump", "crash", "plunge", "disappointing"
    ]

    pos_count = 0
    neg_count = 0
    total = 0
    for article in articles:
        title = article.get("title", "").lower()
        if not title:
            continue
        total += 1
        for word in positive_words:
            if word in title:
                pos_count += 1
                break
        for word in negative_words:
            if word in title:
                neg_count += 1
                break

    if total == 0:
        return 50.0

    # Normalize to 0-100
    net = pos_count - neg_count
    ratio = net / total  # -1 to 1
    score = 50 + (ratio * 40)  # Maps to 10-90 range
    return max(0, min(100, round(score, 2)))


def categorize_news_sentiment(news: dict) -> str:
    """Categorize overall news sentiment."""
    s = score_sentiment(news)
    if s >= 65:
        return "Bullish"
    elif s <= 35:
        return "Bearish"
    else:
        return "Neutral"


def generate_risk_assessment(ticker: str, financials: dict, technicals: dict, sentiment_score: float) -> list:
    """Generate at least 3 bear case risks."""
    risks = []

    # Valuation risk
    pe = financials.get("pe_ratio")
    if isinstance(pe, (int, float)) and pe > 30:
        risks.append(f"Elevated valuation (P/E: {pe}x) leaves limited margin of safety; multiple compression could cause significant downside.")
    elif isinstance(pe, (int, float)) and pe < 0:
        risks.append("Negative earnings indicate the company is currently unprofitable, raising sustainability concerns.")

    # Debt risk
    de = financials.get("debt_to_equity")
    if isinstance(de, (int, float)) and de > 150:
        risks.append(f"High leverage (Debt/Equity: {de}%) increases vulnerability to rising interest rates and economic downturns.")

    # Technical risk
    trend = technicals.get("trend", "")
    if "Bearish" in trend:
        risks.append(f"Technical trend is {trend}; price trading below key moving averages suggests continued selling pressure.")

    rsi = technicals.get("rsi_14")
    if isinstance(rsi, (int, float)) and rsi > 70:
        risks.append(f"RSI at {rsi} indicates overbought conditions; a mean reversion pullback is likely.")

    # Sentiment risk
    if sentiment_score < 40:
        risks.append("Negative news sentiment may indicate developing headwinds not yet fully reflected in the price.")

    # Generic risks to ensure at least 3
    generic_risks = [
        "Macroeconomic risks: Rising interest rates, inflation, or recession could impact overall market valuations.",
        "Sector-specific regulatory changes could adversely affect the company's business model and margins.",
        "Competitive disruption from emerging players or technology shifts may erode market share.",
        "Geopolitical tensions and supply chain disruptions could impact revenue and profitability.",
        "Key management departures or governance issues could create uncertainty."
    ]

    idx = 0
    while len(risks) < 3 and idx < len(generic_risks):
        risks.append(generic_risks[idx])
        idx += 1

    return risks[:5]  # Cap at 5 risks


def compute_analyst_score(tech_score: float, fund_score: float, sent_score: float) -> dict:
    """Compute weighted analyst score: S = 0.4*Tech + 0.4*Fund + 0.2*Sent."""
    score = (0.4 * tech_score) + (0.4 * fund_score) + (0.2 * sent_score)
    score = round(score, 2)

    if score >= 75:
        outlook = "Bullish"
    elif score >= 60:
        outlook = "Moderately Bullish"
    elif score >= 45:
        outlook = "Neutral"
    elif score >= 30:
        outlook = "Moderately Bearish"
    else:
        outlook = "Bearish"

    return {
        "analyst_score": score,
        "score_breakdown": {
            "technical_score": round(tech_score, 2),
            "technical_weight": 0.4,
            "fundamental_score": round(fund_score, 2),
            "fundamental_weight": 0.4,
            "sentiment_score": round(sent_score, 2),
            "sentiment_weight": 0.2
        },
        "outlook": outlook
    }


def determine_technical_status(technicals: dict) -> str:
    """Generate a human-readable technical status summary."""
    if "error" in technicals:
        return "Data Unavailable"
    parts = []
    trend = technicals.get("trend", "Neutral")
    parts.append(f"Trend: {trend}")

    rsi = technicals.get("rsi_14")
    if isinstance(rsi, (int, float)):
        parts.append(f"RSI: {rsi} ({technicals.get('rsi_status', '')})")

    bb_status = technicals.get("bollinger_status", "")
    if bb_status and bb_status != "Data Unavailable":
        parts.append(f"Bollinger: {bb_status}")

    macd_hist = technicals.get("macd_histogram")
    if isinstance(macd_hist, (int, float)):
        macd_signal_str = "Bullish" if macd_hist > 0 else "Bearish"
        parts.append(f"MACD: {macd_signal_str}")

    return "; ".join(parts)


def determine_fundamental_health(financials: dict) -> str:
    """Generate a human-readable fundamental health summary."""
    if "error" in financials:
        return "Data Unavailable"
    parts = []
    pe = financials.get("pe_ratio")
    if isinstance(pe, (int, float)):
        parts.append(f"P/E: {pe}x")

    rg = financials.get("revenue_growth")
    if isinstance(rg, (int, float)):
        sign = "+" if rg > 0 else ""
        parts.append(f"Revenue Growth: {sign}{rg}%")

    de = financials.get("debt_to_equity")
    if isinstance(de, (int, float)):
        parts.append(f"D/E: {de}%")

    pm = financials.get("profit_margin")
    if isinstance(pm, (int, float)):
        parts.append(f"Margin: {pm}%")

    # Overall health label
    fund_score = score_fundamentals(financials)
    if fund_score >= 70:
        label = "Strong"
    elif fund_score >= 50:
        label = "Moderate"
    else:
        label = "Weak"

    return f"{label} ({'; '.join(parts)})" if parts else label


def execute(args: dict) -> dict:
    """
    Main entry point for the Stock Market Analysis skill.

    Args:
        args (dict): Expected keys:
            - ticker (str): Stock ticker symbol (e.g., "AAPL", "NVDA"). Required.
            - period (str): Data period, default "6mo". Options: 1mo, 3mo, 6mo, 1y, 2y, 5y.
            - analysis_type (str): "full", "technical", "fundamental", "sentiment". Default: "full".

    Returns:
        dict: Comprehensive analysis results.
    """
    try:
        # Validate inputs
        if not args or not isinstance(args, dict):
            return {
                "error": "Invalid arguments. Please provide a dict with at least a 'ticker' key.",
                "usage": {
                    "ticker": "AAPL",
                    "period": "6mo",
                    "analysis_type": "full"
                }
            }

        ticker = args.get("ticker", "").strip().upper().replace("$", "")
        if not ticker:
            return {
                "error": "Missing required 'ticker' parameter. Example: {'ticker': 'AAPL'}"
            }

        period = args.get("period", "6mo").strip()
        valid_periods = ["1mo", "3mo", "6mo", "1y", "2y", "5y", "10y", "max"]
        if period not in valid_periods:
            period = "6mo"

        analysis_type = args.get("analysis_type", "full").strip().lower()
        if analysis_type not in ["full", "technical", "fundamental", "sentiment"]:
            analysis_type = "full"

        if not HAS_YFINANCE:
            return {
                "error": "The 'yfinance' library is required but not installed. Please install it with: pip install yfinance",
                "ticker": ticker
            }

        result = {
            "ticker": ticker,
            "analysis_type": analysis_type,
            "timestamp": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC"),
            "disclaimer": "This analysis is for informational purposes only and does NOT constitute financial advice. Always consult a qualified financial advisor before making investment decisions."
        }

        # Fetch price data (needed for technical analysis)
        price_result = None
        if analysis_type in ["full", "technical"]:
            price_result = get_stock_price(ticker, period)
            if "error" in price_result:
                return {
                    "error": price_result["error"],
                    "ticker": ticker,
                    "suggestion": "Please verify the ticker symbol is correct and try again."
                }
            result["price_data_summary"] = {
                "period": price_result["period"],
                "data_points": price_result["data_points"],
                "latest_close": price_result["latest_close"],
                "date_range": f"{price_result['earliest_date']} to {price_result['latest_date']}"
            }

            # Check data recency
            if price_result.get("latest_date"):
                latest = datetime.strptime(price_result["latest_date"], "%Y-%m-%d")
                now = datetime.utcnow()
                age_hours = (now - latest).total_seconds() / 3600
                if age_hours > 24:
                    result["data_recency_warning"] = f"Latest price data is from {price_result['latest_date']}, which is more than 24 hours old. Markets may have moved since then."

        # --- Technical Analysis ---
        tech_score_val = 50.0
        technicals = {}
        if analysis_type in ["full", "technical"]:
            if price_result and "prices" in price_result:
                technicals = calculate_technical_indicators(price_result["prices"])
                tech_score_val = score_technicals(technicals)
                result["technical_analysis"] = {
                    "status": determine_technical_status(technicals),
                    "score": round(tech_score_val, 2),
                    "indicators": technicals
                }
            else:
                result["technical_analysis"] = {"error": "Insufficient price data for technical analysis."}

        # --- Fundamental Analysis ---
        fund_score_val = 50.0
        financials = {}
        if analysis_type in ["full", "fundamental"]:
            financials = get_company_financials(ticker)
            if "error" not in financials:
                fund_score_val = score_fundamentals(financials)
                result["fundamental_analysis"] = {
                    "health": determine_fundamental_health(financials),
                    "score": round(fund_score_val, 2),
                    "metrics": financials
                }
            else:
                result["fundamental_analysis"] = financials

        # --- Sentiment Analysis ---
        sent_score_val = 50.0
        news = {}
        if analysis_type in ["full", "sentiment"]:
            news = get_market_news(ticker)
            if "error" not in news:
                sent_score_val = score_sentiment(news)
                sentiment_category = categorize_news_sentiment(news)
                result["sentiment_analysis"] = {
                    "overall_sentiment": sentiment_category,
                    "score": round(sent_score_val, 2),
                    "news_count": news.get("count", 0),
                    "recent_headlines": [a.get("title", "") for a in news.get("news", [])[:5]]
                }
            else:
                result["sentiment_analysis"] = news

        # --- Composite Score & Outlook (only for full analysis) ---
        if analysis_type == "full":
            scoring = compute_analyst_score(tech_score_val, fund_score_val, sent_score_val)
            result["composite_analysis"] = scoring

            # Risk assessment
            risks = generate_risk_assessment(ticker, financials, technicals, sent_score_val)
            result["risk_assessment"] = {
                "bear_case_risks": risks
            }

            # Final summary
            company_name = financials.get("company_name", ticker)
            tech_status = determine_technical_status(technicals) if technicals else "Data Unavailable"
            fund_health = determine_fundamental_health(financials) if financials and "error" not in financials else "Data Unavailable"
            sent_label = categorize_news_sentiment(news) if news and "error" not in news else "Data Unavailable"

            result["summary"] = {
                "title": f"Analysis: ${ticker} ({company_name})",
                "technical_status": tech_status,
                "fundamental_health": fund_health,
                "sentiment": sent_label,
                "primary_risk": risks[0] if risks else "N/A",
                "outlook": scoring["outlook"],
                "analyst_score": scoring["analyst_score"]
            }

        return result

    except Exception as e:
        return {
            "error": f"An unexpected error occurred during analysis: {str(e)}",
            "ticker": args.get("ticker", "Unknown") if isinstance(args, dict) else "Unknown",
            "disclaimer": "This analysis is for informational purposes only and does NOT constitute financial advice."
        }
