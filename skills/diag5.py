# Read whatsapp.ts for: 1) not-acceptable handling, 2) connection events, 3) group validation
with open('/Users/vbalaraman/OpenSpider/src/whatsapp.ts', 'r') as f:
    content = f.read()
    lines = content.split('\n')

# Search for 'not-acceptable' handling
print('=== not-acceptable mentions ===')
for i, line in enumerate(lines):
    if 'not-acceptable' in line.lower() or 'notacceptable' in line.lower():
        print(f'{i+1}: {line.rstrip()[:200]}')

# Search for connection.update / connection events
print('\n=== connection.update handling ===')
for i, line in enumerate(lines):
    if 'connection.update' in line or 'DisconnectReason' in line or 'loggedOut' in line:
        print(f'{i+1}: {line.rstrip()[:200]}')

# Check for getParticipatingGroups function
print('\n=== getParticipatingGroups function ===')
for i, line in enumerate(lines):
    if 'getParticipatingGroups' in line or 'groupFetchAllParticipating' in line:
        print(f'{i+1}: {line.rstrip()[:200]}')

# Now check tools.ts for send_whatsapp implementation
import os
tools_files = []
for f in os.listdir('/Users/vbalaraman/OpenSpider/src'):
    if 'tool' in f.lower():
        tools_files.append(f)
print(f'\n=== Tool files: {tools_files} ===')

# Check for the send_whatsapp tool handler
for tf in tools_files:
    fp = os.path.join('/Users/vbalaraman/OpenSpider/src', tf)
    with open(fp, 'r') as fh:
        tlines = fh.readlines()
    for i, line in enumerate(tlines):
        if 'send_whatsapp' in line.lower() or 'whatsapp' in line.lower():
            # Print surrounding context
            start = max(0, i-1)
            end = min(len(tlines), i+2)
            for j in range(start, end):
                print(f'{tf}:{j+1}: {tlines[j].rstrip()[:200]}')
            print('---')
