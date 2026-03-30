import os

base = '/Users/vbalaraman/OpenSpider/workspace/pitwall-ai'

# Fix main.tsx to add basename='/f1'
main_tsx_path = os.path.join(base, 'frontend', 'src', 'main.tsx')
with open(main_tsx_path) as f:
    content = f.read()

print('Current main.tsx:')
print(content)
print('---')

# Check if it uses BrowserRouter
if 'BrowserRouter' in content:
    if 'basename' not in content:
        # Add basename to BrowserRouter
        content = content.replace('<BrowserRouter>', '<BrowserRouter basename="/f1">')
        with open(main_tsx_path, 'w') as f:
            f.write(content)
        print('[FIXED] Added basename="/f1" to BrowserRouter')
    elif '/f1' not in content:
        # basename exists but wrong value
        import re
        content = re.sub(r'basename="[^"]*"', 'basename="/f1"', content)
        with open(main_tsx_path, 'w') as f:
            f.write(content)
        print('[FIXED] Updated basename to /f1')
    else:
        print('[OK] basename=/f1 already present')
else:
    print('[WARN] No BrowserRouter found in main.tsx')

# Verify
with open(main_tsx_path) as f:
    final = f.read()
print('\nFinal main.tsx:')
print(final)
