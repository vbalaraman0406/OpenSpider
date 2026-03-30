import os

base = '/Users/vbalaraman/OpenSpider/workspace/pitwall-ai'

path = os.path.join(base, 'backend/routers/drivers.py')
with open(path) as fh:
    print(fh.read())
