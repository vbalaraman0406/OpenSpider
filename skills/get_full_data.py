import yfinance as yf
import json

# Get all data again but print more concisely
tickers = {
    'ES=F': 'S&P 500 Futures', 'NQ=F': 'NASDAQ Futures', 'YM=F': 'Dow Futures',
    '^GSPC': 'S&P 500', '^IXIC': 'NASDAQ', '^DJI': 'Dow Jones',
    '^VIX': 'VIX', '^TNX': '10Y Treasury', 'CL=F': 'WTI Crude',
    'GC=F': 'Gold', 'BTC-USD': 'Bitcoin',
    '^FTSE': 'FTSE 100', '^GDAXI': 'DAX', '^FCHI': 'CAC 40',
    '^N225': 'Nikkei 225', '^HSI': 'Hang Seng', '000001.SS': 'Shanghai'
}

results = []
for symbol, name in tickers.items():
    try:
        t = yf.Ticker(symbol)
        info = t.fast_info
        price = info.get('lastPrice', info.get('last_price', 0))
        prev = info.get('previousClose', info.get('previous_close', 0))
        if price and prev and prev != 0:
            change = round(float(price) - float(prev), 2)
            pct = round((change / float(prev)) * 100, 2)
        else:
            change = 0
            pct = 0
        results.append(f"{name}|{round(float(price),2)}|{change}|{pct}%")
    except Exception as e:
        results.append(f"{name}|ERR|{str(e)[:30]}")

for r in results:
    print(r)
