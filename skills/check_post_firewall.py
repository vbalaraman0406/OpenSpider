with open('/Users/vbalaraman/OpenSpider/src/whatsapp.ts', 'r') as f:
    lines = f.readlines()

# Show lines 540-620 (post-firewall processing)
for i in range(539, min(620, len(lines))):
    print(f'{i+1}: {lines[i]}', end='')
