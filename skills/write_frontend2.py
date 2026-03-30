import os

base = '/Users/vbalaraman/OpenSpider/workspace/pitwall-ai/frontend'

app_tsx = 'function App() {\n  return (\n    <div style={{backgroundColor:"#0a0a0f",color:"#ffffff",minHeight:"100vh",display:"flex",flexDirection:"column",alignItems:"center",justifyContent:"center",fontFamily:"system-ui,sans-serif"}}>\n      <h1 style={{fontSize:"3rem",marginBottom:"0.5rem"}}>Pitwall.ai</h1>\n      <p style={{color:"#e10600",fontSize:"1.5rem"}}>F1 Analytics Dashboard</p>\n      <p style={{color:"#888",marginTop:"2rem"}}>Coming Soon</p>\n      <p style={{color:"#444",marginTop:"1rem",fontSize:"0.8rem"}}>v2.0</p>\n    </div>\n  )\n}\nexport default App\n'

main_tsx = 'import React from "react"\nimport ReactDOM from "react-dom/client"\nimport App from "./App"\nReactDOM.createRoot(document.getElementById("root")!).render(<React.StrictMode><App /></React.StrictMode>)\n'

index_html = '<!DOCTYPE html>\n<html lang="en">\n<head><meta charset="UTF-8"/><meta name="viewport" content="width=device-width,initial-scale=1.0"/><title>Pitwall.ai - F1 Analytics</title></head>\n<body><div id="root"></div><script type="module" src="/src/main.tsx"></script></body>\n</html>\n'

with open(os.path.join(base, 'src', 'App.tsx'), 'w') as f:
    f.write(app_tsx)
print('Wrote App.tsx')

with open(os.path.join(base, 'src', 'main.tsx'), 'w') as f:
    f.write(main_tsx)
print('Wrote main.tsx')

with open(os.path.join(base, 'index.html'), 'w') as f:
    f.write(index_html)
print('Wrote index.html')

dist_assets = os.path.join(base, 'dist', 'assets')
if os.path.exists(dist_assets):
    for fname in os.listdir(dist_assets):
        fpath = os.path.join(dist_assets, fname)
        if os.path.isfile(fpath):
            os.remove(fpath)
            print('Deleted ' + fpath)

dist_index = os.path.join(base, 'dist', 'index.html')
if os.path.exists(dist_index):
    os.remove(dist_index)
    print('Deleted ' + dist_index)

print('Done')
