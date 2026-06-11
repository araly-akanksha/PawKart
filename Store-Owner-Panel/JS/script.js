function nav(page) {
  document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
  document.getElementById('page-' + page).classList.add('active');
  window.scrollTo({ top: 0, behavior: 'smooth' });
}

function selectRole(btn) {
  btn.closest('.role-selector').querySelectorAll('.role-btn')
    .forEach(b => b.classList.remove('active'));
  btn.classList.add('active');
  
  // Hide guest button for Admin and Store Manager
  const role = btn.textContent.trim();
  const guestBtn = document.getElementById('guest-login-btn');
  if (guestBtn) {
    if (role === 'Admin' || role === 'Store Manager') {
      guestBtn.style.display = 'none';
    } else {
      guestBtn.style.display = 'inline-block';
    }
  }
}

function doLogin() {
  const activeRoleBtn = document.querySelector('.role-btn.active');
  const role = activeRoleBtn ? activeRoleBtn.textContent.trim() : 'Customer';
  
  if (role === 'Store Manager') {
    window.location.href = 'dashboard.html?role=manager';
  } else if (role === 'Admin') {
    window.location.href = 'admin.html';
  } else {
    nav('home');
  }
}

function loginAsGuest() {
  const activeRoleBtn = document.querySelector('.role-btn.active');
  const role = activeRoleBtn ? activeRoleBtn.textContent.trim() : 'Customer';
  
  if (role === 'Store Manager') {
    alert('Store Manager guest access has been disabled. Please sign in with your credentials.');
  } else if (role === 'Admin') {
    alert('Admin guest access is not permitted. Please sign in with your credentials.');
  } else {
    nav('home');
  }
}

// Handle direct hash navigation and cart initialization on load
window.addEventListener("DOMContentLoaded", () => {
  if (window.location.hash === "#login") {
    nav("login");
  }
  fetchProductsAndRender();
  renderOrders();
  updateCartSummary();
});

async function fetchProductsAndRender() {
  try {
    const res = await fetch('http://localhost:8000/products');
    if (!res.ok) throw new Error('Failed to fetch products');
    const products = await res.json();
    
    productData = {}; // Clear hardcoded data
    
    products.forEach(p => {
      let category = 'dog';
      const backendCat = (p.category || '').toLowerCase();
      const nameLower = (p.product_name || p.name || '').toLowerCase();
      
      if (backendCat.includes('cat') || nameLower.includes('cat') || nameLower.includes('whiskas')) category = 'cat';
      else if (backendCat.includes('bird') || nameLower.includes('bird') || nameLower.includes('parrot') || nameLower.includes('budgie')) category = 'bird';
      else if (backendCat.includes('fish') || backendCat.includes('aquarium') || nameLower.includes('fish') || nameLower.includes('aquarium')) category = 'aquarium';
      else if (backendCat.includes('toy') || nameLower.includes('toy') || nameLower.includes('bone')) category = 'toys';
      else if (backendCat.includes('health') || backendCat.includes('grooming') || nameLower.includes('shampoo')) category = 'health';
      
      let badge = '';
      if (nameLower.includes('organic')) badge = 'Organic';
      if (nameLower.includes('premium')) badge = 'Best Seller';

      let image = p.image || '../IMG/product_dog_food.png';
      if (!p.image || p.image.includes('placehold.co')) {
        if (category === 'cat') image = '../IMG/product_cat_toys.png';
        if (category === 'health') image = '../IMG/product_shampoo.png';
        if (category === 'bird') image = '../IMG/product_bird_feed.png';
      }

      productData[p.id.toString()] = {
        name: p.product_name || p.name,
        price: p.price,
        image: image,
        category: category,
        rating: 4.5,
        reviewsCount: 100,
        description: p.product_name || p.name || 'No description available',
        badge: badge,
        highlights: ['Premium quality', 'Vet recommended'],
        ratingBreakdown: { 5: 80, 4: 10, 3: 5, 2: 3, 1: 2 },
        reviews: []
      };
    });

    renderFeaturedProducts();
  } catch(e) {
    console.error('Error fetching products', e);
    const offlineMsg = `<div style="text-align:center; padding: 40px; grid-column: 1/-1;">
      <h3 style="color:var(--text-color);">Server Offline</h3>
      <p style="color:var(--text-muted);">Please start your backend server to view products.</p>
    </div>`;
    const featuredGrid = document.getElementById('featured-products-grid');
    if (featuredGrid) featuredGrid.innerHTML = offlineMsg;
  }
}

function handleCustomerSearch() {
  const query = document.getElementById("customerSearch").value;
  renderFeaturedProducts(query);
}

function renderFeaturedProducts(searchQuery = "") {
  const grid = document.getElementById('featured-products-grid');
  if(!grid) return;
  grid.innerHTML = '';
  
  const query = searchQuery.toLowerCase().trim();
  
  // If searching, show all matching products. Else filter to highly rated products (top 8)
  const featured = Object.keys(productData)
    .filter(id => {
      const prod = productData[id];
      const pName = (prod.product_name || prod.name || "").toLowerCase();
      
      if (query) {
        return pName.includes(query) || (prod.category || "").toLowerCase().includes(query);
      }
      
      const rating = parseFloat(prod.rating) || 0;
      return rating >= 4.5;
    })
    .slice(0, query ? 50 : 8); // Show up to 50 results if searching
    
  featured.forEach(id => {
    const prod = productData[id];
    const pNameDisplay = prod.product_name || prod.name || 'Product';
    const stars = '★ ★ ★ ★ ★';
    let badgeHtml = '';
    if (prod.badge) {
      badgeHtml = `<span class="prod-badge badge-organic">${prod.badge}</span>`;
    }
    const html = `
      <div class="product-card" onclick="openProductDetail('${id}')">
        <div class="prod-image-wrapper">
          <img src="${prod.image}" alt="${pNameDisplay}" loading="lazy">
          ${badgeHtml}
        </div>
        <div class="prod-info-wrapper">
          <div class="prod-rating">${stars} <span>(${prod.rating || 4.5})</span></div>
          <h3>${pNameDisplay}</h3>
          <p class="prod-desc">${(prod.description || '').substring(0, 60)}...</p>
          <div class="prod-footer">
            <span class="price">₹${prod.price}</span>
            <button class="add-btn-round" onclick="event.stopPropagation(); addToCart('${id}', 1); showToast('${prod.name} added to cart!')" title="Add to Cart">
              <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                <line x1="12" y1="5" x2="12" y2="19"></line>
                <line x1="5" y1="12" x2="19" y2="12"></line>
              </svg>
            </button>
          </div>
        </div>
      </div>
    `;
    grid.insertAdjacentHTML('beforeend', html);
  });
}

function setThumb(el, src) {
  document.querySelectorAll('.thumb').forEach(t => t.classList.remove('active'));
  el.classList.add('active');
  document.getElementById('mainImage').src = src;
}

function changeQty(btn, delta) {
  const span = btn.parentElement.querySelector('span');
  let val = parseInt(span.textContent) + delta;
  if (val < 1) {
    removeItem(btn);
  } else {
    span.textContent = val;
    updateCartSummary();
  }
}

function removeItem(btn) {
  const card = btn.closest('.cart-card');
  if (card) {
    card.remove();
    updateCartSummary();
  }
}

function updateCartSummary() {
  let subtotal = 0;
  const cards = document.querySelectorAll('#page-cart .cart-card');
  cards.forEach(card => {
    const priceText = card.querySelector('.cart-price').textContent;
    const priceVal = parseFloat(priceText.replace(/[^\d]/g, ''));
    const qtyVal = parseInt(card.querySelector('.qty-controls span').textContent);
    subtotal += priceVal * qtyVal;
  });
  
  const shipping = subtotal > 0 ? 50 : 0;
  const total = subtotal + shipping;
  
  // Update order summary UI
  const summaryCard = document.querySelector('#page-cart .summary-card');
  if (summaryCard) {
    const subtotalEl = summaryCard.querySelector('.summary-row:nth-of-type(1) .summary-val');
    const shippingEl = summaryCard.querySelector('.summary-row:nth-of-type(2) .summary-val');
    const totalEl = summaryCard.querySelector('.summary-row.total .summary-val');
    
    if (subtotalEl) subtotalEl.textContent = '₹' + subtotal;
    if (shippingEl) shippingEl.textContent = '₹' + shipping;
    if (totalEl) totalEl.textContent = '₹' + total;
  }
  
  // Update header cart badge counters
  const totalQty = Array.from(cards).reduce((sum, card) => sum + parseInt(card.querySelector('.qty-controls span').textContent), 0);
  const badges = document.querySelectorAll('.cart-badge-dot');
  badges.forEach(badge => {
    badge.textContent = totalQty;
    badge.style.display = totalQty > 0 ? 'flex' : 'none';
  });
}

// ----------------------------------------------------
// ----------------------------------------------------

let productData = {};


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

let currentDetailProductId = '';
let currentDetailQty = 1;

function openProductDetail(productId) {
  const product = productData[productId];
  if (!product) return;
  
  currentDetailProductId = productId;
  currentDetailQty = 1;
  document.getElementById('detail-qty-val').textContent = currentDetailQty;
  
  // Gallery - Main Image
  const mainImg = document.getElementById('mainImage');
  mainImg.src = product.image;
  mainImg.alt = product.name;
  
  // Gallery - Thumbnails (Main + 2 custom placeholders)
  const thumbRow = document.getElementById('pd-thumbnails');
  thumbRow.innerHTML = '';
  
  // Prepare thumbnails list
  const thumbs = [
    { src: product.image, label: 'Main View' },
    { src: `https://placehold.co/600x500/6d5dfc/ffffff?text=${encodeURIComponent(product.name + ' - Details')}`, label: 'Specs' },
    { src: `https://placehold.co/600x500/10b981/ffffff?text=${encodeURIComponent('Usage %26 Guide')}`, label: 'Guide' }
  ];
  
  thumbs.forEach((t, index) => {
    const img = document.createElement('img');
    img.className = 'thumb' + (index === 0 ? ' active' : '');
    img.src = t.src;
    img.alt = t.label;
    img.onclick = function() { setThumb(this, t.src); };
    thumbRow.appendChild(img);
  });
  
  // Text Info
  document.getElementById('pd-title').textContent = product.name;
  document.getElementById('pd-price').textContent = '₹' + product.price;
  document.getElementById('pd-desc').textContent = product.description;
  
  // Stars Rating
  const starsString = '★'.repeat(Math.round(product.rating)) + '☆'.repeat(5 - Math.round(product.rating));
  document.getElementById('pd-stars-top').textContent = starsString;
  document.getElementById('pd-rating-text').textContent = `${product.rating} (${product.reviewsCount} Reviews)`;
  
  // Details list (Highlights)
  const featuresList = document.getElementById('pd-features-list');
  featuresList.innerHTML = '';
  product.highlights.forEach(highlight => {
    const item = document.createElement('div');
    item.className = 'feature-item-pill';
    item.innerHTML = `
      <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round">
        <polyline points="20 6 9 17 4 12"></polyline>
      </svg>
      <span>${highlight}</span>
    `;
    featuresList.appendChild(item);
  });
  
  // Reviews stats
  document.getElementById('pd-rating-num').textContent = product.rating;
  document.getElementById('pd-stars-breakdown').textContent = starsString;
  document.getElementById('pd-reviews-count').textContent = `${product.reviewsCount} Reviews`;
  
  // Progress Bars
  const barsContainer = document.getElementById('pd-rating-bars');
  barsContainer.innerHTML = '';
  for (let stars = 5; stars >= 1; stars--) {
    const pct = product.ratingBreakdown[stars] || 0;
    const barRow = document.createElement('div');
    barRow.className = 'rating-bar-row';
    barRow.innerHTML = `
      <span>${stars} ★</span>
      <div class="progress-bar-bg"><div class="progress-bar-fill" style="width: ${pct}%;"></div></div>
      <span>${pct}%</span>
    `;
    barsContainer.appendChild(barRow);
  }
  
  // Reviews list
  const reviewsContainer = document.getElementById('pd-reviews-list');
  reviewsContainer.innerHTML = '';
  
  // Avatars and styling
  const avatarColors = ['#6d5dfc', '#10b981', '#f59e0b', '#3b82f6', '#ec4899'];
  product.reviews.forEach((r, idx) => {
    const initials = r.author.substring(0, 2).toUpperCase();
    const color = avatarColors[idx % avatarColors.length];
    const reviewStars = '★'.repeat(r.rating) + '☆'.repeat(5 - r.rating);
    
    const card = document.createElement('div');
    card.className = 'premium-review-card';
    card.innerHTML = `
      <div class="review-header">
        <div class="reviewer-avatar" style="background: ${color};">${initials}</div>
        <div class="reviewer-meta">
          <h4>${r.author}</h4>
          <div class="review-stars-row">
            <div class="stars-gold">${reviewStars}</div>
            <span class="review-date">${r.date}</span>
          </div>
        </div>
      </div>
      <p class="review-comment">${r.text}</p>
    `;
    reviewsContainer.appendChild(card);
  });
  
  // Setup buttons action
  const addToCartBtn = document.getElementById('pd-add-to-cart-btn');
  addToCartBtn.onclick = function() {
    addToCart(productId, currentDetailQty);
    showToast(`Added ${currentDetailQty} x ${product.name} to cart!`);
  };
  
  const buyNowBtn = document.getElementById('pd-buy-now-btn');
  buyNowBtn.onclick = function() {
    addToCart(productId, currentDetailQty);
    nav('cart');
  };
  
  const wishlistBtn = document.getElementById('pd-wishlist-btn');
  if (wishlistBtn) {
    wishlistBtn.onclick = function() {
      toggleWishlist(productId);
    };
    updateWishlistIcon(productId);
  }
  
  // Navigate
  nav('product');
}

function changeDetailQty(delta) {
  currentDetailQty += delta;
  if (currentDetailQty < 1) currentDetailQty = 1;
  document.getElementById('detail-qty-val').textContent = currentDetailQty;
}

function addToCart(productId, qty) {
  qty = parseInt(qty);
  if (isNaN(qty) || qty < 1) qty = 1;
  
  const product = productData[productId];
  if (!product) return;
  
  // Check if item is already in cart
  const cartContainer = document.querySelector('#page-cart .cart-items-box');
  if (!cartContainer) return;
  
  let existingCard = cartContainer.querySelector(`.cart-card[data-product-id="${productId}"]`);
  
  if (existingCard) {
    const qtySpan = existingCard.querySelector('.qty-controls span');
    if (qtySpan) {
      qtySpan.textContent = parseInt(qtySpan.textContent) + qty;
    }
  } else {
    // Create new cart card
    const cardHtml = `
      <div class="cart-card" data-product-id="${productId}">
        <img class="cart-item-thumb" src="${product.image}" alt="${product.name}">
        <div class="cart-item-info">
          <h3>${product.name}</h3>
          <p class="cart-price">₹${product.price}</p>
        </div>
        <div class="qty-controls">
          <button onclick="changeQty(this,-1)">−</button>
          <span>${qty}</span>
          <button onclick="changeQty(this,1)">+</button>
        </div>
        <button class="remove-btn" onclick="removeItem(this)">
          <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" style="margin-right: 4px;">
            <polyline points="3 6 5 6 21 6"></polyline>
            <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path>
          </svg>
          Remove
        </button>
      </div>
    `;
    cartContainer.insertAdjacentHTML('beforeend', cardHtml);
  }
  
  updateCartSummary();
}

function showToast(message) {
  let container = document.getElementById('toast-container');
  if (!container) {
    container = document.createElement('div');
    container.id = 'toast-container';
    document.body.appendChild(container);
  }
  
  const toast = document.createElement('div');
  toast.className = 'toast-notification';
  toast.innerHTML = `
    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round" style="color: #10b981; flex-shrink: 0;">
      <polyline points="20 6 9 17 4 12"></polyline>
    </svg>
    <span>${message}</span>
  `;
  container.appendChild(toast);
  
  // Trigger entry animation
  setTimeout(() => toast.classList.add('show'), 10);
  
  // Auto remove
  setTimeout(() => {
    toast.classList.remove('show');
    setTimeout(() => toast.remove(), 300);
  }, 3000);
}

// ----------------------------------------------------
// DYNAMIC CHECKOUT & ORDER LIFECYCLE
// ----------------------------------------------------

let ordersData = [];

async function fetchOrders() {
  try {
    const res = await fetch('http://localhost:8000/orders');
    if (!res.ok) return;
    const orders = await res.json();
    
    ordersData = orders.map(o => ({
      id: o.id,
      date: o.created_at ? new Date(o.created_at).toLocaleDateString() : 'Recent',
      status: o.status,
      items: o.items.map(item => ({
        productId: item.product_id,
        qty: item.quantity,
        price: item.price
      }))
    })).reverse(); // Newest first
    renderOrders();
  } catch(e) {
    console.error('Error fetching orders:', e);
  }
}

// Call fetchOrders on load
window.addEventListener("DOMContentLoaded", () => {
  fetchOrders();
});

function renderOrders() {
  const container = document.getElementById('orders-list-container');
  if (!container) return;
  
  container.innerHTML = '';
  
  if (ordersData.length === 0) {
    container.innerHTML = `
      <div style="text-align: center; padding: 40px; color: var(--slate); font-weight: 500;">
        <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" style="margin-bottom: 16px; color: #cbd5e1; display: block; margin-left: auto; margin-right: auto;">
          <rect x="3" y="4" width="18" height="18" rx="2" ry="2"></rect>
          <line x1="16" y1="2" x2="16" y2="6"></line>
          <line x1="8" y1="2" x2="8" y2="6"></line>
          <line x1="3" y1="10" x2="21" y2="10"></line>
        </svg>
        <p>No orders placed yet. Start shopping!</p>
      </div>
    `;
    return;
  }
  
  ordersData.forEach(order => {
    let itemsHtml = '';
    
    order.items.forEach(item => {
      const prod = productData[item.productId];
      const name = prod ? prod.name : 'Pet Essential Product';
      const image = prod ? prod.image : '../IMG/product_dog_food.png';
      const itemTotal = item.price * item.qty;
      
      itemsHtml += `
        <div class="order-item-row">
          <img class="order-item-thumb" src="${image}" alt="${name}">
          <div class="order-item-info">
            <h4>${name}</h4>
            <p class="order-item-details">Quantity: ${item.qty} &nbsp;|&nbsp; Unit Price: ₹${item.price}</p>
          </div>
          <div class="order-item-price">
            <span class="total-label">Total Amount</span>
            <span class="price-val">₹${itemTotal}</span>
          </div>
        </div>
      `;
    });
    
    // Status settings
    let statusClass = 'badge-pending';
    let statusText = 'Processing';
    let trackWidth = '33.3%';
    let stepClasses = ['', '', '', ''];
    let stepIcons = ['1', '2', '3', '4'];
    
    if (order.status === 'delivered') {
      statusClass = 'badge-delivered';
      statusText = 'Delivered';
      trackWidth = '100%';
      stepClasses = ['completed', 'completed', 'completed', 'completed active'];
      stepIcons = ['✓', '✓', '✓', '✓'];
    } else if (order.status === 'shipped') {
      statusClass = 'badge-shipping';
      statusText = 'Shipped';
      trackWidth = '66.6%';
      stepClasses = ['completed', 'completed', 'completed active', ''];
      stepIcons = ['✓', '✓', '✓', '4'];
    } else {
      statusClass = 'badge-pending';
      statusText = 'Processing';
      trackWidth = '33.3%';
      stepClasses = ['completed', 'completed active', '', ''];
      stepIcons = ['✓', '✓', '3', '4'];
    }
    
    const cardHtml = `
      <div class="order-card-premium">
        <div class="order-card-header">
          <div class="order-meta">
            <h3>Order #${order.id}</h3>
            <span class="order-date">${order.date}</span>
          </div>
          <span class="order-status-badge ${statusClass}">${statusText}</span>
        </div>
        
        <div class="order-card-body">
          ${itemsHtml}
          
          <div class="order-stepper-container">
            <div class="order-stepper">
              <div class="order-stepper-track-active" style="width: ${trackWidth};"></div>
              
              <div class="stepper-step ${stepClasses[0]}">
                <div class="stepper-icon">${stepIcons[0]}</div>
                <div class="stepper-label">Ordered</div>
              </div>
              <div class="stepper-step ${stepClasses[1]}">
                <div class="stepper-icon">${stepIcons[1]}</div>
                <div class="stepper-label">Packed</div>
              </div>
              <div class="stepper-step ${stepClasses[2]}">
                <div class="stepper-icon">${stepIcons[2]}</div>
                <div class="stepper-label">Shipped</div>
              </div>
              <div class="stepper-step ${stepClasses[3]}">
                <div class="stepper-icon">${stepIcons[3]}</div>
                <div class="stepper-label">Delivered</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    `;
    
    container.insertAdjacentHTML('beforeend', cardHtml);
  });
}

let checkoutItems = [];
let selectedPaymentMethod = 'card';

function openCheckout() {
  const cartCards = document.querySelectorAll('#page-cart .cart-card');
  if (cartCards.length === 0) {
    showToast('Your cart is empty! Add products to shop.');
    return;
  }
  
  checkoutItems = [];
  let subtotal = 0;
  
  const coItemsList = document.getElementById('co-items-list');
  coItemsList.innerHTML = '';
  
  cartCards.forEach(card => {
    const productId = card.getAttribute('data-product-id');
    const qty = parseInt(card.querySelector('.qty-controls span').textContent);
    const prod = productData[productId];
    
    if (prod) {
      const price = prod.price;
      const totalItemVal = price * qty;
      subtotal += totalItemVal;
      
      checkoutItems.push({
        productId: productId,
        qty: qty,
        price: price
      });
      
      const itemHtml = `
        <div class="checkout-review-item">
          <img src="${prod.image}" alt="${prod.name}">
          <div class="review-item-info">
            <h4>${prod.name}</h4>
            <p>Qty: ${qty} &times; ₹${price}</p>
          </div>
          <span class="review-item-price">₹${totalItemVal}</span>
        </div>
      `;
      coItemsList.insertAdjacentHTML('beforeend', itemHtml);
    }
  });
  
  const shipping = subtotal > 0 ? 50 : 0;
  const total = subtotal + shipping;
  
  document.getElementById('co-subtotal').textContent = '₹' + subtotal;
  document.getElementById('co-shipping').textContent = '₹' + shipping;
  document.getElementById('co-total').textContent = '₹' + total;
  
  const placeOrderBtn = document.querySelector('.place-order-btn');
  if (placeOrderBtn) {
    placeOrderBtn.innerHTML = `
      <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" style="margin-right: 6px;">
        <rect x="3" y="11" width="18" height="11" rx="2" ry="2"></rect>
        <path d="M7 11V7a5 5 0 0 1 10 0v4"></path>
      </svg>
      Confirm &amp; Place Order (₹${total})
    `;
  }
  
  selectPaymentMethod('card');
  nav('checkout');
}

function selectPaymentMethod(method) {
  selectedPaymentMethod = method;
  
  document.querySelectorAll('.pay-tab').forEach(tab => {
    tab.classList.remove('active');
  });
  
  const activeTab = document.querySelector(`.pay-tab[onclick*="${method}"]`);
  if (activeTab) activeTab.classList.add('active');
  
  document.querySelectorAll('.payment-panel-content').forEach(panel => {
    panel.classList.remove('active');
  });
  
  const activePanel = document.getElementById('panel-' + method);
  if (activePanel) activePanel.classList.add('active');
}

async function placeOrder() {
  const name = document.getElementById('co-name').value.trim();
  const phone = document.getElementById('co-phone').value.trim();
  const pincode = document.getElementById('co-pincode').value.trim();
  const address = document.getElementById('co-address').value.trim();
  const city = document.getElementById('co-city').value.trim();
  const state = document.getElementById('co-state').value.trim();
  
  if (!name || !phone || !pincode || !address || !city || !state) {
    alert('Please fill out all shipping details.');
    return;
  }
  
  if (selectedPaymentMethod === 'card') {
    const cardnum = document.getElementById('co-cardnum').value.trim();
    const expiry = document.getElementById('co-cardexpiry').value.trim();
    const cvv = document.getElementById('co-cardcvv').value.trim();
    if (!cardnum || !expiry || !cvv) {
      alert('Please fill in card details.');
      return;
    }
  } else if (selectedPaymentMethod === 'upi') {
    const upiid = document.getElementById('co-upiid').value.trim();
    if (!upiid || !upiid.includes('@')) {
      alert('Please enter a valid UPI ID (e.g. username@upi).');
      return;
    }
  }
  
  const fullAddress = `${address}, ${city}, ${state} - ${pincode}`;
  const payload = {
    customer_name: name,
    customer_phone: phone,
    customer_address: fullAddress,
    delivery_slot: "ASAP",
    items: checkoutItems.map(item => ({
      product_id: parseInt(item.productId.toString().replace(/\\D/g, '') || 1),
      quantity: item.qty
    }))
  };

  try {
    const response = await fetch('http://localhost:8000/orders', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || 'Failed to place order');
    }

    const orderData = await response.json();
    
    // Convert to frontend format
    const newOrder = {
      id: orderData.id,
      date: 'Placed just now',
      status: orderData.status || 'pending',
      items: checkoutItems
    };
    
    ordersData.unshift(newOrder);
    
    const cartContainer = document.querySelector('#page-cart .cart-items-box');
    if (cartContainer) {
      cartContainer.innerHTML = '<h2>Your Cart</h2>';
    }
    
    updateCartSummary();
    renderOrders();
    nav('orders');
    showToast(`Order #${orderData.id} placed successfully!`);
  } catch (error) {
    alert('Order Error: ' + error.message);
  }
}

// ----------------------------------------------------
// DYNAMIC CATEGORIES FILTERING
// ----------------------------------------------------

const categoryConfigs = {
  dog: { title: 'Dog Food Essentials', emoji: '🐶', desc: 'Premium selection of nutritious high-protein kibble, wet meals, and treats.', themeClass: 'hero-dog' },
  cat: { title: 'Cat Food Gourmet', emoji: '🐱', desc: 'Curated selection of delicious fish meals, savory broths, and kitten mixes.', themeClass: 'hero-cat' },
  bird: { title: 'Bird Care & Nutrition', emoji: '🦜', desc: 'Vitamin-enriched seeds, grains, and accessories for balcony birds and aviaries.', themeClass: 'hero-bird' },
  aquarium: { title: 'Aquarium & Fish Care', emoji: '🐟', desc: 'Premium food flakes, water filters, and accessories for healthy aquariums.', themeClass: 'hero-aquarium' },
  toys: { title: 'Interactive Pet Toys', emoji: '🧸', desc: 'Fun and durable toys to keep your furry friends active, healthy, and happy.', themeClass: 'hero-toys' },
  health: { title: 'Healthcare & Grooming', emoji: '💊', desc: 'Soothing organic shampoos, multivitamin supplements, and grooming tools.', themeClass: 'hero-health' }
};

function openCategory(categoryKey) {
  const config = categoryConfigs[categoryKey];
  if (!config) return;
  
  document.getElementById('co-category-title').textContent = `${config.emoji} ${config.title}`;
  document.getElementById('co-category-desc').textContent = config.desc;
  
  const hero = document.getElementById('co-category-hero');
  hero.className = 'category-hero'; // Reset
  hero.classList.add(config.themeClass);
  
  const grid = document.getElementById('category-products-grid');
  grid.innerHTML = '';
  
  if (Object.keys(productData).length === 0) {
    grid.innerHTML = `<div style="text-align:center; padding: 40px; grid-column: 1/-1;">
      <h3 style="color:var(--text-color);">Server Offline</h3>
      <p style="color:var(--text-muted);">Please start your backend server to view products.</p>
    </div>`;
    return;
  }
  
  let found = false;
  for (const [id, prod] of Object.entries(productData)) {
    if (prod.category === categoryKey) {
      found = true;
      const stars = '★ '.repeat(Math.round(prod.rating)) + '☆ '.repeat(5 - Math.round(prod.rating));
      
      let badgeHtml = '';
      if (prod.badge) {
        let badgeClass = 'badge-organic';
        if (prod.badge.toLowerCase().includes('best')) badgeClass = 'badge-bestseller';
        if (prod.badge.toLowerCase().includes('new')) badgeClass = 'badge-new';
        badgeHtml = `<span class="prod-badge ${badgeClass}">${prod.badge}</span>`;
      }
      
      const cardHtml = `
        <div class="product-card" onclick="openProductDetail('${id}')">
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
              <button class="add-btn-round" onclick="event.stopPropagation(); addToCart('${id}', 1); showToast('${prod.name} added to cart!')" title="Add to Cart">
                <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                  <line x1="12" y1="5" x2="12" y2="19"></line>
                  <line x1="5" y1="12" x2="19" y2="12"></line>
                </svg>
              </button>
            </div>
          </div>
        </div>
      `;
      grid.insertAdjacentHTML('beforeend', cardHtml);
    }
  }
  
  if (!found) {
    grid.innerHTML = `
      <div style="grid-column: 1 / -1; text-align: center; padding: 40px; color: var(--slate); font-weight: 500;">
        <p>No products found in this category right now. Check back soon!</p>
      </div>
    `;
  }
  
  nav('category');
}
