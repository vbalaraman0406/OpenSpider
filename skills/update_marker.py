import time, os
ts = int(time.time())
path = '/Users/vbalaraman/OpenSpider/workspace/pitwall-ai/DEPLOY_MARKER.txt'
with open(path, 'w') as f:
    f.write('FORCE_UPLOAD_' + str(ts) + '\n')
print('DEPLOY_MARKER.txt updated with timestamp ' + str(ts))
