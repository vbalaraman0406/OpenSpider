import yfinance as yf

# Try to get news from yfinance for relevant tickers
tickers_to_check = ['CL=F', 'BZ=F', 'GC=F', 'LMT', 'RTX', 'XLE']

for sym in tickers_to_check:
    try:
        t = yf.Ticker(sym)
        # Get current price for futures
        info = t.info
        price = info.get('regularMarketPrice') or info.get('currentPrice', 'N/A')
        prev = info.get('regularMarketPreviousClose', 0)
        if isinstance(price, (int,float)) and isinstance(prev, (int,float)) and prev:
            pct = round((price-prev)/prev*100, 2)
        else:
            pct = 'N/A'
        name = info.get('shortName', sym)
        print(f"{sym}: {name} | Price: {price} | Change: {pct}%")
        
        # Try to get news
        news = t.news
        if news:
            for article in news[:3]:
                title = article.get('title', 'No title')
                pub = article.get('publisher', '')
                print(f"  -> {title} ({pub})")
        else:
            print(f"  -> No news available")
    except Exception as e:
        print(f"{sym}: Error - {str(e)[:60]}")
    print()
