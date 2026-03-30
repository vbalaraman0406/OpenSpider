import yfinance as yf

defense = {'LMT': 'Lockheed Martin', 'RTX': 'Raytheon (RTX)', 'NOC': 'Northrop Grumman', 'GD': 'General Dynamics', 'BA': 'Boeing'}

for sym, name in defense.items():
    try:
        t = yf.Ticker(sym)
        info = t.fast_info
        hist_1m = t.history(period='1mo')
        current = info.get('lastPrice', None) or (hist_1m['Close'].iloc[-1] if len(hist_1m) > 0 else None)
        prev_close = info.get('previousClose', None)
        day_chg = round(((current - prev_close) / prev_close * 100), 2) if prev_close and current else 'N/A'
        week_ago = hist_1m['Close'].iloc[-6] if len(hist_1m) > 5 else hist_1m['Close'].iloc[0]
        week_chg = round(((current - week_ago) / week_ago * 100), 2) if week_ago and current else 'N/A'
        month_start = hist_1m['Close'].iloc[0]
        month_chg = round(((current - month_start) / month_start * 100), 2) if month_start and current else 'N/A'
        print(f'{name:<22} {sym:<6} ${current:<10.2f} {day_chg:>7}% {week_chg:>7}% {month_chg:>7}%')
    except Exception as e:
        print(f'{name:<22} {sym:<6} ERROR: {e}')
