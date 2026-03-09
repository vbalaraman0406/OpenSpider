"""
portfolio_tracker.py — Portfolio performance monitor with persistent storage.
Tracks holdings, calculates P&L, sector exposure, and total portfolio value.
Holdings are saved to workspace/portfolio.json for persistence.
"""
try:
    import yfinance as yf
    HAS_YF = True
except ImportError:
    HAS_YF = False

import json
import os
from datetime import datetime

PORTFOLIO_FILE = os.path.join(os.getcwd(), "workspace", "portfolio.json")


def load_portfolio() -> list:
    """Load holdings from persistent storage."""
    if os.path.exists(PORTFOLIO_FILE):
        try:
            with open(PORTFOLIO_FILE, "r") as f:
                return json.load(f)
        except Exception:
            pass
    return []


def save_portfolio(holdings: list):
    """Save holdings to persistent storage."""
    os.makedirs(os.path.dirname(PORTFOLIO_FILE), exist_ok=True)
    with open(PORTFOLIO_FILE, "w") as f:
        json.dump(holdings, f, indent=2)


def execute(args: dict) -> dict:
    if not HAS_YF:
        return {"error": "yfinance not installed. Run: pip install yfinance"}

    action = (args.get("action", "status") or "status").lower()
    holdings = load_portfolio()

    # --- ADD holding ---
    if action == "add":
        ticker = (args.get("ticker", "") or "").strip().upper().replace("$", "")
        shares = float(args.get("shares", 0))
        cost_basis = float(args.get("cost_basis", 0))
        if not ticker or shares <= 0:
            return {"error": "Provide 'ticker', 'shares' (>0), and 'cost_basis'. Example: {\"action\": \"add\", \"ticker\": \"AAPL\", \"shares\": 50, \"cost_basis\": 150}"}

        # Check if already exists, update if so
        existing = next((h for h in holdings if h["ticker"] == ticker), None)
        if existing:
            # Average cost basis
            total_shares = existing["shares"] + shares
            total_cost = (existing["shares"] * existing["cost_basis"]) + (shares * cost_basis)
            existing["shares"] = total_shares
            existing["cost_basis"] = round(total_cost / total_shares, 2)
        else:
            holdings.append({"ticker": ticker, "shares": shares, "cost_basis": cost_basis})

        save_portfolio(holdings)
        return {"success": True, "message": f"Added {shares} shares of {ticker} at ${cost_basis}", "holdings_count": len(holdings)}

    # --- REMOVE holding ---
    if action == "remove":
        ticker = (args.get("ticker", "") or "").strip().upper().replace("$", "")
        if not ticker:
            return {"error": "Provide 'ticker' to remove."}
        before = len(holdings)
        holdings = [h for h in holdings if h["ticker"] != ticker]
        save_portfolio(holdings)
        return {"success": True, "removed": ticker, "holdings_count": len(holdings), "was_found": len(holdings) < before}

    # --- SET entire portfolio ---
    if action == "set":
        new_holdings = args.get("holdings", [])
        if not isinstance(new_holdings, list):
            return {"error": "Provide 'holdings' as a list of {ticker, shares, cost_basis} objects."}
        formatted = []
        for h in new_holdings:
            formatted.append({
                "ticker": (h.get("ticker", "") or "").strip().upper(),
                "shares": float(h.get("shares", 0)),
                "cost_basis": float(h.get("cost_basis", 0)),
            })
        save_portfolio(formatted)
        return {"success": True, "message": f"Portfolio set with {len(formatted)} positions.", "holdings_count": len(formatted)}

    # --- STATUS: calculate P&L ---
    if not holdings:
        return {
            "message": "Portfolio is empty. Add holdings with: {\"action\": \"add\", \"ticker\": \"AAPL\", \"shares\": 50, \"cost_basis\": 150}",
            "holdings_count": 0
        }

    positions = []
    total_cost = 0
    total_value = 0
    sectors = {}

    for h in holdings:
        ticker = h["ticker"]
        shares = h["shares"]
        cost = h["cost_basis"]

        try:
            stock = yf.Ticker(ticker)
            info = stock.info or {}
            price = info.get("regularMarketPrice") or info.get("currentPrice", 0)
            sector = info.get("sector", "Unknown")
            name = info.get("shortName", ticker)

            position_cost = shares * cost
            position_value = shares * price
            pnl = position_value - position_cost
            pnl_pct = round((pnl / position_cost) * 100, 2) if position_cost else 0

            total_cost += position_cost
            total_value += position_value
            sectors[sector] = sectors.get(sector, 0) + position_value

            positions.append({
                "ticker": ticker,
                "name": name,
                "shares": shares,
                "cost_basis": cost,
                "current_price": price,
                "position_value": round(position_value, 2),
                "pnl": round(pnl, 2),
                "pnl_pct": pnl_pct,
                "sector": sector,
                "weight_pct": 0,  # Calculated below
            })
        except Exception as e:
            positions.append({"ticker": ticker, "error": str(e)})

    # Calculate portfolio weights
    for p in positions:
        if "position_value" in p and total_value > 0:
            p["weight_pct"] = round((p["position_value"] / total_value) * 100, 2)

    # Sector allocation
    sector_allocation = {}
    for s, v in sectors.items():
        sector_allocation[s] = {
            "value": round(v, 2),
            "weight_pct": round((v / total_value) * 100, 2) if total_value else 0
        }

    total_pnl = total_value - total_cost
    total_pnl_pct = round((total_pnl / total_cost) * 100, 2) if total_cost else 0

    # Sort by P&L descending
    positions.sort(key=lambda x: x.get("pnl", 0), reverse=True)

    return {
        "portfolio_summary": {
            "total_cost": round(total_cost, 2),
            "total_value": round(total_value, 2),
            "total_pnl": round(total_pnl, 2),
            "total_pnl_pct": total_pnl_pct,
            "positions_count": len(positions),
        },
        "positions": positions,
        "sector_allocation": sector_allocation,
        "timestamp": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC"),
        "disclaimer": "For informational purposes only. Not financial advice."
    }
