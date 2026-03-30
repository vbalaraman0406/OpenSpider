import os

base = '/Users/vbalaraman/OpenSpider/workspace/pitwall-ai'

# Read just race.py router
path = os.path.join(base, 'backend/routers/race.py')
with open(path) as fh:
    print(fh.read())
