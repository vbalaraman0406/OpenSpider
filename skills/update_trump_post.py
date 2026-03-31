import sys

latest_post = sys.argv[1]
try:
    with open('workspace/trump_last_seen.txt', 'r') as f:
        existing = f.read().strip()
except FileNotFoundError:
    existing = ''

post_is_new = latest_post.strip() != existing

if post_is_new:
    with open('workspace/trump_last_seen.txt', 'w') as f:
        f.write(latest_post)
