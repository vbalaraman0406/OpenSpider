import json
import sys
sys.path.insert(0, '.')

# Get OXY details
with open('market_data.json', 'r') as f:
    data = json.load(f)

oxy = data.get('Energy', {}).get('OXY', {})
print('OXY Details:')
for k, v in oxy.items():
    print(f'  {k}: {v}')

# Get 5-day trends using yfinance
try:
    import yfinance as yf
    tickers = ['CL=F', 'BZ=F', 'GC=F', '^GSPC', '^IXIC', '^DJI', 'LMT', 'RTX', 'NOC', 'GD', 'BA', 'XOM', 'CVX', 'OXY']
    print('\n5-Day Trends:')
    for sym in tickers:
        try:
            t = yf.Ticker(sym)
            hist = t.history(period='5d')
            if len(hist) > 1:
                first = hist['Close'].iloc[0]
                last = hist['Close'].iloc[-1]
                chg = ((last - first) / first) * 100
                print(f'{sym}: start=${first:.2f} end=${last:.2f} 5d_chg={chg:+.2f}%')
        except Exception as e:
            print(f'{sym}: err {str(e)[:40]}')
except Exception as e:
    print(f'yfinance error: {e}')
