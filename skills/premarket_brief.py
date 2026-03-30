import yfinance as yf
import json
from datetime import datetime

# Fetch futures and market data
tickers = {
    'ES=F': 'S&P 500 Futures',
    'NQ=F': 'NASDAQ Futures', 
    'YM=F': 'Dow Jones Futures',
    '^VIX': 'VIX',
    '^TNX': '10-Yr Treasury Yield',
    'CL=F': 'Crude Oil WTI',
    'BTC-USD': 'Bitcoin',
    '^FTSE': 'FTSE 100',
    '^GDAXI': 'DAX',
    '^FCHI': 'CAC 40',
    '^N225': 'Nikkei 225',
    '^HSI': 'Hang Seng',
    '000001.SS': 'Shanghai Composite',
    'GC=F': 'Gold',
}

results = {}
for ticker, name in tickers.items():
    try:
        t = yf.Ticker(ticker)
        info = t.fast_info
        price = info.last_price
        prev = info.previous_close
        change = price - prev if price and prev else 0
        pct = (change / prev * 100) if prev else 0
        results[ticker] = {'name': name, 'price': round(price, 2), 'change': round(change, 2), 'pct': round(pct, 2)}
    except Exception as e:
        results[ticker] = {'name': name, 'price': 'N/A', 'change': 'N/A', 'pct': 'N/A', 'error': str(e)}

# Pre-market movers - get some active stocks
mover_tickers = ['AAPL', 'MSFT', 'NVDA', 'TSLA', 'AMZN', 'META', 'GOOGL', 'AMD', 'NFLX', 'JPM', 'BA', 'DIS', 'COIN', 'PLTR', 'SOFI', 'RIVN', 'NIO', 'INTC', 'CRM', 'V']
movers = []
for t in mover_tickers:
    try:
        tk = yf.Ticker(t)
        info = tk.fast_info
        price = info.last_price
        prev = info.previous_close
        change = price - prev if price and prev else 0
        pct = (change / prev * 100) if prev else 0
        movers.append({'ticker': t, 'price': round(price, 2), 'change': round(change, 2), 'pct': round(pct, 2)})
    except:
        pass

movers.sort(key=lambda x: x['pct'], reverse=True)
top_gainers = movers[:5]
top_losers = sorted(movers, key=lambda x: x['pct'])[:5]

print(json.dumps({'market_data': results, 'top_gainers': top_gainers, 'top_losers': top_losers}, indent=2))
