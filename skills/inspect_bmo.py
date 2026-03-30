# Check what's actually in the downloaded files
for filepath, label in [('/tmp/bmo_usa.html', 'USA'), ('/tmp/bmo_can.html', 'Canada')]:
    with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
        text = f.read()
    print(f'=== {label} ({len(text)} bytes) ===')
    # Print first 1500 chars to see what we got
    print(text[:1500])
    print('...')
    print()
