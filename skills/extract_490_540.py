with open('/Users/vbalaraman/OpenSpider/src/whatsapp.ts', 'r') as f:
    lines = f.readlines()

for i in range(489, min(540, len(lines))):
    print(f'{i+1}: {lines[i]}', end='')
