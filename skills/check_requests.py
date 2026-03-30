try:
    import requests
    print('requests available')
except ImportError:
    print('requests not available')
    try:
        import pip
        print('pip available')
    except:
        print('pip not available')

import sys
print(f'Python: {sys.version}')
print(f'Modules: {list(sys.modules.keys())[:20]}')
