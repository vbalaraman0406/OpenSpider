import json
import sys
sys.path.insert(0, '.')
from market_movers import execute

result = execute({'category': 'all', 'limit': '15'})
print(json.dumps(result, indent=2))
