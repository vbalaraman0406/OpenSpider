import os
import json
from datetime import datetime

MEMORY_FILE = 'workspace/memory/trump_truth_last_check.md'

# Current scraped posts from the prior agent's findings
# Only confirmed post today:
current_posts = [
    {
        'timestamp': '2026-03-21T16:44:00-07:00',
        'summary': 'Iran/Strait of Hormuz ultimatum',
        'content_preview': 'Post about Iran and Strait of Hormuz ultimatum (confirmed from today ~4:44 PM PDT)'
    }
]

# Read previous check state
previous_timestamps = set()
if os.path.exists(MEMORY_FILE):
    with open(MEMORY_FILE, 'r') as f:
        content = f.read()
    print(f'Previous check file found:\n{content}')
    for line in content.strip().split('\n'):
        if line.startswith('- '):
            # Extract timestamp from format: - TIMESTAMP | preview
            parts = line[2:].split(' | ')
            if parts:
                previous_timestamps.add(parts[0].strip())
else:
    print('No previous check file found. First run.')

print(f'Previous timestamps: {previous_timestamps}')

# Determine new posts (not in previous check AND within last 30 minutes)
now = datetime(2026, 3, 21, 21, 44)  # Current time: 9:44 PM PDT
new_posts = []
for post in current_posts:
    ts = post['timestamp']
    if ts not in previous_timestamps:
        # Check if within 30 minutes - the post at 4:44 PM is ~5 hours old
        # Parse the timestamp
        try:
            post_time = datetime.fromisoformat(ts)
            post_time_naive = post_time.replace(tzinfo=None)
            diff_minutes = (now - post_time_naive).total_seconds() / 60
            print(f'Post at {ts} is {diff_minutes:.0f} minutes old')
            if diff_minutes <= 30:
                new_posts.append(post)
                print(f'  -> NEW (within 30 min window)')
            else:
                print(f'  -> OLD (outside 30 min window, skipping alert)')
        except Exception as e:
            print(f'Error parsing timestamp: {e}')
    else:
        print(f'Post {ts} already reported in previous check')

print(f'\nNew posts to alert: {len(new_posts)}')
if new_posts:
    print('SEND_ALERT=YES')
    for p in new_posts:
        print(f'  {p["timestamp"]} - {p["summary"]}')
else:
    print('SEND_ALERT=NO')
    print('No new Trump posts detected.')

# Save current state for next check
os.makedirs('workspace/memory', exist_ok=True)
with open(MEMORY_FILE, 'w') as f:
    f.write(f'# Trump Truth Social - Last Check\n')
    f.write(f'# Checked at: 2026-03-21 21:44 PDT\n')
    f.write(f'# Posts found:\n')
    for post in current_posts:
        f.write(f'- {post["timestamp"]} | {post["content_preview"][:50]}\n')

print('\nState file updated.')
