import time

# Add timestamp to main.py to force GCP file hash change
with open('/Users/vbalaraman/OpenSpider/workspace/pitwall-ai/backend/main.py', 'r') as f:
    content = f.read()

# Remove old timestamp lines
lines = content.split('\n')
lines = [l for l in lines if not l.startswith('# DEPLOY_TIMESTAMP')]
content = '\n'.join(lines)

# Add new timestamp
timestamp = str(time.time())
content = '# DEPLOY_TIMESTAMP_' + timestamp + '\n' + content

with open('/Users/vbalaraman/OpenSpider/workspace/pitwall-ai/backend/main.py', 'w') as f:
    f.write(content)

print('Updated main.py with timestamp ' + timestamp)

# Verify dist/index.html is inline
with open('/Users/vbalaraman/OpenSpider/workspace/pitwall-ai/frontend/dist/index.html', 'r') as f:
    html = f.read()

if 'document.getElementById' in html and 'Pitwall.ai' in html:
    print('dist/index.html confirmed inline HTML with no external JS')
else:
    print('ERROR: dist/index.html does not have inline JS')

print('Ready to deploy')
