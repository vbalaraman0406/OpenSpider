import sys
sys.path.insert(0, 'workspace/pitwall-ai/backend')

try:
    from main import app
    print('Backend app imported successfully!')
    print(f'Routes: {[r.path for r in app.routes]}')
except Exception as e:
    print(f'Import failed: {e}')
    import traceback
    traceback.print_exc()
