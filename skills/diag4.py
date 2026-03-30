# Read the sendWhatsAppMessage function from whatsapp.ts
with open('/Users/vbalaraman/OpenSpider/src/whatsapp.ts', 'r') as f:
    lines = f.readlines()

# Print lines 270-380 (sendWhatsAppMessage function area)
print('=== sendWhatsAppMessage function ===')
for i in range(269, min(380, len(lines))):
    print(f'{i+1}: {lines[i].rstrip()}')
