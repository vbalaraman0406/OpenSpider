import json
import sys
sys.path.insert(0, '.')
from stock_quote import execute as get_quote

# Test with a simple stock ticker
result = get_quote({'ticker': 'AAPL'})
print(type(result))
print(json.dumps(result, indent=2, default=str))
