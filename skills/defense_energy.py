import yfinance as yf

stocks = {
    'Defense': {
        'Lockheed Martin': 'LMT',
        'Raytheon (RTX)': 'RTX',
        'Northrop Grumman': 'NOC',
        'General Dynamics': 'GD',
        'L3Harris': 'LHX',
    },
    'Energy': {
        'ExxonMobil': 'XOM',
        'Chevron': 'CVX',
        'Occidental': 'OXY',
    }
}

for cat, items in stocks.items():
    print(f"=== {cat} ===")
    for name, sym in items.items():
        try:
            t = yf.Ticker(sym)
            info = t.info
            price = info.get('regularMarketPrice') or info.get('previousClose')
            prev = info.get('regularMarketPreviousClose') or info.get('previousClose')
            vol = info.get('volume') or info.get('regularMarketVolume') or 0
            w52h = info.get('fiftyTwoWeekHigh', 'N/A')
            w52l = info.get('fiftyTwoWeekLow', 'N/A')
            mc = info.get('marketCap', 0)
            pe = info.get('trailingPE', 'N/A')
            
            if price and prev and prev > 0:
                chg = price - prev
                chg_pct = (chg/prev)*100
                cs = f"{chg:+.2f} ({chg_pct:+.2f}%)"
            else:
                cs = 'N/A'
            
            if isinstance(mc, (int,float)) and mc > 0:
                mcs = f"${mc/1e9:.1f}B"
            else:
                mcs = 'N/A'
            
            if isinstance(vol, (int,float)) and vol > 0:
                vs = f"{vol/1e6:.1f}M"
            else:
                vs = 'N/A'
            
            print(f"{name} ({sym}): ${price} | Chg: {cs} | Vol: {vs} | P/E: {pe} | MktCap: {mcs} | 52wk: {w52l}-{w52h}")
        except Exception as e:
            print(f"{name}: ERR {str(e)[:60]}")
