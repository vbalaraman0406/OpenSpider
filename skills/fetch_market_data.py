import yfinance as yf

# Fetch S&P 500 and NASDAQ data
sp500 = yf.Ticker('^GSPC')
nasdaq = yf.Ticker('^IXIC')
vix = yf.Ticker('^VIX')
tny = yf.Ticker('^TNX')

end_date = '2026-03-05'
start_date = '2026-02-01'

sp_hist = sp500.history(start=start_date, end=end_date)
nq_hist = nasdaq.history(start=start_date, end=end_date)
vix_hist = vix.history(start=start_date, end=end_date)
tny_hist = tny.history(start=start_date, end=end_date)

print('=== S&P 500 Last 5 Days ===')
if len(sp_hist) > 0:
    print(sp_hist.tail(5).to_string())
else:
    print('No data available')

print('\n=== NASDAQ Last 5 Days ===')
if len(nq_hist) > 0:
    print(nq_hist.tail(5).to_string())
else:
    print('No data available')

print('\n=== VIX Last 3 Days ===')
if len(vix_hist) > 0:
    print(vix_hist.tail(3).to_string())
else:
    print('No data available')

print('\n=== 10Y Treasury Last 3 Days ===')
if len(tny_hist) > 0:
    print(tny_hist.tail(3).to_string())
else:
    print('No data available')

# Volume stats
if len(sp_hist) >= 20:
    sp_vol_20avg = sp_hist['Volume'].tail(20).mean()
    sp_vol_today = sp_hist['Volume'].iloc[-1]
    print(f'\nS&P 500 Volume Today: {sp_vol_today:,.0f}, 20-day avg: {sp_vol_20avg:,.0f}')
else:
    print(f'\nS&P 500 data points: {len(sp_hist)}')

if len(nq_hist) >= 20:
    nq_vol_20avg = nq_hist['Volume'].tail(20).mean()
    nq_vol_today = nq_hist['Volume'].iloc[-1]
    print(f'NASDAQ Volume Today: {nq_vol_today:,.0f}, 20-day avg: {nq_vol_20avg:,.0f}')
else:
    print(f'NASDAQ data points: {len(nq_hist)}')

# Calculate daily changes
if len(sp_hist) >= 2:
    sp_close = sp_hist['Close'].iloc[-1]
    sp_prev = sp_hist['Close'].iloc[-2]
    sp_chg = sp_close - sp_prev
    sp_pct = (sp_chg / sp_prev) * 100
    print(f'\nS&P 500 Close: {sp_close:.2f}, Change: {sp_chg:+.2f} ({sp_pct:+.2f}%)')

if len(nq_hist) >= 2:
    nq_close = nq_hist['Close'].iloc[-1]
    nq_prev = nq_hist['Close'].iloc[-2]
    nq_chg = nq_close - nq_prev
    nq_pct = (nq_chg / nq_prev) * 100
    print(f'NASDAQ Close: {nq_close:.2f}, Change: {nq_chg:+.2f} ({nq_pct:+.2f}%)')

if len(vix_hist) >= 2:
    vix_close = vix_hist['Close'].iloc[-1]
    vix_prev = vix_hist['Close'].iloc[-2]
    vix_chg = vix_close - vix_prev
    print(f'VIX Close: {vix_close:.2f}, Change: {vix_chg:+.2f}')

if len(tny_hist) >= 1:
    tny_close = tny_hist['Close'].iloc[-1]
    print(f'10Y Treasury Yield: {tny_close:.3f}%')
