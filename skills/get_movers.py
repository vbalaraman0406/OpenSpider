import yfinance as yf

tickers = ['AAPL','MSFT','GOOGL','AMZN','NVDA','META','TSLA','AVGO','JPM','V',
           'UNH','JNJ','WMT','PG','MA','HD','XOM','CVX','MRK','ABBV',
           'CRM','ORCL','NFLX','AMD','INTC','BA','CAT','GS','MS','COST',
           'SMCI','PLTR','MSTR','IONQ','RIVN','SOFI','HOOD','RKLB','AFRM',
           'FDX','MU','GIS','ADBE','NKE','LEN','KBH','FIVE']

results = []
for t in tickers:
    try:
        tk = yf.Ticker(t)
        i = tk.info
        price = i.get('regularMarketPrice', None)
        prev = i.get('previousClose', None)
        pm = i.get('preMarketPrice', None)
        if pm and prev and prev > 0:
            chg = ((pm - prev) / prev) * 100
            results.append((t, price, prev, pm, chg))
        elif price and prev and prev > 0:
            chg = ((price - prev) / prev) * 100
            results.append((t, price, prev, pm, chg))
    except:
        pass

results.sort(key=lambda x: x[4], reverse=True)
print('TOP GAINERS (Pre-Market):')
for t, price, prev, pm, chg in results[:8]:
    print(f'  {t}: prev=${prev}, preMarket=${pm}, chg={chg:+.2f}%')

print('\nTOP LOSERS (Pre-Market):')
for t, price, prev, pm, chg in results[-8:]:
    print(f'  {t}: prev=${prev}, preMarket=${pm}, chg={chg:+.2f}%')

print('\nDone.')
