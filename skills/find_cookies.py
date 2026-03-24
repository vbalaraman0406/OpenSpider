import os
import time

base = '/Users/vbalaraman/OpenSpider'
results = []

for root, dirs, files in os.walk(base):
    # Skip node_modules and .git
    dirs[:] = [d for d in dirs if d not in ('node_modules', '.git', 'venv', '__pycache__')]
    for f in files:
        fp = os.path.join(root, f)
        lower = f.lower()
        if any(kw in lower for kw in ['cookie', 'f1', 'fantasy', 'session', 'auth', 'token']):
            try:
                mtime = os.path.getmtime(fp)
                size = os.path.getsize(fp)
                results.append((fp, mtime, size))
            except:
                pass

# Sort by modification time, newest first
results.sort(key=lambda x: x[1], reverse=True)

print('=== Cookie/F1/Auth related files ===')
for fp, mt, sz in results[:30]:
    print(f'{time.ctime(mt)} | {sz:>8} bytes | {fp}')

# Also check workspace directory contents
print('\n=== Workspace directory listing ===')
workspace = os.path.join(base, 'workspace')
if os.path.exists(workspace):
    for item in sorted(os.listdir(workspace)):
        fp = os.path.join(workspace, item)
        try:
            mtime = os.path.getmtime(fp)
            size = os.path.getsize(fp) if os.path.isfile(fp) else 0
            isdir = 'DIR' if os.path.isdir(fp) else 'FILE'
            print(f'{time.ctime(mtime)} | {isdir:>4} | {size:>8} bytes | {item}')
        except:
            pass

# Check browser_profiles
print('\n=== Browser profiles ===')
bp = os.path.join(workspace, 'browser_profiles')
if os.path.exists(bp):
    for root2, dirs2, files2 in os.walk(bp):
        for f in files2:
            fp = os.path.join(root2, f)
            try:
                mtime = os.path.getmtime(fp)
                size = os.path.getsize(fp)
                print(f'{time.ctime(mtime)} | {size:>8} bytes | {fp}')
            except:
                pass

# Check for recently modified files (last 10 minutes)
print('\n=== Recently modified files (last 30 min) ===')
now = time.time()
recent = []
for root, dirs, files in os.walk(base):
    dirs[:] = [d for d in dirs if d not in ('node_modules', '.git', 'venv', '__pycache__')]
    for f in files:
        fp = os.path.join(root, f)
        try:
            mtime = os.path.getmtime(fp)
            if now - mtime < 1800:  # 30 minutes
                recent.append((fp, mtime, os.path.getsize(fp)))
        except:
            pass
recent.sort(key=lambda x: x[1], reverse=True)
for fp, mt, sz in recent[:30]:
    print(f'{time.ctime(mt)} | {sz:>8} bytes | {fp}')
