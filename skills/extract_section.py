with open('/Users/vbalaraman/OpenSpider/src/whatsapp.ts', 'r') as f:
    lines = f.readlines()

# Print lines 325-520 (the DM validation and message processing logic)
for i in range(324, min(520, len(lines))):
    print(f'{i+1}: {lines[i]}', end='')
