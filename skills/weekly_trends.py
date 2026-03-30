import json
import sys
sys.path.insert(0, '.')

try:
    import yfinance as yf
except:
    pass

# Get weekly data for key commodities and indices
tickers = ['CL=F', 'BZ=F', 'GC=F', '^GSPC', '^IXIC', '^DJI', 'LMT', 'RTX', 'NOC', 'GD', 'BA', 'XOM', 'CVX', 'OXY']

for sym in tickers:
    try:
        t = yf.Ticker(sym)
        hist = t.history(period='5d')
        if len(hist) > 0:
            first_close = hist['Close'].iloc[0]
            last_close = hist['Close'].iloc[-1]
            weekly_chg = ((last_close - first_close) / first_close) * 100
            high_5d = hist['High'].max()
            low_5d = hist['Low'].min()
            avg_vol = hist['Volume'].mean()
            print(f"{sym}: 5d_start=${first_close:.2f} 5d_end=${last_close:.2f} 5d_chg={weekly_chg:.2f}% 5d_high=${high_5d:.2f} 5d_low=${low_5d:.2f}")
        else:
            print(f"{sym}: No 5d data")
    except Exception as e:
        print(f"{sym}: ERROR {str(e)[:60]}")

# Also read the saved detailed data
print('\n--- DETAILED QUOTE DATA ---')
with open('market_data.json', 'r') as f:
    data = json.load(f)

for cat, stocks in data.items():
    print(f"\n=== {cat} ===")
    for sym, info in stocks.items():
        w52h = info.get('52_week_high', info.get('year_high', 'N/A'))
        w52l = info.get('52_week_low', info.get('year_low', 'N/A'))
        vol = info.get('volume', 'N/A')
        mcap = info.get('market_cap', 'N/A')
        prev = info.get('previous_close', 'N/A')
        print(f"  {sym}: price=${info.get('price','N/A')} prev_close=${prev} vol={vol} mcap={mcap} 52wH={w52h} 52wL={w52l}")
