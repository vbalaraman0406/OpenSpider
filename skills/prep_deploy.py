import os
import time

base = '/Users/vbalaraman/OpenSpider/workspace/pitwall-ai'

marker = 'DEPLOY_MARKER_' + str(time.time()) + '_FORCE_UPLOAD\n'
with open(os.path.join(base, 'DEPLOY_MARKER.txt'), 'w') as f:
    f.write(marker)
print('Wrote DEPLOY_MARKER.txt: ' + marker.strip())

gcloudignore = '.git\n.gitignore\nnode_modules/\nfrontend/src/\nfrontend/node_modules/\n__pycache__/\n*.pyc\ncache/\n.env\n'
with open(os.path.join(base, '.gcloudignore'), 'w') as f:
    f.write(gcloudignore)
print('Wrote .gcloudignore')

print('Ready to deploy')
