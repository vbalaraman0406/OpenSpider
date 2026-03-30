import os, time

base = '/Users/vbalaraman/OpenSpider/workspace/pitwall-ai'

# Write deploy marker to force GCP hash change
marker = os.path.join(base, 'DEPLOY_MARKER.txt')
with open(marker, 'w') as f:
    f.write(f'DEPLOY_TIMESTAMP={time.time()}\nFIX=route_ordering_health_api\n')
print(f'Marker written: {marker}')

# Verify main.py
with open(os.path.join(base, 'backend', 'main.py'), 'r') as f:
    content = f.read()
print(f'main.py size: {len(content)} bytes')
print('Health before catch-all:', content.index('health') < content.index('path:path'))
