with open('google_raw.html', 'r') as f:
    html = f.read()

# Print first 2000 chars to see what we got
print('=== FIRST 2000 CHARS ===')
print(html[:2000])
print('\n=== LAST 500 CHARS ===')
print(html[-500:])
