with open('/tmp/premarket_email.html') as f:
    html = f.read()
# Output the full HTML
import sys
sys.stdout.write(html)