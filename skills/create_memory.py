import json, os

os.makedirs('workspace/memory', exist_ok=True)

memory = {
    'last_check_time': '2026-03-20T19:21:00-07:00',
    'last_post_seen': {
        'approximate_timestamp': '2026-03-20T14:17:00-07:00',
        'content_snippet': 'We are getting very close to meeting our objectives as we consider winding down our...',
        'topic_summary': 'Middle East policy update - mentions Hormuz Strait policing by other nations and Middle Eastern allies'
    },
    'new_posts_found': False
}

with open('workspace/memory/trump_truthsocial_last_check.json', 'w') as f:
    json.dump(memory, f, indent=2)

print('Memory file created successfully.')
