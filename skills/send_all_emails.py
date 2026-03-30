# Read the HTML email and print it as a single-line JSON string
import json
with open('/tmp/premarket_email.html') as f:
    html = f.read()

# Output as JSON so we can use it
print(json.dumps({'body': html, 'length': len(html)}))
