
with open(r'C:\Users\yeshw\Documents\GitHub\PawKart\Store-Owner-Panel\JS\script.js', 'r', encoding='utf-8') as f:
    code = f.read()

wishlist_logic = '''
// ----------------------------------------------------
// WISHLIST LOGIC
// ----------------------------------------------------
let wishlist = JSON.parse(localStorage.getItem('pawkart_wishlist') || '[]');

function toggleWishlist(productId) {
  if (wishlist.includes(productId)) {
    wishlist = wishlist.filter(id => id !== productId);
    showToast('Removed from Wishlist');
  } else {
    wishlist.push(productId);
    showToast('Added to Wishlist');
  }
  localStorage.setItem('pawkart_wishlist', JSON.stringify(wishlist));
  updateWishlistIcon(productId);
}

function updateWishlistIcon(productId) {
  const icon = document.getElementById('pd-wishlist-icon');
  if (!icon) return;
  if (wishlist.includes(productId)) {
    icon.setAttribute('fill', '#ec4899');
    icon.style.color = '#ec4899';
  } else {
    icon.setAttribute('fill', 'none');
    icon.style.color = 'currentColor';
  }
}
'''

new_code = code.replace('let currentDetailProductId = \'\';', wishlist_logic + '\nlet currentDetailProductId = \'\';')

open(r'C:\Users\yeshw\Documents\GitHub\PawKart\Store-Owner-Panel\JS\script.js', 'w', encoding='utf-8').write(new_code)

