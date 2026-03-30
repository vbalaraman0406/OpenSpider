import os
import time

base = '/Users/vbalaraman/OpenSpider/workspace/pitwall-ai'

# Write fresh DEPLOY_MARKER.txt to force GCP hash change
ts = str(time.time())
marker_path = os.path.join(base, 'DEPLOY_MARKER.txt')
with open(marker_path, 'w') as f:
    f.write('DEPLOY_TIMESTAMP=' + ts + '\n')
print('DEPLOY_MARKER.txt written with timestamp:', ts)

# Update main.py timestamp to force re-upload
main_path = os.path.join(base, 'backend', 'main.py')
with open(main_path, 'r') as f:
    content = f.read()

import re
content = re.sub(r'# DEPLOY_TIMESTAMP_[\d.]+', '# DEPLOY_TIMESTAMP_' + ts, content)
if 'DEPLOY_TIMESTAMP' not in content:
    content = content + '\n# DEPLOY_TIMESTAMP_' + ts + '\n'

with open(main_path, 'w') as f:
    f.write(content)
print('main.py updated with timestamp:', ts)

# Verify dist/index.html is clean
index_path = os.path.join(base, 'frontend', 'dist', 'index.html')
with open(index_path, 'r') as f:
    html = f.read()
print('dist/index.html length:', len(html))
print('Has /f1/assets/index-Cv5HRAMH.js:', 'index-Cv5HRAMH.js' in html)
print('Has inline script:', 'innerHTML' in html)
print('HTML content:')
print(html)
