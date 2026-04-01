import sys

new_post_text = "In the Ballroom case, the Judge said we have to get Congressional approval. He is WRONG! Congressional approval has never been given on anything, in these circumstances, big or small, having to do with construction at the White House. In this case, even less so, because the Ballroom is being built with Private Donations, no Federal Taxpayer Money! President DONALD J. TRUMP"

file_path = "workspace/trump_last_seen.txt"
try:
    with open(file_path, 'w') as f:
        f.write(new_post_text)
    print(f"File {file_path} updated successfully.")
except Exception as e:
    print(f"Error updating file: {e}", file=sys.stderr)
    sys.exit(1)