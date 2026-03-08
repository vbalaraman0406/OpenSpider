with open('/Users/vbalaraman/OpenSpider/src/whatsapp.ts', 'r') as f:
    lines = f.readlines()

# Print lines 390-520 (the DM validation section)
for i in range(389, min(520, len(lines))):
    print(f'{i+1}: {lines[i]}', end='')
