import yfinance as yf

def get_quote(ticker_symbol):
    try:
        stock = yf.Ticker(ticker_symbol)
        info = stock.info or {}
        price = info.get('regularMarketPrice') or info.get('currentPrice')
        prev_close = info.get('regularMarketPreviousClose') or info.get('previousClose')
        change = round(price - prev_close, 2) if price and prev_close else None
        change_pct = round((change / prev_close) * 100, 2) if change and prev_close else None
        hist = stock.history(period='5d')
        weekly_change = None
        if len(hist) >= 2:
            first_close = hist['Close'].iloc[0]
            last_close = hist['Close'].iloc[-1]
            weekly_change = round(((last_close - first_close) / first_close) * 100, 2)
        mc = info.get('marketCap')
        mc_str = f"${mc/1e9:.1f}B" if mc else 'N/A'
        return f"${price:.2f} | {change:+.2f} ({change_pct:+.2f}%) | Wk: {weekly_change:+.2f}% | MCap: {mc_str}"
    except Exception as e:
        return f"ERROR: {e}"

defense = {'LMT': 'Lockheed Martin', 'RTX': 'Raytheon', 'NOC': 'Northrop Grumman', 'GD': 'General Dynamics', 'BA': 'Boeing'}
for t, n in defense.items():
    print(f"{n} ({t}): {get_quote(t)}")
