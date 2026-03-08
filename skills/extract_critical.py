with open('/Users/vbalaraman/OpenSpider/src/whatsapp.ts', 'r') as f:
    lines = f.readlines()

# Print lines 400-520 in two chunks to avoid truncation
print('=== LINES 400-460 ===')
for i in range(399, min(460, len(lines))):
    print(f'{i+1}: {lines[i]}', end='')
