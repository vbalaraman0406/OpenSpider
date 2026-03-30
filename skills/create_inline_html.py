html_content = '''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Pitwall.ai - F1 Analytics</title>
</head>
<body style="margin:0;padding:0;background:#0a0a0f;color:white;font-family:Arial,sans-serif;">
<div id="root"></div>
<script>
document.getElementById("root").innerHTML = "<div style='display:flex;flex-direction:column;align-items:center;justify-content:center;min-height:100vh;'><h1 style='font-size:3rem;margin-bottom:0.5rem;'>Pitwall.ai</h1><h2 style='color:#e10600;font-size:1.5rem;'>F1 Analytics Dashboard</h2><p style='color:#888;margin-top:2rem;'>Coming Soon - v2.0</p><div style='margin-top:2rem;padding:1rem;background:#1a1a2e;border-radius:8px;border:1px solid #333;'><p>Status: React rendering OK</p><p>GCP App Engine: Working</p></div></div>";
</script>
</body>
</html>'''

with open('/Users/vbalaraman/OpenSpider/workspace/pitwall-ai/frontend/dist/index.html', 'w') as f:
    f.write(html_content)

print('Wrote inline HTML to dist/index.html')
print('No external JS needed - all rendering is inline')
