import yfinance as yf
import json
from datetime import datetime

data = {}

# S&P 500 and NASDAQ futures
tickers = {
    'ES=F': 'S&P 500 Futures',
    'NQ=F': 'NASDAQ Futures',
    'YM=F': 'Dow Futures',
    '^GSPC': 'S&P 500',
    '^IXIC': 'NASDAQ Composite',
    '^DJI': 'Dow Jones',
    '^VIX': 'VIX',
    '^TNX': 'US 10-Year Treasury Yield',
    'CL=F': 'WTI Crude Oil',
    'GC=F': 'Gold',
    'BTC-USD': 'Bitcoin',
    '^FTSE': 'FTSE 100',
    '^GDAXI': 'DAX',
    '^FCHI': 'CAC 40',
    '^N225': 'Nikkei 225',
    '^HSI': 'Hang Seng',
    '000001.SS': 'Shanghai Composite',
    'DX-Y.NYB': 'US Dollar Index'
}

for symbol, name in tickers.items():
    try:
        t = yf.Ticker(symbol)
        info = t.fast_info
        price = info.get('lastPrice', info.get('last_price', 'N/A'))
        prev = info.get('previousClose', info.get('previous_close', 'N/A'))
        if price != 'N/A' and prev != 'N/A' and prev != 0:
            change = round(price - prev, 2)
            pct = round((change / prev) * 100, 2)
        else:
            change = 'N/A'
            pct = 'N/A'
        data[symbol] = {'name': name, 'price': price, 'prev_close': prev, 'change': change, 'pct_change': pct}
    except Exception as e:
        data[symbol] = {'name': name, 'price': 'N/A', 'error': str(e)}

print(json.dumps(data, indent=2, default=str))
