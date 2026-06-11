import re

def patch_js_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
        
    pagination_code = '''
function setupPagination(totalItems, itemsPerPage, currentPage, containerId, pageChangeCallbackName) {
  const container = document.getElementById(containerId);
  if (!container) return;
  const existingNav = container.nextElementSibling;
  if (existingNav && existingNav.classList.contains('pagination-wrapper')) {
    existingNav.remove();
  }
  const totalPages = Math.ceil(totalItems / itemsPerPage);
  if (totalPages <= 1) return;
  let html = '<div class="pagination-wrapper" style="display: flex; justify-content: center; gap: 8px; margin-top: 24px; width: 100%; grid-column: 1/-1;">';
  html += `<button class="secondary-btn" style="padding: 6px 12px; font-size: 0.85rem;" onclick="${pageChangeCallbackName}(${currentPage - 1})" ${currentPage === 1 ? 'disabled' : ''}>Prev</button>`;
  for (let i = 1; i <= totalPages; i++) {
    if (i === 1 || i === totalPages || (i >= currentPage - 2 && i <= currentPage + 2)) {
      if (i === currentPage) {
        html += `<button class="primary-btn" style="padding: 6px 12px; font-size: 0.85rem;">${i}</button>`;
      } else {
        html += `<button class="secondary-btn" style="padding: 6px 12px; font-size: 0.85rem;" onclick="${pageChangeCallbackName}(${i})">${i}</button>`;
      }
    } else if (i === currentPage - 3 || i === currentPage + 3) {
      html += `<span style="padding: 6px 4px;">...</span>`;
    }
  }
  html += `<button class="secondary-btn" style="padding: 6px 12px; font-size: 0.85rem;" onclick="${pageChangeCallbackName}(${currentPage + 1})" ${currentPage === totalPages ? 'disabled' : ''}>Next</button>`;
  html += '</div>';
  container.insertAdjacentHTML('afterend', html);
}
'''
    if 'setupPagination' not in content:
        content = content + '\n' + pagination_code

    # Helper to patch a render function
    def patch_render(func_name, container_id, items_per_page=12):
        nonlocal content
        # Change signature to accept page
        pattern = r'function ' + func_name + r'\(\) \{'
        replacement = f'function {func_name}(page = 1) {{'
        content = re.sub(pattern, replacement, content, count=1)
        
        # Change slice(0, 50) to slice for pagination
        slice_pattern = r'filtered\.slice\(0,\s*50\)'
        slice_replacement = f'filtered.slice((page - 1) * {items_per_page}, page * {items_per_page})'
        content = re.sub(slice_pattern, slice_replacement, content)
        
        # Add pagination call before the end of the function
        end_pattern = r'(container\.innerHTML = htmlString;[\r\n\s]*)\}'
        end_replacement = r'\1  setupPagination(filtered.length, ' + str(items_per_page) + f', page, "{container_id}", "{func_name}");\n}}'
        content = re.sub(end_pattern, end_replacement, content)

    if 'admin.js' in filepath:
        # Fix owner_name bug
        bug_pattern = r's\.owner_name\.toLowerCase\(\)\.includes\(query\)'
        bug_replacement = r'(s.owner_name || "").toLowerCase().includes(query)'
        content = content.replace(bug_pattern, bug_replacement)

        patch_render('renderStores', 'storesContainer', 12)
        patch_render('renderWarehouses', 'warehousesContainer', 12)
        patch_render('renderProducts', 'productsContainer', 12)
        patch_render('renderOrders', 'ordersContainer', 15)
        patch_render('renderComplaints', 'complaintsContainer', 15)
        patch_render('renderUsers', 'usersContainer', 15)
    
    if 'dashboard.js' in filepath:
        patch_render('renderProducts', 'productsContainer', 12)
        patch_render('renderInventory', 'inventoryContainer', 12)
        patch_render('renderOrders', 'ordersContainer', 15)
        
        # renderReviews doesn't have slice(0, 50), it just has filtered.forEach
        review_slice_pattern = r'filtered\.forEach\(r => \{'
        review_slice_replacement = f'filtered.slice((page - 1) * 12, page * 12).forEach(r => {{'
        content = re.sub(r'function renderReviews\(\) \{', 'function renderReviews(page = 1) {', content)
        content = content.replace(review_slice_pattern, review_slice_replacement)
        
        rev_end_pattern = r'(  \}\);\n)\}'
        rev_end_replacement = r'\1  setupPagination(filtered.length, 12, page, "reviewsContainer", "renderReviews");\n}'
        content = re.sub(rev_end_pattern, rev_end_replacement, content, count=1)

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f'Patched {filepath}')

patch_js_file('C:/Users/yeshw/Documents/GitHub/PawKart/Store-Owner-Panel/JS/admin.js')
patch_js_file('C:/Users/yeshw/Documents/GitHub/PawKart/Store-Owner-Panel/JS/dashboard.js')
