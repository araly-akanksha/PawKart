"""Quick smoke test for both servers"""
import urllib.request
import json

# Test backend
r = urllib.request.urlopen("http://127.0.0.1:8000/healthz")
print("Backend:", json.loads(r.read()))

# Test frontend serves HTML
r = urllib.request.urlopen("http://127.0.0.1:5173/")
html = r.read().decode()
print("Frontend HTML length:", len(html))
print("Has root div:", 'id="root"' in html)
print("Has main.jsx:", "main.jsx" in html)
print("Title correct:", "PawKart Dashboard" in html)
