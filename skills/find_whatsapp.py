import os

files = os.listdir('./')
for f in sorted(files):
    if 'whatsapp' in f.lower() or 'wa_' in f.lower() or 'wapi' in f.lower():
        print(f)

print('---')
# Check if there's a send mechanism
for f in sorted(files):
    if 'send' in f.lower():
        print(f)
