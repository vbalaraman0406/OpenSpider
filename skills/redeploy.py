import os
import time

base = '/Users/vbalaraman/OpenSpider/workspace/pitwall-ai'

marker = 'FORCE_UPLOAD_' + str(time.time()) + '_v3_FINAL\n'
with open(os.path.join(base, 'DEPLOY_MARKER.txt'), 'w') as f:
    f.write(marker)
print('Wrote DEPLOY_MARKER.txt: ' + marker.strip())
