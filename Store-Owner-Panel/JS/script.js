function nav(page) {
  document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
  document.getElementById('page-' + page).classList.add('active');
  window.scrollTo({ top: 0, behavior: 'smooth' });
}

function selectRole(btn) {
  btn.closest('.role-selector').querySelectorAll('.role-btn')
    .forEach(b => b.classList.remove('active'));
  btn.classList.add('active');
  
  // Hide guest button for Admin
  const role = btn.textContent.trim();
  const guestBtn = document.getElementById('guest-login-btn');
  if (guestBtn) {
    if (role === 'Admin') {
      guestBtn.style.display = 'none';
    } else {
      guestBtn.style.display = 'block';
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
    window.location.href = 'dashboard.html?role=manager&guest=true';
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
  renderOrders();
  updateCartSummary();
});

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
// PRODUCT DETAILS & TOAST DYNAMICS
// ----------------------------------------------------

const productData = {
  dog_food: {
    name: 'Premium Dog Food',
    price: 599,
    image: '../IMG/product_dog_food.png',
    category: 'dog',
    rating: 4.8,
    reviewsCount: 523,
    description: 'High-protein dog food made from premium organic ingredients for healthier growth, stronger immunity, and active lifestyles.',
    badge: 'Organic',
    highlights: [
      'High Protein Formula with real chicken & grains',
      'Rich in Vitamins, Minerals, and Omega-3 for shiny coat',
      'Suitable For All Breeds & Age Groups',
      'Recommended by leading pet nutritionists & veterinarians'
    ],
    ratingBreakdown: { 5: 82, 4: 12, 3: 4, 2: 1, 1: 1 },
    reviews: [
      { author: 'Rahul', rating: 5, date: '3 days ago', text: 'My dog loved it immediately. Very good kibble size and digestability. Highly recommend!' },
      { author: 'Priya', rating: 5, date: '1 week ago', text: 'Packaging was excellent and double sealed. Clean, natural ingredients are visible. Vet recommended.' },
      { author: 'Vikram', rating: 4, date: '2 weeks ago', text: 'Great quality food. My lab has a noticeably shinier coat now. Shipping took two days.' }
    ]
  },
  cat_toys: {
    name: 'Cat Toy Pack',
    price: 349,
    image: '../IMG/product_cat_toys.png',
    category: 'toys',
    rating: 4.9,
    reviewsCount: 312,
    description: 'Interactive 6-in-1 variety set designed to keep your cats active, playful, and mentally stimulated throughout the day.',
    badge: 'Best Seller',
    highlights: [
      '6-in-1 variety pack (crinkle balls, mice, play feathers)',
      'Non-toxic organic catnip infusions and natural dye-free fibers',
      'Promotes active exercises, jumping, and claw wellness',
      'Durable stitching made to resist intensive clawing and biting'
    ],
    ratingBreakdown: { 5: 91, 4: 6, 3: 2, 2: 1, 1: 0 },
    reviews: [
      { author: 'Sneha', rating: 5, date: '2 days ago', text: 'My kitten went absolutely wild for the feather wand and the little mice! Best cat toys I have bought.' },
      { author: 'Rohan', rating: 5, date: '5 days ago', text: 'Highly interactive set. Sturdy materials, has lasted through weeks of aggressive chewing.' },
      { author: 'Divya', rating: 4, date: '1 month ago', text: 'Nice toys and good variety. The rod for the wand is a bit short but works great anyway!' }
    ]
  },
  shampoo: {
    name: 'Pet Shampoo',
    price: 249,
    image: '../IMG/product_shampoo.png',
    category: 'health',
    rating: 4.7,
    reviewsCount: 184,
    description: 'Gentle organic lavender and oatmeal formula tailored specifically to soothe dry, itchy, or sensitive pet skin.',
    badge: 'New',
    highlights: [
      'Organic oatmeal & fresh lavender extracts for natural aroma',
      'Balanced pH formula optimized for both dogs and cats',
      '100% paraben-free, dye-free, alcohol-free, and soap-free',
      'Eliminates wet pet odors and maintains a soft, glossy coat'
    ],
    ratingBreakdown: { 5: 78, 4: 15, 3: 5, 2: 1, 1: 1 },
    reviews: [
      { author: 'Anjali', rating: 5, date: '4 days ago', text: 'Smells incredibly clean and fresh! Lathers perfectly and is very gentle on my pup\'s sensitive skin.' },
      { author: 'Manoj', rating: 4, date: '1 week ago', text: 'Lathers nicely and washes off clean. The lavender scent is very soothing during bath time.' },
      { author: 'Tina', rating: 5, date: '3 weeks ago', text: 'No more scratching or redness after baths. Will buy this brand exclusively from now on.' }
    ]
  },
  bird_feed: {
    name: 'Bird Feed',
    price: 199,
    image: '../IMG/product_bird_feed.png',
    category: 'bird',
    rating: 4.6,
    reviewsCount: 98,
    description: 'Nutritious premium seed mix enriched with essential vitamins and calcium, perfect for wild birds and companion aviaries.',
    badge: '100% Organic',
    highlights: [
      'Multi-grain mix with striped sunflower seeds & millet',
      'Enriched with calcium and amino acids for beak and egg health',
      'Promotes feather vibrant coloration and natural foraging habits',
      '100% pesticide-free, triple-cleaned to prevent dust and weed seeds'
    ],
    ratingBreakdown: { 5: 72, 4: 18, 3: 7, 2: 2, 1: 1 },
    reviews: [
      { author: 'Arjun', rating: 5, date: '2 days ago', text: 'The sparrows and lovebirds in my balcony adore this mix. Very clean seeds, no dust.' },
      { author: 'Pooja', rating: 4, date: '6 days ago', text: 'Good assortment of grains. Attracts a wide variety of local birds every morning.' },
      { author: 'Karan', rating: 5, date: '2 weeks ago', text: 'Excellent quality seed packet. Scarcely any waste or empty shells. Will buy again.' }
    ]
  },
  cat_food: {
    name: 'Gourmet Cat Salmon Feast',
    price: 429,
    image: 'https://placehold.co/600x500/ffedd5/ea580c?text=Salmon+Cat+Feast',
    category: 'cat',
    rating: 4.8,
    reviewsCount: 156,
    description: 'Delectable salmon and tuna wet feast loaded with essential taurine and ocean nutrients for mature cats.',
    badge: 'Bestseller',
    highlights: [
      'Rich in Omega-3 fatty acids for hairball control',
      'Contains essential Taurine for vision and cardiac health',
      '100% grain-free recipe with real wild-caught salmon flakes',
      'Hydrates and balances urinary tract environment'
    ],
    ratingBreakdown: { 5: 84, 4: 10, 3: 4, 2: 1, 1: 1 },
    reviews: [
      { author: 'Meera', rating: 5, date: '4 days ago', text: 'My cat is extremely picky but cleaned her bowl immediately! Excellent moisture content.' },
      { author: 'Ravi', rating: 5, date: '1 week ago', text: 'Very high quality ingredients, smells like real fish. Highly recommend for coat shine.' }
    ]
  },
  aquarium_flakes: {
    name: 'Premium Goldfish Flakes',
    price: 180,
    image: 'https://placehold.co/600x500/e0f2fe/0284c7?text=Goldfish+Flakes',
    category: 'aquarium',
    rating: 4.7,
    reviewsCount: 84,
    description: 'Highly digestible, color-enhancing flake food formulated to keep pond fish and goldfish healthy and tank water clean.',
    badge: 'New',
    highlights: [
      'Probiotic formula supporting robust immune systems',
      'Natural carotenoids to enhance vibrant gold and red coloring',
      'Clean water formulation that will not cloud aquarium water',
      'Rich in vitamin C and mineral blends for scale development'
    ],
    ratingBreakdown: { 5: 76, 4: 16, 3: 6, 2: 2, 1: 0 },
    reviews: [
      { author: 'Sanjay', rating: 5, date: '3 days ago', text: 'My goldfish are much more active and their colors are visibly brighter. Flakes float well.' },
      { author: 'Aditi', rating: 4, date: '2 weeks ago', text: 'Very good food. Tank stays very clean, no nasty smell or clouding. Great value.' }
    ]
  },
  chew_bone: {
    name: 'Natural Chew Toy Bone',
    price: 299,
    image: 'https://placehold.co/600x500/f3e8ff/9333ea?text=Natural+Chew+Bone',
    category: 'toys',
    rating: 4.6,
    reviewsCount: 142,
    description: 'Durable, allergen-free dental chew toy bone made from natural rubber, perfect for active chewing and cleaning teeth.',
    badge: 'Organic',
    highlights: [
      'Made from 100% natural, non-toxic eco-friendly rubber',
      'Ridged texture sweeps away plaque and tartar during play',
      'Infused with mild natural beef flavor to attract interest',
      'Tough structure designed to withstand large dogs'
    ],
    ratingBreakdown: { 5: 70, 4: 20, 3: 7, 2: 2, 1: 1 },
    reviews: [
      { author: 'Kartik', rating: 5, date: '5 days ago', text: 'My golden retriever has chewed this for hours daily and it shows no damage. Highly durable!' },
      { author: 'Nisha', rating: 4, date: '1 month ago', text: 'Excellent chew toy. Really helps with puppy teething. Teeth look much cleaner.' }
    ]
  },
  vitamins: {
    name: 'Pet Multivitamin Drops',
    price: 399,
    image: 'https://placehold.co/600x500/fce7f3/db2777?text=Multivitamin+Drops',
    category: 'health',
    rating: 4.8,
    reviewsCount: 112,
    description: 'Daily liquid multivitamin drops rich in vitamins A, D, E, and calcium to promote strong bones and high energy.',
    badge: '100% Organic',
    highlights: [
      'Comprehensive vitamin profile (A, B-Complex, D3, E)',
      'Liquid dropper format for easy mixing with pet food',
      'Supports puppy bone growth, joint flexibility, and vitality',
      'All-natural, sugar-free, preservative-free drops'
    ],
    ratingBreakdown: { 5: 85, 4: 10, 3: 3, 2: 1, 1: 1 },
    reviews: [
      { author: 'Harish', rating: 5, date: '2 days ago', text: 'My older dog has much more energy since starting these drops. Easy to mix in kibble.' },
      { author: 'Ritu', rating: 5, date: '3 weeks ago', text: 'Excellent daily booster. Coat is shedding less, highly recommend for senior pet care.' }
    ]
  }
};

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

let ordersData = [
  {
    id: 'PK1001',
    date: 'Placed on June 8, 2026',
    status: 'delivered',
    items: [
      { productId: 'dog_food', qty: 2, price: 599 }
    ]
  },
  {
    id: 'PK1002',
    date: 'Placed on June 9, 2026',
    status: 'shipped',
    items: [
      { productId: 'shampoo', qty: 1, price: 249 }
    ]
  },
  {
    id: 'PK1003',
    date: 'Placed on June 9, 2026',
    status: 'processing',
    items: [
      { productId: 'bird_feed', qty: 3, price: 199 }
    ]
  }
];

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

function placeOrder() {
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
  
  const orderId = 'PK' + Math.floor(1000 + Math.random() * 9000);
  
  const months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'];
  const today = new Date();
  const dateStr = `Placed on ${months[today.getMonth()]} ${today.getDate()}, ${today.getFullYear()}`;
  
  const newOrder = {
    id: orderId,
    date: dateStr,
    status: 'processing',
    items: [...checkoutItems]
  };
  
  ordersData.unshift(newOrder);
  
  const cartContainer = document.querySelector('#page-cart .cart-items-box');
  if (cartContainer) {
    cartContainer.innerHTML = '<h2>Your Cart</h2>';
  }
  
  updateCartSummary();
  renderOrders();
  nav('orders');
  showToast(`Order #${orderId} placed successfully!`);
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
