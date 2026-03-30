import yfinance as yf
import json

# Get top movers - check some well-known volatile stocks for pre-market activity
# We'll check a broad list and find biggest movers
tickers_to_check = ['AAPL','MSFT','GOOGL','AMZN','NVDA','META','TSLA','AMD','NFLX','CRM',
    'COIN','PLTR','SOFI','RIVN','NIO','LCID','MARA','RIOT','SQ','SHOP',
    'SNOW','DKNG','RBLX','ABNB','UBER','LYFT','BA','JPM','GS','WFC',
    'XOM','CVX','PFE','MRNA','JNJ','UNH','LLY','COST','WMT','TGT',
    'DIS','PYPL','INTC','MU','AVGO','QCOM','ARM','SMCI','DELL','CRWD']

movers = []
for sym in tickers_to_check:
    try:
        t = yf.Ticker(sym)
        info = t.fast_info
        price = float(info.get('lastPrice', info.get('last_price', 0)))
        prev = float(info.get('previousClose', info.get('previous_close', 0)))
        if price and prev and prev != 0:
            change = round(price - prev, 2)
            pct = round((change / prev) * 100, 2)
            movers.append((sym, price, change, pct))
    except:
        pass

# Sort by pct change
movers.sort(key=lambda x: x[3], reverse=True)

print('=== TOP GAINERS ===')
for m in movers[:7]:
    print(f"{m[0]}|{m[1]}|{m[2]}|{m[3]}%")

print('=== TOP LOSERS ===')
for m in movers[-7:]:
    print(f"{m[0]}|{m[1]}|{m[2]}|{m[3]}%")

# Get news for major indices
print('\n=== MARKET NEWS ===')
for sym in ['^GSPC', 'AAPL', 'NVDA', 'TSLA']:
    try:
        t = yf.Ticker(sym)
        news = t.news
        if news:
            for n in news[:2]:
                title = n.get('title', n.get('content', {}).get('title', 'N/A'))
                print(f"{sym}: {title}")
    except Exception as e:
        print(f"{sym}: News error - {str(e)[:40]}")
