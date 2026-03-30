import yfinance as yf
import json

# Define all tickers to analyze
tickers = {
    'Commodities': {
        'CL=F': 'WTI Crude Oil',
        'BZ=F': 'Brent Crude Oil', 
        'GC=F': 'Gold Futures',
        'SI=F': 'Silver Futures'
    },
    'Major Indices': {
        '^GSPC': 'S&P 500',
        '^IXIC': 'NASDAQ',
        '^DJI': 'Dow Jones'
    },
    'Defense Stocks': {
        'LMT': 'Lockheed Martin',
        'RTX': 'RTX Corp (Raytheon)',
        'NOC': 'Northrop Grumman',
        'GD': 'General Dynamics',
        'BA': 'Boeing'
    },
    'Energy Stocks': {
        'XOM': 'ExxonMobil',
        'CVX': 'Chevron',
        'OXY': 'Occidental Petroleum'
    }
}

results = {}

for category, ticker_dict in tickers.items():
    results[category] = []
    for symbol, name in ticker_dict.items():
        try:
            t = yf.Ticker(symbol)
            info = t.info
            hist = t.history(period='5d')
            hist_1mo = t.history(period='1mo')
            
            current = info.get('regularMarketPrice') or info.get('currentPrice') or (hist['Close'].iloc[-1] if len(hist) > 0 else 'N/A')
            prev_close = info.get('regularMarketPreviousClose') or info.get('previousClose', 'N/A')
            
            # Weekly change
            if len(hist) >= 2:
                week_start = hist['Close'].iloc[0]
                week_end = hist['Close'].iloc[-1]
                week_chg = ((week_end - week_start) / week_start) * 100
                week_chg_str = f"{week_chg:+.2f}%"
            else:
                week_chg_str = 'N/A'
            
            # Monthly change
            if len(hist_1mo) >= 2:
                mo_start = hist_1mo['Close'].iloc[0]
                mo_end = hist_1mo['Close'].iloc[-1]
                mo_chg = ((mo_end - mo_start) / mo_start) * 100
                mo_chg_str = f"{mo_chg:+.2f}%"
            else:
                mo_chg_str = 'N/A'
            
            day_chg = info.get('regularMarketChangePercent', 'N/A')
            if isinstance(day_chg, (int, float)):
                day_chg_str = f"{day_chg:+.2f}%"
            else:
                day_chg_str = 'N/A'
            
            mkt_cap = info.get('marketCap', 'N/A')
            if isinstance(mkt_cap, (int, float)) and mkt_cap > 0:
                if mkt_cap >= 1e12:
                    mkt_cap_str = f"${mkt_cap/1e12:.2f}T"
                elif mkt_cap >= 1e9:
                    mkt_cap_str = f"${mkt_cap/1e9:.2f}B"
                else:
                    mkt_cap_str = f"${mkt_cap/1e6:.2f}M"
            else:
                mkt_cap_str = 'N/A'
            
            high52 = info.get('fiftyTwoWeekHigh', 'N/A')
            low52 = info.get('fiftyTwoWeekLow', 'N/A')
            
            results[category].append({
                'Symbol': symbol,
                'Name': name,
                'Price': f"${current:.2f}" if isinstance(current, (int, float)) else str(current),
                'Day Chg': day_chg_str,
                'Week Chg': week_chg_str,
                'Month Chg': mo_chg_str,
                'Mkt Cap': mkt_cap_str,
                '52W High': f"${high52:.2f}" if isinstance(high52, (int, float)) else str(high52),
                '52W Low': f"${low52:.2f}" if isinstance(low52, (int, float)) else str(low52)
            })
            print(f"  ✓ {symbol} ({name}): ${current:.2f}" if isinstance(current, (int, float)) else f"  ✓ {symbol}: {current}")
        except Exception as e:
            print(f"  ✗ {symbol} ({name}): Error - {str(e)[:80]}")
            results[category].append({'Symbol': symbol, 'Name': name, 'Price': 'ERROR', 'Day Chg': 'N/A', 'Week Chg': 'N/A', 'Month Chg': 'N/A', 'Mkt Cap': 'N/A', '52W High': 'N/A', '52W Low': 'N/A'})

# Print formatted results
for category, items in results.items():
    print(f"\n=== {category} ===")
    for item in items:
        print(f"  {item['Symbol']:8s} | {item['Name']:25s} | Price: {item['Price']:>10s} | Day: {item['Day Chg']:>8s} | Week: {item['Week Chg']:>8s} | Month: {item['Month Chg']:>8s} | Cap: {item['Mkt Cap']:>10s}")
