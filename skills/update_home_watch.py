import json, os
from datetime import datetime

data = {
    "address": "9405 NE 102nd St, Vancouver, WA 98662",
    "baselinePrice": 799000,
    "currentPrice": 799000,
    "status": "active",
    "lastChecked": datetime.now().isoformat(),
    "sources": {
        "zillow": {
            "price": 799000,
            "status": "active",
            "url": "https://www.zillow.com/homedetails/9405-NE-102nd-St-Vancouver-WA-98662/66649389_zpid/"
        },
        "redfin": {
            "price": 799000,
            "status": "active",
            "url": "https://www.redfin.com/WA/Vancouver/9405-NE-102nd-St-98662/home/14618170"
        },
        "realtor": {
            "price": 799000,
            "status": "active",
            "url": "https://www.realtor.com/realestateandhomes-detail/9405-NE-102nd-St_Vancouver_WA_98662_M18431-42963"
        }
    }
}

os.makedirs('workspace/memory', exist_ok=True)
with open('workspace/memory/home_watch_9405_ne_102nd.json', 'w') as f:
    json.dump(data, f, indent=2)

print('Written successfully')
print(json.dumps(data, indent=2))