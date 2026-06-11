import re

with open(r'C:\Users\yeshw\Documents\GitHub\PawKart\Store-Owner-Panel\JS\dashboard.js', 'r', encoding='utf-8') as f:
    content = f.read()

# Fix renderProducts
def replace_render_products(match):
    code = match.group(0)
    # Fix mapping
    code = code.replace('const matchesSearch = p.name.toLowerCase().includes(query)', 
                        'const pName = (p.product_name || p.name || "").toLowerCase();\n    const matchesSearch = pName.includes(query)')
    # Fix sorting
    code = code.replace('a.price - b.price', 'parseFloat(a.price) - parseFloat(b.price)')
    code = code.replace('b.price - a.price', 'parseFloat(b.price) - parseFloat(a.price)')
    # Add rating sort logic
    code = code.replace('} else {', '} else if (sortBy === "rating-high") {\n    filtered.sort((a, b) => parseFloat(b.rating || 0) - parseFloat(a.rating || 0));\n  } else {')
    # Fix the DOM bloat loop
    code = code.replace('container.innerHTML += `', 'htmlString += `')
    code = code.replace('filtered.forEach(p => {', 'let htmlString = "";\n  filtered.slice(0, 50).forEach(p => { // Limit to top 50 to avoid crash')
    code = code.replace('</div>\n    </div>\n  `;\n  });', '</div>\n    </div>\n  `;\n  });\n  container.innerHTML = htmlString;')
    # Fix template variables
    code = code.replace('${p.name}', '${p.product_name || p.name}')
    return code

render_prod_regex = re.compile(r'function renderProducts\(\) \{.*?container\.innerHTML \+= `.*?</div>\n    </div>\n  `;\n  \}\);\n\}', re.DOTALL)
new_content = render_prod_regex.sub(replace_render_products, content)

# Fix renderInventory
def replace_render_inventory(match):
    code = match.group(0)
    code = code.replace('const matchesSearch = p.name.toLowerCase().includes(query)', 
                        'const pName = (p.product_name || p.name || "").toLowerCase();\n    const matchesSearch = pName.includes(query)')
    code = code.replace('container.innerHTML += `', 'htmlString += `')
    code = code.replace('filtered.forEach(p => {', 'let htmlString = "";\n  filtered.slice(0, 50).forEach(p => {')
    code = code.replace('</td>\n    </tr>\n  `;\n  });', '</td>\n    </tr>\n  `;\n  });\n  container.innerHTML = htmlString;')
    code = code.replace('${p.name}', '${p.product_name || p.name}')
    return code

render_inv_regex = re.compile(r'function renderInventory\(\) \{.*?container\.innerHTML \+= `.*?</td>\n    </tr>\n  `;\n  \}\);\n\}', re.DOTALL)
new_content = render_inv_regex.sub(replace_render_inventory, new_content)

# Write back
with open(r'C:\Users\yeshw\Documents\GitHub\PawKart\Store-Owner-Panel\JS\dashboard.js', 'w', encoding='utf-8') as f:
    f.write(new_content)
print('Updated dashboard.js')
