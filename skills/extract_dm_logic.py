import re

with open('/Users/vbalaraman/OpenSpider/src/whatsapp.ts', 'r') as f:
    content = f.read()

lines = content.split('\n')

# Find all lines referencing allowedDMs, dmPolicy, botMode, isGroup, mention, shouldProcess, shouldRespond
keywords = ['allowedDMs', 'dmPolicy', 'botMode', 'isGroup', 'shouldProcess', 'shouldRespond', 'mention', 'allowlist', 'sender', 'remoteJid', 'fromMe']

print('=== KEY LINES ===')
for i, line in enumerate(lines, 1):
    if any(kw in line for kw in keywords):
        # Print context: 2 lines before and after
        start = max(0, i-3)
        end = min(len(lines), i+2)
        for j in range(start, end):
            marker = '>>>' if j == i-1 else '   '
            print(f'{marker} {j+1}: {lines[j]}')
        print('---')

# Also find the function that handles incoming messages
print('\n=== FUNCTION DEFINITIONS ===')
for i, line in enumerate(lines, 1):
    if 'function ' in line or 'async ' in line and ('=>' in line or '{' in line):
        stripped = line.strip()
        if any(kw in stripped.lower() for kw in ['message', 'handle', 'process', 'incoming', 'upsert']):
            print(f'{i}: {stripped[:150]}')
