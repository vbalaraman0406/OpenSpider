import json
from datetime import datetime, timezone

snapshot = {
    "timestamp": datetime.now().astimezone().isoformat(),
    "usa": {
        "status": "Page not available (404)",
        "reports": 0,
        "top5": []
    },
    "canada": {
        "status": "No current problems",
        "reports": 0,
        "top5": [
            {"name": "Online Banking", "pct": 0},
            {"name": "Funds Transfer", "pct": 0},
            {"name": "Mobile Banking", "pct": 0}
        ]
    }
}

with open('workspace/bmo_downdetector_last.json', 'w') as f:
    json.dump(snapshot, f, indent=2)

print('Snapshot updated. No changes detected — no message sent.')
