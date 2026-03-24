import re

with open('/Users/vbalaraman/OpenSpider/src/whatsapp.ts', 'r') as f:
    lines = f.readlines()

patterns = ['sendMessage', 'group', 'not-acceptable', 'sessions', 'retry', 'sendToGroup', 'sendWhatsApp', 'GroupMetadata']
for i, line in enumerate(lines, 1):
    for p in patterns:
        if p.lower() in line.lower():
            print(f'{i}: {line.rstrip()[:120]}')
            break
