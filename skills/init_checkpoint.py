import json
import os

# Ensure directory exists
os.makedirs('workspace/memory', exist_ok=True)

checkpoint = {
    'last_check_time': '2026-03-20T21:52:00-07:00',
    'last_check_epoch': 1774090320,
    'posts_seen': [],
    'status': 'no_data_available',
    'note': 'First run - browser relay not attached and HTTP requests blocked by security guard. No posts could be scraped.'
}

with open('workspace/memory/trump_truth_social_last_check.json', 'w') as f:
    json.dump(checkpoint, f, indent=2)

print('Checkpoint file created successfully')
print(json.dumps(checkpoint, indent=2))
