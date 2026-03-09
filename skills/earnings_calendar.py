"""
earnings_calendar.py — Earnings reports: upcoming dates, EPS estimates, surprises.
Uses yfinance for earnings data.
"""
try:
    import yfinance as yf
    HAS_YF = True
except ImportError:
    HAS_YF = False

from datetime import datetime, timedelta
import json


def execute(args: dict) -> dict:
    if not HAS_YF:
        return {"error": "yfinance not installed. Run: pip install yfinance"}

    ticker = (args.get("ticker", "") or "").strip().upper().replace("$", "")
    date_range = (args.get("date_range", "") or "").strip().lower()

    # Single ticker mode: get earnings history + next date
    if ticker:
        try:
            stock = yf.Ticker(ticker)
            info = stock.info or {}

            result = {
                "ticker": ticker,
                "name": info.get("shortName", ticker),
                "timestamp": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC"),
                "disclaimer": "For informational purposes only. Not financial advice."
            }

            # Next earnings date
            try:
                cal = stock.calendar
                if cal is not None:
                    if isinstance(cal, dict):
                        earnings_date = cal.get("Earnings Date")
                        if earnings_date:
                            if isinstance(earnings_date, list) and len(earnings_date) > 0:
                                result["next_earnings_date"] = str(earnings_date[0])
                            else:
                                result["next_earnings_date"] = str(earnings_date)
                        if "Revenue Estimate" in cal:
                            result["revenue_estimate"] = cal.get("Revenue Estimate")
                        if "EPS Estimate" in cal:
                            result["eps_estimate"] = cal.get("EPS Estimate")
                    elif hasattr(cal, "to_dict"):
                        cal_dict = cal.to_dict()
                        result["calendar_raw"] = {str(k): str(v) for k, v in cal_dict.items()}
            except Exception:
                pass

            # Earnings history
            try:
                earnings = stock.earnings_history
                if earnings is not None and hasattr(earnings, "to_dict"):
                    history = []
                    records = earnings.to_dict("records") if hasattr(earnings, "to_dict") else []
                    for r in records[-8:]:  # Last 8 quarters
                        entry = {}
                        for k, v in r.items():
                            k_str = str(k).lower()
                            if hasattr(v, "isoformat"):
                                entry[k_str] = v.isoformat()
                            elif v is not None:
                                try:
                                    entry[k_str] = float(v) if isinstance(v, (int, float)) else str(v)
                                except (ValueError, TypeError):
                                    entry[k_str] = str(v)
                    if history:
                        result["earnings_history"] = history
            except Exception:
                pass

            # Quarterly earnings (EPS actual vs estimate)
            try:
                qe = stock.quarterly_earnings
                if qe is not None and not qe.empty:
                    quarters = []
                    for idx, row in qe.iterrows():
                        q = {"quarter": str(idx)}
                        if "Revenue" in row:
                            q["revenue"] = float(row["Revenue"]) if row["Revenue"] else None
                        if "Earnings" in row:
                            q["earnings"] = float(row["Earnings"]) if row["Earnings"] else None
                        quarters.append(q)
                    result["quarterly_earnings"] = quarters[-8:]
            except Exception:
                pass

            # Revenue & earnings trend
            try:
                fin = stock.financials
                if fin is not None and not fin.empty:
                    revenue_row = fin.loc["Total Revenue"] if "Total Revenue" in fin.index else None
                    if revenue_row is not None:
                        result["annual_revenue"] = {
                            str(col.date()): float(val) for col, val in revenue_row.items()
                            if val is not None
                        }
            except Exception:
                pass

            return result

        except Exception as e:
            return {"error": f"Failed to fetch earnings for {ticker}: {str(e)}"}

    # Calendar mode: get earnings for this week from popular tickers
    if date_range in ("this_week", "next_week", "today"):
        now = datetime.utcnow()
        if date_range == "today":
            start = now.date()
            end = start
        elif date_range == "next_week":
            start = (now + timedelta(days=(7 - now.weekday()))).date()
            end = start + timedelta(days=4)
        else:
            start = (now - timedelta(days=now.weekday())).date()
            end = start + timedelta(days=4)

        # Check a set of popular tickers for upcoming earnings
        check_tickers = [
            "AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "META", "TSLA", "JPM", "BAC",
            "JNJ", "WMT", "HD", "PG", "DIS", "NFLX", "AMD", "INTC", "CRM", "COST",
            "AVGO", "LLY", "UNH", "V", "MA", "ORCL", "ADBE", "PYPL", "SOFI", "PLTR"
        ]

        upcoming = []
        for t in check_tickers:
            try:
                stock = yf.Ticker(t)
                cal = stock.calendar
                if cal and isinstance(cal, dict):
                    ed = cal.get("Earnings Date")
                    if ed:
                        edate = ed[0] if isinstance(ed, list) else ed
                        if hasattr(edate, "date"):
                            edate = edate.date()
                        if start <= edate <= end:
                            upcoming.append({
                                "ticker": t,
                                "name": (stock.info or {}).get("shortName", t),
                                "earnings_date": str(edate),
                                "eps_estimate": cal.get("EPS Estimate"),
                                "revenue_estimate": cal.get("Revenue Estimate"),
                            })
            except Exception:
                continue

        return {
            "date_range": f"{start} to {end}",
            "upcoming_earnings": upcoming,
            "checked_tickers": len(check_tickers),
            "timestamp": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC"),
        }

    return {"error": "Provide either 'ticker' or 'date_range'. Examples: {\"ticker\": \"AAPL\"} or {\"date_range\": \"this_week\"}"}
