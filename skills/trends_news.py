import yfinance as yf

# 5-day trends for defense and energy
stocks = {
    'LMT': 'Lockheed Martin', 'RTX': 'Raytheon', 'NOC': 'Northrop Grumman',
    'GD': 'General Dynamics', 'LHX': 'L3Harris',
    'XOM': 'ExxonMobil', 'CVX': 'Chevron', 'OXY': 'Occidental'
}

print('=== 5-DAY TRENDS ===')
for sym, name in stocks.items():
    try:
        t = yf.Ticker(sym)
        hist = t.history(period='5d')
        if len(hist) > 0:
            prices = [f"{p:.2f}" for p in hist['Close'].tolist()]
            first = hist['Close'].iloc[0]
            last = hist['Close'].iloc[-1]
            wk_change = ((last - first) / first) * 100
            print(f"{name} ({sym}): {' -> '.join(prices)} | 5d: {wk_change:+.2f}%")
    except Exception as e:
        print(f"{name}: err {str(e)[:40]}")

# Also get 1-month trends for key items
print('\n=== 1-MONTH CHANGE ===')
key_tickers = {'CL=F': 'WTI Oil', 'BZ=F': 'Brent Oil', 'GC=F': 'Gold', '^GSPC': 'S&P 500', '^IXIC': 'NASDAQ', '^VIX': 'VIX'}
for sym, name in key_tickers.items():
    try:
        t = yf.Ticker(sym)
        hist = t.history(period='1mo')
        if len(hist) > 1:
            first = hist['Close'].iloc[0]
            last = hist['Close'].iloc[-1]
            mo_change = ((last - first) / first) * 100
            print(f"{name}: {first:.2f} -> {last:.2f} | 1mo: {mo_change:+.2f}%")
    except Exception as e:
        print(f"{name}: err {str(e)[:40]}")
