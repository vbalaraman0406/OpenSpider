import os

# Read saved post
saved_path = 'workspace/trump_last_seen.txt'
saved = ''
if os.path.exists(saved_path):
    with open(saved_path, 'r') as f:
        saved = f.read().strip()

# New post from previous step
new = 'Tonight at 6:24 P.M. EST, for the first time in over 50 YEARS, America is going back to the Moon! Artemis II, among the most powerful rockets ever built, is launching our Brave Astronauts farther into Deep Space than any human has EVER gone. We are WINNING, in Space, on Earth, and everywhere in between — Economically, Militarily, and now, BEYOND THE STARS. N...[COMPACTED 12 chars]...mpete, we DOMINATE, and the whole World is watching. God bless our incredible Astronauts, God bless NASA, and God bless the Greatest Nation ever to exist, the United States of America! President DONALD J. TRUMP'

# Check if new post is empty or identical
if saved == new or not new:
    print('No update: posts identical or no new post found.')
else:
    # Overwrite file with new post
    with open(saved_path, 'w') as f:
        f.write(new)
    print('New post detected and file updated.')
    # Indicate that WhatsApp should be sent
    print('SEND_WHATSAPP')
