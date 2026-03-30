import yfinance as yf
import json
from datetime import datetime, timedelta

def get_quote(ticker_symbol, name=None):
    try:
        t = yf.Ticker(ticker_symbol)
        hist = t.history(period='5d')
        if hist.empty:
            return {'ticker': ticker_symbol, 'name': name or ticker_symbol, 'price': 'N/A', 'change': 'N/A', 'change_pct': 'N/A', 'volume': 'N/A'}
        
        current = hist['Close'].iloc[-1]
        if len(hist) >= 2:
            prev = hist['Close'].iloc[-2]
            change = current - prev
            change_pct = (change / prev) * 100
        else:
            change = 0
            change_pct = 0
        
        # Weekly trend
        if len(hist) >= 5:
            week_start = hist['Close'].iloc[0]
            week_change_pct = ((current - week_start) / week_start) * 100
        else:
            week_change_pct = change_pct
        
        vol = hist['Volume'].iloc[-1] if 'Volume' in hist.columns else 0
        
        return {
            'ticker': ticker_symbol,
            'name': name or ticker_symbol,
            'price': round(current, 2),
            'change': round(change, 2),
            'change_pct': round(change_pct, 2),
            'week_change_pct': round(week_change_pct, 2),
            'volume': f"{int(vol):,}" if vol else 'N/A'
        }
    except Exception as e:
        return {'ticker': ticker_symbol, 'name': name or ticker_symbol, 'price': 'ERR', 'change': 'ERR', 'change_pct': 'ERR', 'week_change_pct': 'ERR', 'volume': 'ERR', 'error': str(e)}

# Commodities
print("=== COMMODITIES ===")
commodities = [
    ('CL=F', 'WTI Crude Oil'),
    ('BZ=F', 'Brent Crude Oil'),
    ('GC=F', 'Gold Spot'),
    ('SI=F', 'Silver Spot'),
]
for sym, name in commodities:
    q = get_quote(sym, name)
    print(f"{q['name']} ({q['ticker']}): ${q['price']} | Day: {q['change']} ({q['change_pct']}%) | Week: {q.get('week_change_pct','N/A')}%")

# Indices
print("\n=== MAJOR INDICES ===")
indices = [
    ('^GSPC', 'S&P 500'),
    ('^IXIC', 'NASDAQ Composite'),
    ('^DJI', 'Dow Jones'),
    ('^VIX', 'VIX (Fear Index)'),
]
for sym, name in indices:
    q = get_quote(sym, name)
    print(f"{q['name']} ({q['ticker']}): {q['price']} | Day: {q['change']} ({q['change_pct']}%) | Week: {q.get('week_change_pct','N/A')}%")

# Defense stocks
print("\n=== DEFENSE/AEROSPACE ===")
defense = [
    ('LMT', 'Lockheed Martin'),
    ('RTX', 'RTX Corp'),
    ('NOC', 'Northrop Grumman'),
    ('GD', 'General Dynamics'),
    ('BA', 'Boeing'),
]
for sym, name in defense:
    q = get_quote(sym, name)
    print(f"{q['name']} ({q['ticker']}): ${q['price']} | Day: {q['change']} ({q['change_pct']}%) | Week: {q.get('week_change_pct','N/A')}% | Vol: {q['volume']}")

# Energy stocks
print("\n=== ENERGY SECTOR ===")
energy = [
    ('XOM', 'ExxonMobil'),
    ('CVX', 'Chevron'),
    ('OXY', 'Occidental Petroleum'),
    ('HAL', 'Halliburton'),
    ('SLB', 'Schlumberger'),
]
for sym, name in energy:
    q = get_quote(sym, name)
    print(f"{q['name']} ({q['ticker']}): ${q['price']} | Day: {q['change']} ({q['change_pct']}%) | Week: {q.get('week_change_pct','N/A')}% | Vol: {q['volume']}")

print("\n=== DATA TIMESTAMP ===")
print(f"Data fetched: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
