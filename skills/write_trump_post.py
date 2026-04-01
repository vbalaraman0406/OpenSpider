import sys
new_text = "Netanyahu to Newsmax: Trump Has Shown 'Tremendous Leadership': https://www.newsmax.com/newsmax-tv/benjamin-netanyahu-israel-donald-trump/2026/03/30/id/1251249/"
try:
    with open('workspace/trump_last_seen.txt', 'w') as f:
        f.write(new_text)
    print('File written successfully.')
except Exception as e:
    print(f'Error writing file: {e}', file=sys.stderr)
    sys.exit(1)