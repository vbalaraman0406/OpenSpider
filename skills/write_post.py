import sys
new_post = "Wow! Congratulations to Nissan, and Christian Meunier, Americas Chairman, on the tremendous success they are having in the U.S. They have moved most of their production to our great Country, largely because of Tariffs, and the results are AMAZING!!!"
try:
    with open('workspace/trump_last_seen.txt', 'w') as f:
        f.write(new_post)
    print('File written successfully.')
except Exception as e:
    print(f'Error: {e}', file=sys.stderr)
    sys.exit(1)