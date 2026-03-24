import os
import glob

# Check for log files
log_dirs = [
    '/Users/vbalaraman/OpenSpider/logs',
    '/Users/vbalaraman/OpenSpider/workspace/logs',
    '/Users/vbalaraman/OpenSpider',
]

for d in log_dirs:
    if os.path.exists(d):
        for f in os.listdir(d):
            if 'log' in f.lower() or f.endswith('.log') or f.endswith('.txt'):
                fp = os.path.join(d, f)
                size = os.path.getsize(fp)
                print(f'{fp} ({size} bytes)')

# Also check for auth/session state
auth_dirs = [
    '/Users/vbalaraman/OpenSpider/auth_info',
    '/Users/vbalaraman/OpenSpider/auth_info_baileys',
    '/Users/vbalaraman/OpenSpider/baileys_auth',
    '/Users/vbalaraman/OpenSpider/session',
]

print('\n=== AUTH/SESSION DIRS ===')
for d in auth_dirs:
    if os.path.exists(d):
        files = os.listdir(d)
        print(f'{d}: {len(files)} files')
        for f in files[:10]:
            fp = os.path.join(d, f)
            print(f'  {f} ({os.path.getsize(fp)} bytes)')
    else:
        print(f'{d}: NOT FOUND')

# Check for any session-related dirs
print('\n=== ALL DIRS IN PROJECT ROOT ===')
for f in os.listdir('/Users/vbalaraman/OpenSpider'):
    fp = os.path.join('/Users/vbalaraman/OpenSpider', f)
    if os.path.isdir(fp):
        print(f'  {f}/')
