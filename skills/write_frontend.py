import os

base = '/Users/vbalaraman/OpenSpider/workspace/pitwall-ai/frontend'

# App.tsx
app_tsx = '''function App() {
  return (
    <div style={{backgroundColor:"#0a0a0f",color:"#ffffff",minHeight:"100vh",display:"flex",flexDirection:"column",alignItems:"center",justifyContent:"center",fontFamily:"system-ui,sans-serif"}}>
      <h1 style={{fontSize:"3rem",marginBottom:"0.5rem"}}>\u{1F3CE}\uFE0F Pitwall.ai</h1>
      <p style={{color:"#e10600",fontSize:"1.5rem"}}>F1 Analytics Dashboard</p>
      <p style={{color:"#888",marginTop:"2rem"}}>Coming Soon \u2014 Under Construction</p>
      <p style={{color:"#444",marginTop:"1rem",fontSize:"0.8rem"}}>v2.0</p>
    </div>
  )
}
export default App
'''

main_tsx = '''import React from "react"
import ReactDOM from "react-dom/client"
import App from "./App"
ReactDOM.createRoot(document.getElementById("root")!).render(<React.StrictMode><App /></React.StrictMode>)
'''

index_html = '''<!DOCTYPE html>
<html lang="en">
<head><meta charset="UTF-8"/><meta name="viewport" content="width=device-width,initial-scale=1.0"/><title>Pitwall.ai - F1 Analytics</title></head>
<body><div id="root"></div><script type="module" src="/src/main.tsx"></script></body>
</html>
'''

with open(os.path.join(base, 'src', 'App.tsx'), 'w') as f:
    f.write(app_tsx)
print('Wrote App.tsx')

with open(os.path.join(base, 'src', 'main.tsx'), 'w') as f:
    f.write(main_tsx)
print('Wrote main.tsx')

with open(os.path.join(base, 'index.html'), 'w') as f:
    f.write(index_html)
print('Wrote index.html')

# Clean dist/assets
dist_assets = os.path.join(base, 'dist', 'assets')
if os.path.exists(dist_assets):
    for fname in os.listdir(dist_assets):
        fpath = os.path.join(dist_assets, fname)
        if os.path.isfile(fpath):
            os.remove(fpath)
            print(f'Deleted {fpath}')

# Clean dist/index.html
dist_index = os.path.join(base, 'dist', 'index.html')
if os.path.exists(dist_index):
    os.remove(dist_index)
    print(f'Deleted {dist_index}')

print('Done writing frontend files and cleaning dist')
