import sys
sys.path.insert(0, '/Users/vbalaraman/OpenSpider/skills')

import yfinance as yf
from datetime import datetime, timedelta

def get_quote(ticker):
    try:
        stock = yf.Ticker(ticker)
        info = stock.info or {}
        price = info.get('regularMarketPrice') or info.get('currentPrice', 0)
        prev_close = info.get('regularMarketPreviousClose') or info.get('previousClose', 0)
        change = round(price - prev_close, 2) if price and prev_close else None
        change_pct = round((change / prev_close) * 100, 2) if change and prev_close else None
        
        hist = stock.history(period='5d')
        weekly_change_pct = None
        if len(hist) >= 2:
            first_close = float(hist['Close'].iloc[0])
            last_close = float(hist['Close'].iloc[-1])
            weekly_change_pct = round(((last_close - first_close) / first_close) * 100, 2)
        
        return {
            'ticker': ticker,
            'name': info.get('shortName') or info.get('longName', ticker),
            'price': price,
            'change': change,
            'change_pct': change_pct,
            'weekly_change_pct': weekly_change_pct,
            'volume': info.get('regularMarketVolume') or info.get('volume'),
            'market_cap': info.get('marketCap'),
            '52w_high': info.get('fiftyTwoWeekHigh'),
            '52w_low': info.get('fiftyTwoWeekLow'),
            'pe_ratio': info.get('trailingPE'),
        }
    except Exception as e:
        return {'ticker': ticker, 'error': str(e)}

print('=== COMMODITIES ===')
for t in ['CL=F', 'BZ=F', 'GC=F']:
    q = get_quote(t)
    label = {'CL=F': 'WTI Crude Oil', 'BZ=F': 'Brent Crude Oil', 'GC=F': 'Gold'}.get(t, t)
    print(f"{label}: ${q.get('price','N/A')} | Daily: {q.get('change_pct','N/A')}% | Weekly: {q.get('weekly_change_pct','N/A')}%")

print('\n=== MAJOR INDICES ===')
for t in ['^GSPC', '^IXIC', '^DJI']:
    q = get_quote(t)
    label = {'^GSPC': 'S&P 500', '^IXIC': 'NASDAQ', '^DJI': 'Dow Jones'}.get(t, t)
    print(f"{label}: {q.get('price','N/A')} | Daily: {q.get('change_pct','N/A')}% | Weekly: {q.get('weekly_change_pct','N/A')}%")

print('\n=== DEFENSE STOCKS ===')
for t in ['LMT', 'RTX', 'NOC', 'GD']:
    q = get_quote(t)
    print(f"{q.get('name', t)} ({t}): ${q.get('price','N/A')} | Daily: {q.get('change_pct','N/A')}% | Weekly: {q.get('weekly_change_pct','N/A')}% | P/E: {q.get('pe_ratio','N/A')} | MCap: {q.get('market_cap','N/A')}")

print('\n=== ENERGY STOCKS ===')
for t in ['XOM', 'CVX', 'OXY']:
    q = get_quote(t)
    print(f"{q.get('name', t)} ({t}): ${q.get('price','N/A')} | Daily: {q.get('change_pct','N/A')}% | Weekly: {q.get('weekly_change_pct','N/A')}% | P/E: {q.get('pe_ratio','N/A')} | MCap: {q.get('market_cap','N/A')}")

print('\n=== VIX ===')
q = get_quote('^VIX')
print(f"VIX: {q.get('price','N/A')} | Daily: {q.get('change_pct','N/A')}% | Weekly: {q.get('weekly_change_pct','N/A')}%")
