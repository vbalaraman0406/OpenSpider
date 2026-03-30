import os

base = '/Users/vbalaraman/OpenSpider/workspace/pitwall-ai'

key_files = [
    'backend/main.py',
    'backend/test_regression.py',
    'backend/requirements.txt',
    'backend/routers/race.py',
    'backend/routers/drivers.py',
    'backend/routers/__init__.py',
    'backend/app/main.py',
    'backend/app/config.py',
    'backend/app/f1_data.py',
    'backend/app/__init__.py',
    'backend/app/routers/predictions.py',
    'backend/app/routers/drivers.py',
    'backend/app/routers/races.py',
    'backend/app/routers/__init__.py',
    'backend/app/routers/telemetry.py',
    'backend/app/services/data_processor.py',
    'backend/app/services/__init__.py',
    'backend/app/services/prediction_service.py',
    'backend/app/services/fastf1_service.py',
]

for relpath in key_files:
    path = os.path.join(base, relpath)
    if os.path.exists(path):
        with open(path) as fh:
            content = fh.read()
        print(f'\n===== {relpath} ({len(content)} bytes) =====')
        print(content)
    else:
        print(f'\n===== {relpath} NOT FOUND =====')
