import os, subprocess

# List all files
files = os.listdir('.')
print('All files:')
for f in sorted(files):
    print(f'  {f}')

print('\n--- read_whatsapp.py (first 40 lines) ---')
try:
    with open('read_whatsapp.py', 'r') as fh:
        lines = fh.readlines()[:40]
        for l in lines:
            print(l.rstrip())
except:
    print('not found')

print('\n--- send_whatsapp.py (full) ---')
try:
    with open('send_whatsapp.py', 'r') as fh:
        print(fh.read())
except:
    print('not found')
