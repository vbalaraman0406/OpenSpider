import os

js_path = '/Users/vbalaraman/OpenSpider/workspace/pitwall-ai/frontend/dist/assets/index-DSBP2uHW.js'
with open(js_path) as f:
    content = f.read()

# Check for fetch/axios calls
print('Contains fetch:', 'fetch(' in content)
print('Contains axios:', 'axios' in content)
print('Contains /f1/api:', '/f1/api' in content)
print('Contains baseURL:', 'baseURL' in content)

# Find the App component rendering
# Search for createElement or jsx calls near 'Pitwall'
idx = content.find('Pitwall')
if idx >= 0:
    print('\nContext around Pitwall (500 chars before and after):')
    print(content[max(0,idx-500):idx+500])

# Check for error handling
print('\nContains try:', content.count('try{'))
print('Contains catch:', content.count('catch'))
print('Contains console.error:', 'console.error' in content)

# Check for any dynamic imports that might fail
print('Contains import(:', 'import(' in content)
print('Contains vendor:', 'vendor' in content)

# Check the React rendering at the end
print('\nLast 500 chars:')
print(content[-500:])
