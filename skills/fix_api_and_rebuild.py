import os

# Fix api.ts to use /api instead of /f1/api
api_ts_path = '/Users/vbalaraman/OpenSpider/workspace/pitwall-ai/frontend/src/api.ts'
with open(api_ts_path, 'r') as f:
    content = f.read()

print('=== BEFORE api.ts ===')
print(content[:500])

# Replace /f1/api with /api
content = content.replace("'/f1/api'", "'/api'")
content = content.replace('"/f1/api"', '"/api"')
content = content.replace('`/f1/api', '`/api')

with open(api_ts_path, 'w') as f:
    f.write(content)

print('=== AFTER api.ts ===')
with open(api_ts_path, 'r') as f:
    print(f.read()[:500])

print('\n=== api.ts fix applied ===')
