import yfinance as yf
import json

tickers = {
    'ES=F': 'S&P 500 Futures', 'NQ=F': 'NASDAQ Futures', 'YM=F': 'Dow Jones Futures',
    '^VIX': 'VIX', '^TNX': '10-Yr Treasury Yield', 'CL=F': 'Crude Oil WTI',
    'BTC-USD': 'Bitcoin', '^FTSE': 'FTSE 100', '^GDAXI': 'DAX', '^FCHI': 'CAC 40',
    '^N225': 'Nikkei 225', '^HSI': 'Hang Seng', '000001.SS': 'Shanghai Composite', 'GC=F': 'Gold'
}
results = {}
for ticker, name in tickers.items():
    try:
        t = yf.Ticker(ticker)
        info = t.fast_info
        price = info.last_price
        prev = info.previous_close
        change = round(price - prev, 2) if price and prev else 0
        pct = round((change / prev * 100), 2) if prev else 0
        results[ticker] = {'name': name, 'price': round(price, 2), 'change': change, 'pct': pct}
    except Exception as e:
        results[ticker] = {'name': name, 'price': 'N/A', 'change': 'N/A', 'pct': 'N/A'}

mover_tickers = ['AAPL','MSFT','NVDA','TSLA','AMZN','META','GOOGL','AMD','NFLX','JPM','BA','DIS','COIN','PLTR','SOFI','RIVN','NIO','INTC','CRM','V']
movers = []
for t in mover_tickers:
    try:
        tk = yf.Ticker(t)
        info = tk.fast_info
        price = info.last_price
        prev = info.previous_close
        change = round(price - prev, 2) if price and prev else 0
        pct = round((change / prev * 100), 2) if prev else 0
        movers.append({'ticker': t, 'price': round(price, 2), 'change': change, 'pct': pct})
    except:
        pass

movers.sort(key=lambda x: x['pct'], reverse=True)
data = {'market': results, 'gainers': movers[:5], 'losers': sorted(movers, key=lambda x: x['pct'])[:5]}
with open('/tmp/premarket_data.json', 'w') as f:
    json.dump(data, f)
print('Data saved. Summary:')
for k, v in results.items():
    print(f"{v['name']}: {v['price']} ({v['change']:+} / {v['pct']:+}%)" if isinstance(v['change'], (int, float)) else f"{v['name']}: N/A")
print('\nTop Gainers:')
for g in movers[:5]:
    print(f"  {g['ticker']}: ${g['price']} ({g['pct']:+}%)")
print('Top Losers:')
for l in sorted(movers, key=lambda x: x['pct'])[:5]:
    print(f"  {l['ticker']}: ${l['price']} ({l['pct']:+}%)")
