with open('/Users/vbalaraman/OpenSpider/src/whatsapp.ts', 'r') as f:
    lines = f.readlines()

# Print lines 380-410 (early message gates)
for i in range(379, min(410, len(lines))):
    print(f'{i+1}: {lines[i]}', end='')

print('\n\n=== Lines 460-500 (pre-firewall gates) ===')
for i in range(459, min(500, len(lines))):
    print(f'{i+1}: {lines[i]}', end='')
