import re
with open(r'C:\Users\yeshw\Documents\GitHub\PawKart\Store-Owner-Panel\HTML\index.html', 'r', encoding='utf-8') as f:
    content = f.read()

new_content = re.sub(
    r'<div class=\"cart-items-box\" id=\"cart-items-container\">.*?<div class=\"summary-card\">',
    '<div class=\"cart-items-box\" id=\"cart-items-container\">\n      <h2>Your Cart</h2>\n      <!-- Cart items will be dynamically injected here -->\n    </div>\n\n    <div class=\"summary-card\">',
    content,
    flags=re.DOTALL
)

with open(r'C:\Users\yeshw\Documents\GitHub\PawKart\Store-Owner-Panel\HTML\index.html', 'w', encoding='utf-8') as f:
    f.write(new_content)
