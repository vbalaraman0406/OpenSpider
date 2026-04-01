import sys
post_text = "All of those countries that can’t get jet fuel because of the Strait of Hormuz, like the United Kingdom, which refused to get involved in the decapitation of Iran, I have a suggestion for you: Number 1, buy from the U.S., we have plenty, and Number 2, build up some delayed courage, go to the Strait, and just TAKE IT. You’ll have to start learning how to fight for yourself, the U.S.A. won’t be there to help you anymore, just like you weren’t there for us. Iran has been, essentially, decimated. The hard part is done. Go get your own oil! President DJT"
try:
    with open('workspace/trump_last_seen.txt', 'w') as f:
        f.write(post_text)
    print('File overwritten successfully.')
except Exception as e:
    print(f'Error: {e}')
    sys.exit(1)