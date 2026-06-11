// Mock Database State (Now loaded from backend)
let products = [];
let orders = [];
let reviews = [];

let deliveryZones = ["Bangalore Central", "Bangalore East", "Mumbai Central"];
let viewMode = "grid";
let activePage = "dashboard";

async function fetchDashboardData() {
  try {
    const pRes = await fetch('http://localhost:8000/products');
    products = await pRes.json();
    
    const oRes = await fetch('http://localhost:8000/orders');
    orders = await oRes.json();
    
    const rRes = await fetch('http://localhost:8000/reviews');
    reviews = await rRes.json();
    
    if (activePage === "dashboard") updateDashboardPage();
    if (activePage === "products") renderProducts();
    if (activePage === "inventory") renderInventory();
    if (activePage === "orders") renderOrders();
    if (activePage === "reviews") renderReviews();
  } catch (e) {
    console.error("Failed to fetch data", e);
  }
}

// ── NAVIGATION ──
const breadcrumbLabels = {
  dashboard: "Dashboard > Home",
  products: "Dashboard > Products",
  inventory: "Dashboard > Inventory",
  orders: "Dashboard > Orders",
  reviews: "Dashboard > Reviews",
  reports: "Dashboard > Reports",
  settings: "Dashboard > Settings"
};

let navHistory = [];
function switchPage(name, addToHistory = true) {
  if (addToHistory) {
    const activePage = document.querySelector('.dashboard-page.active');
    if (activePage) {
      const activeId = activePage.id.replace('page-', '');
      if (activeId !== name) {
        navHistory.push(activeId);
      }
    }
  }
  document.querySelectorAll('.dashboard-page').forEach(p => p.classList.remove('active'));
  document.querySelectorAll('.nav-links li').forEach(li => li.classList.remove('active'));
  
  const pageElement = document.getElementById('page-' + name);
  if (pageElement) pageElement.classList.add('active');
  
  const navLink = document.querySelector(`li[onclick="switchPage('${name}')"]`);
  if (navLink) navLink.classList.add('active');

  // Update breadcrumb
  document.getElementById("breadcrumb").textContent = breadcrumbLabels[name] || "Dashboard";
  
  // Update sidebar active classes
  document.querySelectorAll(".sidebar ul li").forEach(li => {
    li.classList.toggle("active", li.getAttribute("data-page") === name);
  });

  activePage = name;
  window.scrollTo({ top: 0, behavior: "smooth" });

  // Page specific render triggers
  if (name === "dashboard") updateDashboardPage();
  else if (name === "products") renderProducts();
  else if (name === "inventory") renderInventory();
  else if (name === "orders") renderOrders();
  else if (name === "reviews") renderReviews();
  else if (name === "reports") renderReports();
  else if (name === "settings") renderSettings();
}

// Bind Navigation Click Events
document.querySelectorAll(".sidebar ul li[data-page]").forEach(li => {
  li.addEventListener("click", () => {
    switchPage(li.getAttribute("data-page"));
  });
});

// ── GLOBAL SEARCH ──
function handleGlobalSearch() {
  const query = document.getElementById("globalSearch").value.toLowerCase();
  
  if (activePage === "products") {
    document.getElementById("productSearch").value = query;
    filterProducts();
  } else if (activePage === "inventory") {
    document.getElementById("inventorySearch").value = query;
    filterInventory();
  } else if (activePage === "orders") {
    document.getElementById("orderSearch").value = query;
    filterOrders();
  } else {
    // If on other pages, search across active lists
    console.log("Global search query:", query);
  }
}

// ── DASHBOARD ACTIONS ──
function updateDashboardPage() {
  // Calculate stats
  const lowStockCount = products.filter(p => p.stockStatus === "low-stock" || p.stockStatus === "out-stock").length;
  document.getElementById("dash-low-stock-count").textContent = lowStockCount;

  // Render recent orders (limit to 3)
  const container = document.getElementById("dashboardOrdersList");
  container.innerHTML = "";
  
  orders.slice(0, 3).forEach(order => {
    container.innerHTML += `
      <div class="order-card">
        <div>
          <h4>#${order.id}</h4>
          <p>${order.customer} • ${order.items}</p>
        </div>
        <span class="badge ${order.status}">${order.status.charAt(0).toUpperCase() + order.status.slice(1)}</span>
      </div>
    `;
  });
}

// ── PRODUCTS OPERATIONS ──
function setView(mode) {
  viewMode = mode;
  const container = document.getElementById("productsContainer");
  const gridBtn = document.getElementById("gridBtn");
  const listBtn = document.getElementById("listBtn");

  if (mode === "list") {
    container.classList.add("list-view");
    listBtn.classList.add("active");
    gridBtn.classList.remove("active");
  } else {
    container.classList.remove("list-view");
    gridBtn.classList.add("active");
    listBtn.classList.remove("active");
  }
  renderProducts();
}

function renderProducts() {
  const container = document.getElementById("productsContainer");
  container.innerHTML = "";

  const query = document.getElementById("productSearch").value.toLowerCase();
  const categoryFilter = document.getElementById("productFilterCategory").value;
  const statusFilter = document.getElementById("productFilterStatus").value;
  const sortBy = document.getElementById("productSort").value;

  // Apply filters
  let filtered = products.filter(p => {
    const pName = (p.product_name || p.name || "").toLowerCase();
    const matchesSearch = pName.includes(query) || (p.category || "").toLowerCase().includes(query);
    const matchesCategory = categoryFilter === "All" || p.category === categoryFilter;
    const matchesStatus = statusFilter === "All" || p.stockStatus === statusFilter;
    return matchesSearch && matchesCategory && matchesStatus;
  });

  // Apply sorting
  if (sortBy === "price-low") {
    filtered.sort((a, b) => parseFloat(a.price) - parseFloat(b.price));
  } else if (sortBy === "price-high") {
    filtered.sort((a, b) => parseFloat(b.price) - parseFloat(a.price));
  } else if (sortBy === "rating-high") {
    filtered.sort((a, b) => parseFloat(b.rating || 0) - parseFloat(a.rating || 0));
  } else {
    // Default sort by id (newest/reversed)
    filtered.sort((a, b) => b.id - a.id);
  }

  if (filtered.length === 0) {
    container.innerHTML = `<p style="grid-column: 1/-1; text-align: center; padding: 40px; color: var(--text-secondary);">No products match selected filters.</p>`;
    return;
  }

  let htmlString = "";
  // Paginate / limit to 50 items to avoid DOM crashes
  filtered.slice(0, 50).forEach(p => {
    const stockClass = p.stockStatus;
    const stockLabel = p.stockStatus === "in-stock" ? "In Stock" : p.stockStatus === "low-stock" ? "Low Stock" : "Out of Stock";
    const pNameDisplay = p.product_name || p.name || 'Product';
    
    htmlString += `
      <div class="product-card" data-name="${pNameDisplay}">
        <img src="${p.image}" alt="${pNameDisplay}" loading="lazy" />
        <div class="product-card-body">
          <h3>${pNameDisplay}</h3>
          <p>Category: ${p.category}</p>
          <span class="stock ${stockClass}">${stockLabel} (${p.quantity})</span>
          <div class="product-footer">
            ₹${p.price}
            <button onclick="editProductPrice(${p.id})">Edit</button>
          </div>
        </div>
      </div>
    `;
  });
  container.innerHTML = htmlString;
}

function filterProducts() {
  renderProducts();
}

function openAddProductModal() {
  const name = prompt("Enter Product Name:");
  if (!name) return;
  const category = prompt("Enter Category (e.g. Dog Food, Cat Food, Toys, Healthcare):") || "Toys";
  const price = parseFloat(prompt("Enter Price (INR):")) || 99;
  const quantity = parseInt(prompt("Enter Stock Quantity:")) || 100;
  
  let stockStatus = "in-stock";
  if (quantity === 0) stockStatus = "out-stock";
  else if (quantity < 20) stockStatus = "low-stock";

  const newProduct = {
    id: products.length + 1,
    name,
    category,
    price,
    location: "Warehouse A",
    stockStatus,
    quantity,
    image: `https://placehold.co/300x200/EDE8F9/7C5CBF?text=${encodeURIComponent(name)}`
  };

  products.push(newProduct);
  renderProducts();
  alert("Product created successfully!");
}

function editProductPrice(id) {
  const product = products.find(p => p.id === id);
  if (!product) return;
  const newPrice = parseFloat(prompt(`Enter new price for ${product.name}:`, product.price));
  if (newPrice) {
    product.price = newPrice;
    renderProducts();
  }
}

// ── INVENTORY OPERATIONS ──
function renderInventory() {
  const container = document.getElementById("inventoryContainer");
  container.innerHTML = "";

  const query = document.getElementById("inventorySearch").value.toLowerCase();
  const warehouseFilter = document.getElementById("inventoryWarehouse").value;

  // Calculate counters
  const totalSKUs = products.length;
  const healthyCount = products.filter(p => p.stockStatus === "in-stock").length;
  const lowCount = products.filter(p => p.stockStatus === "low-stock").length;
  const outCount = products.filter(p => p.stockStatus === "out-stock").length;

  document.getElementById("inv-total-skus").textContent = totalSKUs;
  document.getElementById("inv-healthy-skus").textContent = healthyCount;
  document.getElementById("inv-low-skus").textContent = lowCount;
  document.getElementById("inv-out-skus").textContent = outCount;

  // Filter
  const filtered = products.filter(p => {
    const pName = (p.product_name || p.name || "").toLowerCase();
    const pLoc = (p.location || "").toLowerCase();
    const matchesSearch = pName.includes(query) || pLoc.includes(query);
    const matchesWarehouse = warehouseFilter === "All" || p.location === warehouseFilter;
    return matchesSearch && matchesWarehouse;
  });

  if (filtered.length === 0) {
    container.innerHTML = `<p style="grid-column: 1/-1; text-align: center; padding: 40px; color: var(--text-secondary);">No inventory items match selected filters.</p>`;
    return;
  }

  let htmlString = "";
  // Paginate / limit to 50 items to avoid DOM crashes
  filtered.slice(0, 50).forEach(p => {
    const stockClass = p.stockStatus;
    const stockLabel = p.stockStatus === "in-stock" ? "Healthy" : p.stockStatus === "low-stock" ? "Low Stock" : "Out of Stock";
    const pNameDisplay = p.product_name || p.name || 'Product';

    htmlString += `
      <div class="inventory-card">
        <img src="${p.image}" alt="${pNameDisplay}" loading="lazy" />
        <div class="inventory-card-body">
          <h3>${pNameDisplay}</h3>
          <p>Location: ${p.location}</p>
          <div class="stock-row">
            <strong>${p.quantity} Units</strong>
            <span class="stock ${stockClass}">${stockLabel}</span>
          </div>
          <button onclick="adjustStockLevel(${p.id})">Refill / Adjust Stock</button>
        </div>
      </div>
    `;
  });
  container.innerHTML = htmlString;
}

function filterInventory() {
  renderInventory();
}

function adjustStockLevel(id) {
  const product = products.find(p => p.id === id);
  if (!product) return;
  const newQty = parseInt(prompt(`Enter new quantity for ${product.name}:`, product.quantity));
  if (isNaN(newQty)) return;

  product.quantity = newQty;
  if (newQty === 0) product.stockStatus = "out-stock";
  else if (newQty < 20) product.stockStatus = "low-stock";
  else product.stockStatus = "in-stock";

  renderInventory();
}

// ── ORDERS OPERATIONS ──
function renderOrders() {
  const container = document.getElementById("ordersContainer");
  container.innerHTML = "";

  const query = document.getElementById("orderSearch").value.toLowerCase();
  const statusFilter = document.getElementById("orderStatusFilter").value;

  // Update stats
  document.getElementById("order-count-total").textContent = orders.length;
  document.getElementById("order-count-pending").textContent = orders.filter(o => o.status === "pending").length;
  document.getElementById("order-count-processing").textContent = orders.filter(o => o.status === "processing").length;
  document.getElementById("order-count-delivered").textContent = orders.filter(o => o.status === "delivered").length;

  const filtered = orders.filter(o => {
    const oCust = (o.customer || "").toLowerCase();
    const oId = (o.id || "").toString().toLowerCase();
    const oItems = (o.items || "").toLowerCase();
    const matchesSearch = oCust.includes(query) || oId.includes(query) || oItems.includes(query);
    const matchesStatus = statusFilter === "All" || o.status === statusFilter;
    return matchesSearch && matchesStatus;
  });

  if (filtered.length === 0) {
    container.innerHTML = `<p style="grid-column: 1/-1; text-align: center; padding: 40px; color: var(--text-secondary);">No orders match filters.</p>`;
    return;
  }

  let htmlString = "";
  // Paginate / limit to 50 items to avoid DOM crashes
  filtered.slice(0, 50).forEach(o => {
    let actionButtons = "";
    if (o.status === "pending") {
      actionButtons = `
        <button class="primary-btn" onclick="updateOrderStatus('${o.id}', 'processing')">Approve</button>
        <button class="secondary-btn" style="color: var(--red); border-color: var(--red);" onclick="updateOrderStatus('${o.id}', 'cancelled')">Cancel</button>
      `;
    } else if (o.status === "processing") {
      actionButtons = `
        <button class="primary-btn" style="background: var(--green);" onclick="updateOrderStatus('${o.id}', 'delivered')">Ship</button>
        <button class="secondary-btn" style="color: var(--red); border-color: var(--red);" onclick="updateOrderStatus('${o.id}', 'cancelled')">Cancel</button>
      `;
    } else {
      actionButtons = `<p style="font-size: .75rem; color: var(--text-secondary);">No actions required.</p>`;
    }

    htmlString += `
      <div class="order-card" style="display: block;">
        <div class="order-header">
          <h3>#${o.id}</h3>
          <span class="badge ${o.status}">${(o.status || "Unknown").charAt(0).toUpperCase() + (o.status || "Unknown").slice(1)}</span>
        </div>
        <p>Customer: <span>${o.customer}</span></p>
        <p>Items: <span>${o.items}</span></p>
        <p>Total: <span>₹${o.amount}</span></p>
        <p>Payment: <span>${o.gateway}</span></p>
        <div class="order-actions">
          ${actionButtons}
        </div>
      </div>
    `;
  });
  container.innerHTML = htmlString;
}

function filterOrders() {
  renderOrders();
}

async function updateOrderStatus(id, newStatus) {
  try {
    const numericId = id.startsWith('PK') ? id.substring(2) : id;
    const res = await fetch(`http://localhost:8000/orders/${numericId}/status`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ status: newStatus })
    });
    if (!res.ok) throw new Error('Failed to update status');
    
    // Refresh dashboard data
    fetchDashboardData();
  } catch(e) {
    console.error('Error updating status:', e);
    alert('Failed to update order status');
  }
}

// ── REVIEWS OPERATIONS ──
function renderReviews() {
  const container = document.getElementById("reviewsContainer");
  container.innerHTML = "";

  const filter = document.getElementById("reviewRatingFilter").value;

  const unansweredReviews = reviews.filter(r => !r.replied).length;
  document.getElementById("review-unanswered-count").textContent = unansweredReviews;

  const filtered = reviews.filter(r => {
    return filter === "All" || r.rating.toString() === filter;
  });

  if (filtered.length === 0) {
    container.innerHTML = `<p style="text-align: center; padding: 40px; color: var(--text-secondary);">No reviews match filters.</p>`;
    return;
  }

  filtered.forEach(r => {
    let stars = "⭐".repeat(r.rating);
    let replyButton = r.replied 
      ? `<p style="font-size: .8rem; color: var(--green); font-weight: 500;">✓ Replied</p>` 
      : `<button class="secondary-btn" onclick="replyToReview(${r.id})">Reply to Feedback</button>`;

    container.innerHTML += `
      <div class="review-card">
        <div class="review-header">
          <h3>${r.product}</h3>
          <span class="rating">${stars}</span>
        </div>
        <div class="customer-name">${r.customer}</div>
        <div class="review-date">Reviewed ${r.date}</div>
        <p class="review-text">"${r.text}"</p>
        <div>${replyButton}</div>
      </div>
    `;
  });
}

function filterReviews() {
  renderReviews();
}

function replyToReview(id) {
  const review = reviews.find(r => r.id === id);
  if (!review) return;
  const replyText = prompt(`Reply to ${review.customer}'s review:`);
  if (replyText) {
    review.replied = true;
    renderReviews();
    alert("Reply sent successfully!");
  }
}

// ── REPORTS OPERATIONS ──
function renderReports() {
  const container = document.getElementById("reportTopProducts");
  container.innerHTML = "";

  // Mock list of best sellers
  const bestSellers = [
    { rank: 1, name: "Premium Dog Food", sales: 480, revenue: 287520 },
    { rank: 2, name: "Pet Shampoo", sales: 320, revenue: 79680 },
    { rank: 3, name: "Cat Treats", sales: 210, revenue: 31290 }
  ];

  bestSellers.forEach(item => {
    container.innerHTML += `
      <li>
        <div class="rank-info">
          <span class="rank-num">${item.rank}</span>
          <span class="product-rank">${item.name}</span>
        </div>
        <span class="product-sales">${item.sales} sales (₹${item.revenue.toLocaleString()})</span>
      </li>
    `;
  });
}

// ── SETTINGS OPERATIONS ──
function renderSettings() {
  renderDeliveryZones();
}

function switchSettingsTab(tabBtn, panelId) {
  // Remove active state from tabs
  document.querySelectorAll(".settings-tab").forEach(tab => tab.classList.remove("active"));
  // Add active state to clicked tab
  tabBtn.classList.add("active");

  // Hide all panels
  document.querySelectorAll(".settings-panel").forEach(panel => panel.classList.remove("active"));
  // Show target panel
  document.getElementById("settings-" + panelId).classList.add("active");
}

function renderDeliveryZones() {
  const container = document.getElementById("deliveryZoneContainer");
  container.innerHTML = "";

  deliveryZones.forEach((zone, index) => {
    container.innerHTML += `
      <div class="zone-tag">
        ${zone}
        <button onclick="deleteDeliveryZone(${index})">×</button>
      </div>
    `;
  });
}

function addDeliveryZone() {
  const input = document.getElementById("newZoneInput");
  const zoneName = input.value.trim();
  if (!zoneName) return;

  deliveryZones.push(zoneName);
  input.value = "";
  renderDeliveryZones();
}

function deleteDeliveryZone(index) {
  deliveryZones.splice(index, 1);
  renderDeliveryZones();
}

function saveSettings(message) {
  alert("💾 " + message);
}

function logout() {
  window.location.href = 'index.html#login';
}

// Handle URL role parameter to dynamically adjust profile
const urlParams = new URLSearchParams(window.location.search);
const roleParam = urlParams.get('role') || 'manager'; // Default to manager

function initUserProfile() {
  const avatarEl = document.querySelector(".header-right .avatar");
  const nameEl = document.querySelector(".header-right .user-profile h4");
  const roleEl = document.querySelector(".header-right .user-profile span");
  const welcomeTitle = document.querySelector(".welcome-card h1");
  const logoText = document.querySelector(".sidebar .logo span");

  if (roleParam === 'admin') {
    if (avatarEl) avatarEl.textContent = "AD";
    if (nameEl) nameEl.textContent = "Admin User";
    if (roleEl) roleEl.textContent = "System Admin";
    if (welcomeTitle) welcomeTitle.textContent = "Good Morning, Admin 👋";
    if (logoText) logoText.textContent = "PawKart Admin";
  } else {
    if (avatarEl) avatarEl.textContent = "AK";
    if (nameEl) nameEl.textContent = "Akanksha";
    if (roleEl) roleEl.textContent = "Store Manager";
    if (welcomeTitle) welcomeTitle.textContent = "Good Morning, Akanksha 👋";
    if (logoText) logoText.textContent = "PawKart Manager";
  }
}

// Initialise Application Page
switchPage("dashboard");
initUserProfile();
fetchDashboardData();

function goBack() {
  if (typeof navHistory !== 'undefined' && navHistory.length > 0) {
    const prevPage = navHistory.pop();
    switchPage(prevPage, false);
  } else {
    // Default fallback
    if (document.getElementById('page-dashboard')) switchPage('dashboard', false);
    else window.location.href = 'index.html';
  }
}
