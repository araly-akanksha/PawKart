import os

index_path = r'C:\Users\yeshw\Documents\GitHub\PawKart\Store-Owner-Panel\HTML\index.html'

with open(index_path, 'r', encoding='utf-8') as f:
    content = f.read()

replacement = """  <header class="shop-header">
    <button class="back-btn" onclick="goBack()" title="Go Back" style="background:none;border:none;cursor:pointer;margin-right:15px;color:var(--text-color);display:flex;align-items:center;">
      <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <line x1="19" y1="12" x2="5" y2="12"></line>
        <polyline points="12 19 5 12 12 5"></polyline>
      </svg>
    </button>"""

if 'class="back-btn"' not in content:
    new_content = content.replace('  <header class="shop-header">', replacement)
    with open(index_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    print("Injected into index.html")
else:
    print("Already injected into index.html")

dashboard_path = r'C:\Users\yeshw\Documents\GitHub\PawKart\Store-Owner-Panel\HTML\dashboard.html'
with open(dashboard_path, 'r', encoding='utf-8') as f:
    content = f.read()

if 'class="back-btn"' not in content:
    replacement = """    <header style="display:flex; align-items:center;">
      <button class="back-btn" onclick="goBack()" title="Go Back" style="background:none;border:none;cursor:pointer;margin-right:15px;color:var(--text-color);display:flex;align-items:center;">
        <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <line x1="19" y1="12" x2="5" y2="12"></line>
          <polyline points="12 19 5 12 12 5"></polyline>
        </svg>
      </button>"""
    new_content = content.replace('    <header>', replacement)
    with open(dashboard_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    print("Injected into dashboard.html")

admin_path = r'C:\Users\yeshw\Documents\GitHub\PawKart\Store-Owner-Panel\HTML\admin.html'
with open(admin_path, 'r', encoding='utf-8') as f:
    content = f.read()

if 'class="back-btn"' not in content:
    replacement = """      <div class="page-header" style="display:flex; align-items:center;">
        <button class="back-btn" onclick="goBack()" title="Go Back" style="background:none;border:none;cursor:pointer;margin-right:15px;color:var(--text-color);display:flex;align-items:center;">
          <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <line x1="19" y1="12" x2="5" y2="12"></line>
            <polyline points="12 19 5 12 12 5"></polyline>
          </svg>
        </button>"""
    new_content = content.replace('      <div class="page-header">', replacement)
    with open(admin_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    print("Injected into admin.html")
