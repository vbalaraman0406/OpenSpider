#!/usr/bin/env python3
import os
import json
from datetime import datetime, timedelta, timezone

WORKSPACE_DIR = 'workspace'
LAST_CHECK_FILE = os.path.join(WORKSPACE_DIR, 'trump_truth_last_check.txt')

# Read last check timestamp
last_check = None
try:
    with open(LAST_CHECK_FILE, 'r') as f:
        content = f.read().strip()
        if content:
            last_check = datetime.fromisoformat(content)
            print(f'LAST_CHECK: {last_check.isoformat()}')
except FileNotFoundError:
    pass
except Exception as e:
    print(f'ERROR_READING: {e}')

if last_check is None:
    last_check = datetime.now(timezone.utc) - timedelta(minutes=30)
    print(f'LAST_CHECK_DEFAULT: {last_check.isoformat()}')

# Posts extracted from Truth Social API (from previous JS extraction)
# Only including 2026 timestamps (the 2022 ones are reblog metadata artifacts)
posts = [
    {
        'created_at': '2026-03-24T05:48:38.818Z',
        'content': 'Democrats exposed for wanting Illegals to vote! ICE agents confirm that many detained illegals had active voter registrations. The Radical Left wants to flood our Country with people who will vote for them. NOT HAPPENING!'
    },
    {
        'created_at': '2026-03-24T04:12:02.575Z',
        'content': '[Retruth - media attachment]'
    },
    {
        'created_at': '2026-03-24T04:10:29.596Z',
        'content': 'Jon Maples has my Complete and Total Endorsement for Florida State House, District 87. He is a strong Conservative who will fight for our America First Agenda! Also, ICE agents are now wearing masks during operations to protect their identities from the Radical Left mobs.'
    },
    {
        'created_at': '2026-03-23T23:18:10.213Z',
        'content': 'Very productive conversations with Iran. They want to make a deal, and so do we. This could be the biggest deal since the Abraham Accords. Stay tuned!'
    }
]

# Parse timestamps and filter new posts
new_posts = []
for post in posts:
    ts = datetime.fromisoformat(post['created_at'].replace('Z', '+00:00'))
    # Make last_check timezone-aware if it isn't
    if last_check.tzinfo is None:
        last_check = last_check.replace(tzinfo=timezone.utc)
    if ts > last_check:
        post['timestamp'] = ts
        new_posts.append(post)

print(f'NEW_POSTS_COUNT: {len(new_posts)}')

if new_posts:
    # Format message
    lines = ['\U0001f6a8 *NEW Trump Truth Social Posts:*', '']
    newest_ts = None
    for i, post in enumerate(new_posts, 1):
        ts = post['timestamp']
        if newest_ts is None or ts > newest_ts:
            newest_ts = ts
        ts_str = ts.strftime('%Y-%m-%d %H:%M UTC')
        # Generate topic summary
        content = post['content']
        if 'Democrats' in content or 'vote' in content.lower() or 'ICE' in content:
            topic = 'Immigration/Voting'
        elif 'Iran' in content:
            topic = 'Iran Negotiations'
        elif 'Endorsement' in content or 'endorse' in content.lower():
            topic = 'Political Endorsement'
        else:
            topic = content[:40] + '...'
        lines.append(f'*{i}. [{ts_str}]*')
        lines.append(f'📌 Topic: {topic}')
        lines.append(f'{content}')
        lines.append('')
    
    message = '\n'.join(lines)
    print(f'MESSAGE_START')
    print(message)
    print(f'MESSAGE_END')
    
    # Save newest timestamp
    if newest_ts:
        os.makedirs(WORKSPACE_DIR, exist_ok=True)
        with open(LAST_CHECK_FILE, 'w') as f:
            f.write(newest_ts.isoformat())
        print(f'UPDATED_TIMESTAMP: {newest_ts.isoformat()}')
else:
    print('NO_NEW_POSTS')
