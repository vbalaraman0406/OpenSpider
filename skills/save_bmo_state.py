import json
from datetime import datetime

data = {
    "ca": {
        "status": "No current problems",
        "problems": [
            {"name": "Online Banking", "pct": 0},
            {"name": "Funds Transfer", "pct": 0},
            {"name": "Mobile Banking", "pct": 0}
        ],
        "url": "https://downdetector.ca/status/bmo/"
    },
    "us": {
        "status": "Page not available (404)",
        "problems": [],
        "url": "https://downdetector.com/status/bmo/"
    },
    "timestamp": datetime.now().isoformat()
}

with open('workspace/bmo_downdetector_last.json', 'w') as f:
    json.dump(data, f, indent=2)

print('State saved successfully')
print(json.dumps(data, indent=2))
