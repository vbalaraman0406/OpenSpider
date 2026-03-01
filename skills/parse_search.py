import re

with open('search_results.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Remove script and style tags
clean = re.sub(r'<script[^>]*>.*?</script>', ' ', html, flags=re.DOTALL|re.IGNORECASE)
clean = re.sub(r'<style[^>]*>.*?</style>', ' ', clean, flags=re.DOTALL|re.IGNORECASE)

# Extract all href URLs
urls = re.findall(r'href="(/url\?q=([^&"]+))', clean)
print("=== Extracted URLs ===")
for full, url in urls[:30]:
    decoded = url.replace('%3A', ':').replace('%2F', '/').replace('%3F', '?').replace('%3D', '=').replace('%26', '&')
    if 'google' not in decoded and 'youtube' not in decoded and 'accounts' not in decoded:
        print(decoded)

# Extract all visible text and look for Let's Remodel
text = re.sub(r'<[^>]+>', ' ', clean)
text = re.sub(r'\s+', ' ', text)

# Find chunks mentioning remodel
chunks = text.split('.')
for chunk in chunks:
    if re.search(r"let.{0,3}s.{0,3}remodel", chunk, re.IGNORECASE):
        print("\nREMODEL MENTION:", chunk.strip()[:300])

# Also look for any business listing patterns
for chunk in chunks:
    if re.search(r'(bathroom|kitchen|contractor|remodel)', chunk, re.IGNORECASE) and len(chunk.strip()) > 30:
        print("\nRELEVANT:", chunk.strip()[:300])
