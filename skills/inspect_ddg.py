with open('/tmp/tn_ddg.html', 'r', errors='ignore') as f:
    html = f.read()

# Print first 3000 chars to understand structure
print(html[:3000])
