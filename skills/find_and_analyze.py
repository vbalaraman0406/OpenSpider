import os
import json
import glob

# Search for calendar file
for root, dirs, files in os.walk('/Users/vbalaraman/OpenSpider'):
    for f in files:
        if 'calendar' in f.lower() or 'f1' in f.lower():
            print(f'Found: {os.path.join(root, f)}')

# Also check workspace directory
workspace = '/Users/vbalaraman/OpenSpider/workspace'
if os.path.exists(workspace):
    print(f'\nWorkspace contents:')
    for f in os.listdir(workspace):
        print(f'  {f}')
else:
    print('No workspace directory found')
