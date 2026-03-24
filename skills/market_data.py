import yfinance as yf
import json

tickers = {
    'WTI Crude Oil': 'CL=F',
    'Brent Crude Oil': 'BZ=F',
    'Gold': 'GC=F',
    'S&P 500': '^GSPC',
    'NASDAQ': '^IXIC',
    'Lockheed Martin': 'LMT',
    'Raytheon (RTX)': 'RTX',
    'Northrop Grumman': 'NOC',
    'General Dynamics': 'GD',
    'L3Harris': 'LHX'
}

for name, symbol in tickers.items():
    try:
        t = yf.Ticker(symbol)
        info = t.fast_info
        hist = t.history(period='5d')
        if len(hist) > 0:
            current = hist['Close'].iloc[-1]
            prev = hist['Close'].iloc[0] if len(hist) > 1 else current
            change_pct = ((current - prev) / prev) * 100
            high_52 = getattr(info, 'year_high', 'N/A')
            low_52 = getattr(info, 'year_low', 'N/A')
            mkt_cap = getattr(info, 'market_cap', 'N/A')
            print(f"{name} ({symbol}): ${current:.2f} | 5d Chg: {change_pct:+.2f}% | 52w H: {high_52} | 52w L: {low_52} | MktCap: {mkt_cap}")
        else:
            print(f"{name} ({symbol}): No data available")
    except Exception as e:
        print(f"{name} ({symbol}): Error - {e}")
