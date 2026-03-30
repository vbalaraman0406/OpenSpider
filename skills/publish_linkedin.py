import json, os, subprocess, sys

# Read the draft
workspace = os.path.join(os.getcwd(), 'workspace')
draft_file = os.path.join(workspace, 'linkedin_draft.json')

with open(draft_file, 'r') as f:
    draft = json.load(f)

print(f"Draft status: {draft['status']}")
print(f"Char count: {draft['char_count']}")

# Read linkedin_post.py to find the API endpoint
with open('linkedin_post.py', 'r') as f:
    script_content = f.read()

# Extract key parts - look for URL, API endpoint, headers
import re
urls = re.findall(r'https?://[^\s\'\"]+', script_content)
print(f"URLs found in script: {urls}")

# Look for localhost or API references
for line in script_content.split('\n'):
    line_lower = line.lower().strip()
    if any(kw in line_lower for kw in ['url', 'endpoint', 'api', 'post', 'request', 'host', 'port', 'gateway', 'linkedin']):
        if not line.strip().startswith('#'):
            print(f"Relevant line: {line.strip()}")
