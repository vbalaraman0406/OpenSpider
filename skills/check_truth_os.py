import os
import json
import re
import html
from datetime import datetime, timezone, timedelta

now = datetime.now(timezone.utc)
window_start = now - timedelta(minutes=30)
print(f"Current UTC: {now.isoformat()}")
print(f"Window start: {window_start.isoformat()}")
print(f"Current PDT: {(now - timedelta(hours=7)).strftime('%Y-%m-%d %H:%M:%S')}")
print()

url = 'https://truthsocial.com/api/v1/accounts/107780257626128497/statuses?limit=10'
cmd = 'curl -s -m 15 "' + url + '"'
print(f"Running: {cmd}")

stream = os.popen(cmd)
raw = stream.read()
stream.close()

if not raw.strip():
    print("Empty response from curl")
else:
    try:
        data = json.loads(raw)
        print(f"Got {len(data)} posts")
        new_posts = []
        for post in data:
            created_str = post.get('created_at', '')
            try:
                created = datetime.fromisoformat(created_str.replace('Z', '+00:00'))
            except:
                continue
            content_html = post.get('content', '')
            content = re.sub(r'<[^>]+>', '', content_html)
            content = html.unescape(content).strip()
            post_id = post.get('id', '')
            pdt_time = (created - timedelta(hours=7)).strftime('%Y-%m-%d %I:%M %p PDT')
            print(f"Post {post_id}: {pdt_time} | {content[:120]}")
            if created >= window_start:
                new_posts.append({'id': post_id, 'time_pdt': pdt_time, 'time_utc': created.isoformat(), 'content': content})
        print(f"\nNEW POSTS (last 30 min): {len(new_posts)}")
        for p in new_posts:
            print(f"\nID: {p['id']}\nTime: {p['time_pdt']}\nContent: {p['content'][:500]}")
        result_path = '/Users/vbalaraman/OpenSpider/workspace/truth_check_result.json'
        with open(result_path, 'w') as f:
            json.dump({'new_posts': new_posts, 'all_count': len(data), 'check_time': now.isoformat()}, f, indent=2)
        print(f"\nResults saved to {result_path}")
    except json.JSONDecodeError as e:
        print(f"JSON parse error: {e}")
        print(f"Raw (first 1000): {raw[:1000]}")
