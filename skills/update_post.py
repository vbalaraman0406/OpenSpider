import os
new_post = "Wow! Congratulations to Nissan, and Christian Meunier, Americas Chairman, on the tremendous success they are having in the U.S. They have moved most of their production to our great Country, largely because of Tariffs, and the results are AMAZING!!!"
file_path = '/Users/vbalaraman/OpenSpider/workspace/trump_last_seen.txt'
try:
    with open(file_path, 'w') as f:
        f.write(new_post)
    print('File written successfully to:', file_path)
except Exception as e:
    print(f'Error: {e}')
    raise