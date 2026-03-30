with open('/tmp/premarket_email.html') as f:
    content = f.read()
# Save to a temp file as a Python string literal
with open('/tmp/email_body.txt', 'w') as f:
    f.write(content)
print(f'File size: {len(content)} chars')
print('First 100:', content[:100])
print('Last 100:', content[-100:])