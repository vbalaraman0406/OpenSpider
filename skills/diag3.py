import os

# Read server.log and search specifically for the Family group JID and error patterns
with open('/Users/vbalaraman/OpenSpider/server.log', 'r') as f:
    lines = f.readlines()

family_jid = '14156249639-1373117853'

print(f'=== Total log lines: {len(lines)} ===')

# Find all lines mentioning the family group JID
print('\n=== Lines mentioning Family group JID ===')
for i, line in enumerate(lines):
    if family_jid in line:
        print(f'L{i+1}: {line.rstrip()[:250]}')

# Find all lines with 'not-acceptable' or 'No sessions'
print('\n=== Lines with not-acceptable ===')
for i, line in enumerate(lines):
    if 'not-acceptable' in line.lower():
        print(f'L{i+1}: {line.rstrip()[:250]}')

print('\n=== Lines with No sessions ===')
for i, line in enumerate(lines):
    if 'no sessions' in line.lower() or 'No sessions' in line:
        print(f'L{i+1}: {line.rstrip()[:250]}')

# Also check last 50 lines of log
print('\n=== Last 30 lines of server.log ===')
for line in lines[-30:]:
    print(line.rstrip()[:200])
