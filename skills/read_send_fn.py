with open('/Users/vbalaraman/OpenSpider/src/whatsapp.ts', 'r') as f:
    lines = f.readlines()

# Read lines 280-330 (sendWhatsAppMessage function)
for i in range(279, min(330, len(lines))):
    print(f'{i+1}: {lines[i].rstrip()}')
