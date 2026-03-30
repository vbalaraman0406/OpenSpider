import json, sys
sys.path.insert(0, '.')
from stock_quote import execute

for ticker in ['SPY', 'QQQ']:
    result = execute({'ticker': ticker})
    print(f"=== {ticker} ===")
    for k, v in result.items():
        print(f"  {k}: {v}")
    print()
