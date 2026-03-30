import json

try:
    with open('package.json', 'r') as f:
        pkg = json.load(f)
    print('name:', pkg.get('name'))
    print('main:', pkg.get('main'))
    print('scripts:', json.dumps(pkg.get('scripts', {}), indent=2))
    deps = pkg.get('dependencies', {})
    for k in deps:
        if 'whatsapp' in k.lower() or 'baileys' in k.lower() or 'wa' in k.lower():
            print(f'WA dep: {k} = {deps[k]}')
except Exception as e:
    print(f'Error: {e}')
