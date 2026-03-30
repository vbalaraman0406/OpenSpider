with open('/Users/vbalaraman/OpenSpider/src/whatsapp.ts', 'r') as f:
    lines = f.readlines()

# Read the full sendWhatsAppMessage function (lines 280-327)
print('=== sendWhatsAppMessage FULL (lines 280-327) ===')
for i in range(279, min(328, len(lines))):
    print(f'{i+1}: {lines[i].rstrip()}')

# Also check if there's any 'not-acceptable' handling anywhere in the file
print('\n=== All error handling patterns ===')
for i, line in enumerate(lines):
    l = line.lower()
    if 'not-acceptable' in l or 'notacceptable' in l or '408' in l or 'timed out' in l or 'statuscode' in l:
        print(f'{i+1}: {lines[i].rstrip()[:200]}')

# Check the connection.update handler for disconnect reasons
print('\n=== Connection update handler (around line 492) ===')
for i in range(485, min(540, len(lines))):
    print(f'{i+1}: {lines[i].rstrip()}')
