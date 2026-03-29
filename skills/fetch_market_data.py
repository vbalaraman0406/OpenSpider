import yfinance as yf
import json

tickers = {
    'WTI Crude (USO)': 'USO',
    'Brent Crude (BNO)': 'BNO',
    'WTI Crude Futures (CL=F)': 'CL=F',
    'Brent Crude Futures (BZ=F)': 'BZ=F',
    'Gold (GLD)': 'GLD',
    'Spot Gold (GC=F)': 'GC=F',
    'S&P 500 (SPY)': 'SPY',
    'NASDAQ (QQQ)': 'QQQ',
    'S&P 500 Index (^GSPC)': '^GSPC',
    'NASDAQ Index (^IXIC)': '^IXIC',
    'Lockheed Martin (LMT)': 'LMT',
    'Raytheon (RTX)': 'RTX',
    'Northrop Grumman (NOC)': 'NOC',
    'General Dynamics (GD)': 'GD',
    'L3Harris (LHX)': 'LHX',
    'VIX (^VIX)': '^VIX'
}

results = {}
for name, ticker in tickers.items():
    try:
        t = yf.Ticker(ticker)
        info = t.fast_info
        hist = t.history(period='5d')
        
        last_price = info.last_price if hasattr(info, 'last_price') else None
        prev_close = info.previous_close if hasattr(info, 'previous_close') else None
        
        change = None
        change_pct = None
        if last_price and prev_close and prev_close != 0:
            change = last_price - prev_close
            change_pct = (change / prev_close) * 100
        
        # 5-day trend
        five_day_change = None
        if len(hist) >= 2:
            first_close = hist['Close'].iloc[0]
            last_close = hist['Close'].iloc[-1]
            if first_close != 0:
                five_day_change = ((last_close - first_close) / first_close) * 100
        
        results[name] = {
            'price': round(last_price, 2) if last_price else 'N/A',
            'prev_close': round(prev_close, 2) if prev_close else 'N/A',
            'change': round(change, 2) if change else 'N/A',
            'change_pct': round(change_pct, 2) if change_pct else 'N/A',
            '5d_change_pct': round(five_day_change, 2) if five_day_change else 'N/A'
        }
        print(f"{name}: ${results[name]['price']} | Day: {results[name]['change_pct']}% | 5D: {results[name]['5d_change_pct']}%")
    except Exception as e:
        print(f"{name}: ERROR - {str(e)[:80]}")
        results[name] = {'price': 'N/A', 'error': str(e)[:80]}

print('\n--- DONE ---')
