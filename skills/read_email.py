with open('/tmp/email_body.html','r') as f:
    content = f.read()
print(len(content))
print(content[:200])