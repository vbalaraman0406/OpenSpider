import os, time

base = '/Users/vbalaraman/OpenSpider/workspace/pitwall-ai'

# Add unique timestamp to main.py to bust GCP file dedup cache
main_path = os.path.join(base, 'backend', 'main.py')
with open(main_path, 'r') as f:
    content = f.read()

timestamp = str(time.time())
if 'CACHE_BUST' in content:
    lines = content.split('\n')
    lines = [l for l in lines if 'CACHE_BUST' not in l]
    content = '\n'.join(lines)

content = f'# CACHE_BUST={timestamp}\n' + content

with open(main_path, 'w') as f:
    f.write(content)
print(f'Cache bust added: {timestamp}')

# Also update DEPLOY_MARKER
marker = os.path.join(base, 'DEPLOY_MARKER.txt')
with open(marker, 'w') as f:
    f.write(f'TIMESTAMP={timestamp}\nVERSION=f1live3\nFIX=route_ordering\n')
print(f'Marker updated')
print(f'main.py size: {len(content)} bytes')
