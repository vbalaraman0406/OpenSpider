import os
import subprocess
import time

project_dir = '/Users/vbalaraman/OpenSpider/workspace/pitwall-ai'

# Add deploy timestamp to main.py to force GCP re-upload
main_path = os.path.join(project_dir, 'backend', 'main.py')
with open(main_path, 'r') as f:
    content = f.read()

# Add/update deploy timestamp comment
timestamp = time.time()
if '# DEPLOY_TS:' in content:
    lines = content.split('\n')
    lines = [l for l in lines if not l.startswith('# DEPLOY_TS:')]
    content = '\n'.join(lines)
content = f'# DEPLOY_TS: {timestamp}\n' + content

with open(main_path, 'w') as f:
    f.write(content)
print(f'Added deploy timestamp {timestamp} to main.py')

# Also add timestamp to fastf1_loader.py and routers to force re-upload
for fpath in ['backend/data/fastf1_loader.py', 'backend/routers/race.py', 'backend/routers/drivers.py']:
    full = os.path.join(project_dir, fpath)
    if os.path.isfile(full):
        with open(full, 'r') as f:
            c = f.read()
        if '# DEPLOY_TS:' in c:
            lines = c.split('\n')
            lines = [l for l in lines if not l.startswith('# DEPLOY_TS:')]
            c = '\n'.join(lines)
        c = f'# DEPLOY_TS: {timestamp}\n' + c
        with open(full, 'w') as f:
            f.write(c)
        print(f'Updated {fpath}')

print('All files stamped. Ready for deploy.')
