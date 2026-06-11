import re
import os

filepath = r'C:\Users\yeshw\Documents\GitHub\PawKart\Store-Owner-Panel\JS\script.js'

with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

replacement = """let currentCategory = null;
let currentCategoryPage = 1;
const categoryItemsPerPage = 12;

function openCategory(categoryKey) {
  const config = categoryConfigs[categoryKey];
  if (!config) return;
  
  currentCategory = categoryKey;
  currentCategoryPage = 1;
  const searchInput = document.getElementById('categorySearchBar');
  if (searchInput) searchInput.value = '';
  
  document.getElementById('co-category-title').textContent = `${config.emoji} ${config.title}`;
  document.getElementById('co-category-desc').textContent = config.desc;
  
  const hero = document.getElementById('co-category-hero');
  hero.className = 'category-hero'; // Reset
  hero.classList.add(config.themeClass);
  
  renderCategoryProducts();
  nav('category');
}

function handleCategorySearch() {
  currentCategoryPage = 1;
  renderCategoryProducts();
}

function changeCategoryPage(delta) {
  currentCategoryPage += delta;
  renderCategoryProducts();
  document.getElementById('category-page').scrollIntoView({ behavior: 'smooth' });
}

function renderCategoryProducts() {
  const grid = document.getElementById('category-products-grid');
  const paginationControls = document.getElementById('categoryPagination');
  const searchInput = document.getElementById('categorySearchBar');
  const query = searchInput ? searchInput.value.toLowerCase() : '';
  
  grid.innerHTML = '';
  if (paginationControls) paginationControls.innerHTML = '';
  
  if (Object.keys(productData).length === 0) {
    grid.innerHTML = `<div style="text-align:center; padding: 40px; grid-column: 1/-1;">
      <h3 style="color:var(--text-color);">Server Offline</h3>
      <p style="color:var(--text-muted);">Please start your backend server to view products.</p>
    </div>`;
    return;
  }
  
  let filteredProducts = [];
  for (const [id, prod] of Object.entries(productData)) {
    if (prod.category === currentCategory) {
      if (!query || prod.name.toLowerCase().includes(query) || prod.description.toLowerCase().includes(query)) {
        filteredProducts.push({ id, ...prod });
      }
    }
  }
  
  if (filteredProducts.length === 0) {
    grid.innerHTML = `
      <div style="grid-column: 1 / -1; text-align: center; padding: 40px; color: var(--slate); font-weight: 500;">
        <p>No products found matching your search right now. Check back soon!</p>
      </div>
    `;
    return;
  }
  
  const totalPages = Math.ceil(filteredProducts.length / categoryItemsPerPage);
  if (currentCategoryPage > totalPages) currentCategoryPage = totalPages;
  if (currentCategoryPage < 1) currentCategoryPage = 1;
  
  const startIndex = (currentCategoryPage - 1) * categoryItemsPerPage;
  const endIndex = Math.min(startIndex + categoryItemsPerPage, filteredProducts.length);
  const pageProducts = filteredProducts.slice(startIndex, endIndex);
  
  let htmlString = '';
  pageProducts.forEach(prod => {
    const stars = '★ '.repeat(Math.round(prod.rating)) + '☆ '.repeat(5 - Math.round(prod.rating));
    let badgeHtml = '';
    if (prod.badge) {
      let badgeClass = 'badge-organic';
      if (prod.badge.toLowerCase().includes('best')) badgeClass = 'badge-bestseller';
      if (prod.badge.toLowerCase().includes('new')) badgeClass = 'badge-new';
      badgeHtml = `<span class="prod-badge ${badgeClass}">${prod.badge}</span>`;
    }
    
    htmlString += `
      <div class="product-card" onclick="openProductDetail('${prod.id}')">
        <div class="prod-image-wrapper">
          <img src="${prod.image}" alt="${prod.name}">
          ${badgeHtml}
        </div>
        <div class="prod-info-wrapper">
          <div class="prod-rating">${stars} <span>(${prod.rating})</span></div>
          <h3>${prod.name}</h3>
          <p class="prod-desc">${prod.description.length > 70 ? prod.description.substring(0, 67) + '...' : prod.description}</p>
          <div class="prod-footer">
            <span class="price">₹${prod.price}</span>
            <button class="add-btn-round" onclick="event.stopPropagation(); addToCart('${prod.id}', 1); showToast('${prod.name} added to cart!')" title="Add to Cart">
              <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                <line x1="12" y1="5" x2="12" y2="19"></line>
                <line x1="5" y1="12" x2="19" y2="12"></line>
              </svg>
            </button>
          </div>
        </div>
      </div>
    `;
  });
  grid.innerHTML = htmlString;
  
  // Render Pagination
  if (totalPages > 1 && paginationControls) {
    paginationControls.innerHTML = `
      <button class="btn btn-outline" onclick="changeCategoryPage(-1)" ${currentCategoryPage === 1 ? 'disabled' : ''} style="padding: 8px 16px;">Previous</button>
      <span style="color: var(--text-color); font-weight: 500;">Page ${currentCategoryPage} of ${totalPages}</span>
      <button class="btn btn-primary" onclick="changeCategoryPage(1)" ${currentCategoryPage === totalPages ? 'disabled' : ''} style="padding: 8px 16px;">Next</button>
    `;
  }
}
"""

pattern = re.compile(r'function openCategory\(categoryKey\).*?nav\(\'category\'\);\n\}', re.DOTALL)
new_content = pattern.sub(replacement, content)

if new_content != content:
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(new_content)
    print('Updated script.js successfully.')
else:
    print('Regex failed to match.')
