import json
import os
from datetime import datetime

path = 'workspace/skills/trump_truth_last_check.json'
os.makedirs(os.path.dirname(path), exist_ok=True)

data = {
    'last_check_timestamp': '2026-03-21T09:02:00-07:00',
    'last_check_epoch': int(datetime.now().timestamp()),
    'seen_post_ids': [],
    'seen_posts': [],
    'note': 'Initial baseline. No posts were scraped on first run due to aggregator access failures.'
}

with open(path, 'w') as f:
    json.dump(data, f, indent=2)

print('Created initial last check file:')
print(json.dumps(data, indent=2))
