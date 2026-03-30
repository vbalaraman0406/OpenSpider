import os

# Check auth session files
auth_dir = '/Users/vbalaraman/OpenSpider/baileys_auth_info'
files = os.listdir(auth_dir)
print(f'=== AUTH DIR: {len(files)} files ===')
for f in sorted(files):
    fp = os.path.join(auth_dir, f)
    print(f'  {f} ({os.path.getsize(fp)} bytes)')

# Check server.log for Family group errors - last 200 lines
print('\n=== RECENT SERVER LOG (Family group related) ===')
with open('/Users/vbalaraman/OpenSpider/server.log', 'r') as f:
    lines = f.readlines()

# Search for Family group related errors
family_jid = '14156249639-1373117853@g.us'
keywords = ['not-acceptable', 'No sessions', family_jid, 'Family', 'group', 'error', 'failed']

found = []
for i, line in enumerate(lines):
    line_lower = line.lower()
    if any(k.lower() in line_lower for k in keywords):
        found.append((i+1, line.rstrip()[:200]))

# Show last 40 matches
print(f'Total matches: {len(found)}')
for lineno, text in found[-40:]:
    print(f'  L{lineno}: {text}')
