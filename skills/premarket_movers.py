import yfinance as yf
import json

# Get pre-market movers by checking popular large-cap stocks for big moves
tickers_to_check = [
    'AAPL','MSFT','GOOGL','AMZN','NVDA','META','TSLA','AMD','NFLX','CRM',
    'AVGO','ORCL','INTC','BA','DIS','PYPL','UBER','COIN','PLTR','SNOW',
    'SMCI','ARM','MRVL','MU','QCOM','SHOP','SQ','ROKU','RIVN','LCID',
    'NIO','SOFI','HOOD','RBLX','SNAP','PINS','ZM','DOCU','CRWD','PANW',
    'JPM','GS','BAC','WFC','V','MA','UNH','JNJ','PFE','MRNA'
]

movers = []
for ticker in tickers_to_check:
    try:
        t = yf.Ticker(ticker)
        fi = t.fast_info
        price = fi.get('lastPrice', fi.get('last_price', None))
        prev = fi.get('previousClose', fi.get('previous_close', None))
        if price and prev and prev > 0:
            change = price - prev
            pct = (change / prev) * 100
            movers.append({'ticker': ticker, 'price': round(price, 2), 'change': round(change, 2), 'pct': round(pct, 2)})
    except:
        pass

movers.sort(key=lambda x: x['pct'], reverse=True)

print('=== TOP 5 GAINERS ===')
for m in movers[:5]:
    print(f"{m['ticker']}: ${m['price']} ({'+' if m['change']>=0 else ''}{m['change']}, {'+' if m['pct']>=0 else ''}{m['pct']}%)")

print('\n=== TOP 5 LOSERS ===')
for m in movers[-5:]:
    print(f"{m['ticker']}: ${m['price']} ({'+' if m['change']>=0 else ''}{m['change']}, {'+' if m['pct']>=0 else ''}{m['pct']}%)")

print('\n=== MOST ACTIVE (by absolute % change) ===')
by_abs = sorted(movers, key=lambda x: abs(x['pct']), reverse=True)
for m in by_abs[:5]:
    print(f"{m['ticker']}: ${m['price']} ({'+' if m['change']>=0 else ''}{m['change']}, {'+' if m['pct']>=0 else ''}{m['pct']}%)")
