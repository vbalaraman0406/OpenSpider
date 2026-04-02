import os
new_text = "Tonight at 6:24 P.M. EST, for the first time in over 50 YEARS, America is going back to the Moon! Artemis II, among the most powerful rockets ever built, is launching our Brave Astronauts farther into Deep Space than any human has EVER gone. We are WINNING, in Space, on Earth, and everywhere in between — Economically, Militarily, and now, BEYOND THE STARS. N...[COMPACTED 12 chars]...mpete, we DOMINATE, and the whole World is watching. God bless our incredible Astronauts, God bless NASA, and God bless the Greatest Nation ever to exist, the United States of America! President DONALD J. TRUMP"
try:
    os.makedirs('workspace', exist_ok=True)
    file_path = os.path.join('workspace', 'trump_last_seen.txt')
    with open(file_path, 'w') as f:
        f.write(new_text)
    print('File created and updated successfully.')
except Exception as e:
    print(f'Error: {e}')
    import sys
    sys.exit(1)