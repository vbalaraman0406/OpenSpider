with open('/Users/vbalaraman/OpenSpider/src/whatsapp.ts', 'r') as f:
    lines = f.readlines()

for i in range(459, min(530, len(lines))):
    print(f'{i+1}: {lines[i]}', end='')
