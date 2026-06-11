// Global State
let stores = [];
let products = [];
let orders = [];
let complaints = [];
let users = [];
let activePage = "overview";

async function fetchAdminData() {
  try {
    const [sRes, pRes, oRes, cRes, uRes] = await Promise.all([
      fetch('http://localhost:8000/stores').catch(() => null),
      fetch('http://localhost:8000/products').catch(() => null),
      fetch('http://localhost:8000/orders').catch(() => null),
      fetch('http://localhost:8000/complaints').catch(() => null),
      fetch('http://localhost:8000/users').catch(() => null)
    ]);
    
    if (sRes && sRes.ok) stores = await sRes.json();
    if (pRes && pRes.ok) products = await pRes.json();
    if (oRes && oRes.ok) orders = await oRes.json();
    if (cRes && cRes.ok) complaints = await cRes.json();
    if (uRes && uRes.ok) users = await uRes.json();
    
    // Refresh current page if needed
    if (activePage === "overview") renderOverview();
    else if (activePage === "stores") renderStores();
    else if (activePage === "products") renderProducts();
    else if (activePage === "orders") renderOrders();
    else if (activePage === "complaints") renderComplaints();
    else if (activePage === "users") renderUsers();
    
  } catch (e) {
    console.error("Failed to fetch admin data", e);
  }
}

async function uploadCatalogCSV(event) {
  const file = event.target.files[0];
  if (!file) return;

  const formData = new FormData();
  formData.append("file", file);

  try {
    const res = await fetch("http://localhost:8000/admin/upload-catalog", {
      method: "POST",
      body: formData
    });
    const result = await res.json();
    if (res.ok) {
      alert("Success: " + result.message);
      fetchAdminData(); 
    } else {
      alert("Error: " + result.detail);
    }
  } catch (e) {
    console.error(e);
    alert("Failed to upload CSV.");
  }
}

// ── NAVIGATION ──
const pageTitles = {
  overview: "Platform Overview <span>Platform Admin</span>",
  stores: "Managed Retail Stores <span>Store Network</span>",
  warehouses: "Managed Warehouses <span>Logistics Hubs</span>",
  products: "Products SKU Directory <span>Inventory Base</span>",
  orders: "Global Platform Orders <span>Transaction Operations</span>",
  complaints: "Disputes &amp; Support Tickets <span>Disputes Management</span>",
  users: "Platform User Directory <span>Credentials Directory</span>",
  settings: "System Configuration Panel <span>System Settings</span>",
  analysis: "Business Analysis <span>Intelligence Dashboard</span>",
  forecast: "AI Forecasting <span>Predictive Analytics</span>"
};

let navHistory = [];
function switchPage(name, addToHistory = true) {
  if (addToHistory) {
    const activePage = document.querySelector('.page.active');
    if (activePage) {
      const activeId = activePage.id.replace('page-', '');
      if (activeId !== name) {
        navHistory.push(activeId);
      }
    }
  }

  // Hide all page sections
  document.querySelectorAll(".page").forEach(p => p.classList.remove("active"));
  // Show target page
  const target = document.getElementById("page-" + name);
  if (target) target.classList.add("active");

  // Update topbar title
  document.getElementById("pageTitle").innerHTML = pageTitles[name] || "Platform Admin";

  // Update active sidebar nav items
  document.querySelectorAll(".sidebar-nav .nav-item").forEach(item => {
    item.classList.toggle("active", item.getAttribute("data-page") === name);
  });

  activePage = name;
  window.scrollTo({ top: 0, behavior: "smooth" });

  // Page specific render triggers
  if (name === "overview") renderOverview();
  else if (name === "stores") renderStores();
  else if (name === "products") renderProducts();
  else if (name === "orders") renderOrders();
  else if (name === "complaints") renderComplaints();
  else if (name === "users") renderUsers();
  else if (name === "analysis") renderAnalysis();
  else if (name === "forecast") renderForecast();
}

function goBack() {
  if (navHistory.length > 0) {
    const prevPage = navHistory.pop();
    switchPage(prevPage, false);
  } else {
    // Default fallback
    if (document.getElementById('page-overview')) switchPage('overview', false);
    else window.location.href = 'index.html';
  }
}

// Bind Navigation Click Events
document.querySelectorAll(".sidebar-nav .nav-item").forEach(item => {
  item.addEventListener("click", () => {
    switchPage(item.getAttribute("data-page"));
  });
});

function logout() {
  window.location.href = "index.html#login";
}

function handleStoreSelection() {
  const selector = document.getElementById("adminStoreSelector");
  if (!selector) return;
  const value = selector.value;
  
  const tbody = document.getElementById("multiStoreComparisonBody");
  if (!tbody) return;
  
  const rows = tbody.querySelectorAll("tr");
  rows.forEach(row => {
    // Determine which store this row belongs to based on the first column text
    const text = row.cells[0].innerText.toLowerCase();
    
    if (value === "all") {
      row.style.display = "";
    } else {
      // e.g. "store 1" from "store1" value
      const storeNum = value.replace("store", "");
      if (text.includes("store " + storeNum)) {
        row.style.display = "";
      } else {
        row.style.display = "none";
      }
    }
  });
}

// ── OVERVIEW PAGE ──
function renderOverview() {
  // Update Counters
  document.getElementById("overview-pending-approvals").textContent = orders.filter(o => o.status === "pending").length;
  document.getElementById("overview-disputes-count").textContent = complaints.filter(c => c.status !== "resolved").length;

  // (Performance ranking block was replaced by the static 5-store comparison table)
  const perfContainer = document.getElementById("overviewStoresPerformance");
  if (perfContainer) {
    perfContainer.innerHTML = "";
    const ranked = [...stores].sort((a, b) => b.id - a.id);
    ranked.forEach((store, idx) => {
      const percentage = 50 + (idx * 5); // mock percentage
      perfContainer.innerHTML += `
        <div class="store-row">
          <div class="sr-left">
            <span class="sr-rank">${idx + 1}</span>
            <span>${store.name}</span>
          </div>
          <div class="bar-bg">
            <div class="bar-fill" style="width: ${percentage}%;"></div>
          </div>
          <strong>₹${store.min_order_amount || 0}</strong>
        </div>
      `;
    });
  }

  // Render Complaints Preview
  const compContainer = document.getElementById("overviewComplaintsPreview");
  compContainer.innerHTML = "";

  complaints.slice(0, 3).forEach(c => {
    const badgeClass = "medium";
    compContainer.innerHTML += `
      <div class="complaint-card">
        <div>
          <h4>#${c.id}</h4>
          <p>${c.customer_email} • ${c.issue_description}</p>
        </div>
        <span class="badge ${badgeClass}">MEDIUM</span>
      </div>
    `;
  });
}

// ── STORES PAGE ──
function renderStores() {
  const container = document.getElementById("storesContainer");
  container.innerHTML = "";

  const query = document.getElementById("storeSearch").value.toLowerCase();
  const locationFilter = document.getElementById("storeFilterLocation").value;
  const statusFilter = document.getElementById("storeFilterStatus").value;

  const filtered = stores.filter(s => {
    const matchesSearch = s.name.toLowerCase().includes(query) || s.owner_name.toLowerCase().includes(query);
    const matchesLocation = locationFilter === "All" || (s.address && s.address.includes(locationFilter));
    const matchesStatus = statusFilter === "All" || (s.is_open ? "active" : "inactive") === statusFilter;
    return matchesSearch && matchesLocation && matchesStatus;
  });

  if (filtered.length === 0) {
    container.innerHTML = `<p style="grid-column: 1/-1; text-align: center; padding: 40px; color: var(--text-secondary);">No stores match selected filters.</p>`;
    return;
  }

  filtered.forEach(s => {
    const statusClass = s.is_open ? "active" : "inactive";
    const statusLabel = s.is_open ? "Active" : "Inactive";
    container.innerHTML += `
      <div class="store-card">
        <h3>${s.name}</h3>
        <p><i class="ti ti-map-pin"></i> ${s.address || 'Unknown'}</p>
        <p><i class="ti ti-user"></i> ${s.owner_name}</p>
        <p><i class="ti ti-coin"></i> Min Order ₹${s.min_order_amount || 0}</p>
        <div style="margin-top: 8px;">
          <span class="badge ${statusClass}">${statusLabel}</span>
        </div>
        <div class="store-actions">
          <button class="btn-secondary" onclick="toggleStoreStatus(${s.id})">Toggle Status</button>
        </div>
      </div>
    `;
  });
}

function filterStores() {
  renderStores();
}

function openAddStoreModal() {
  const name = prompt("Enter Store Name:");
  if (!name) return;
  const location = prompt("Enter Location (e.g. Bangalore, Mumbai, Delhi):") || "Bangalore";
  const manager = prompt("Enter Store Manager Name:") || "N/A";

  stores.push({
    id: stores.length + 1,
    name,
    address: location,
    owner_name: manager,
    is_open: true,
    min_order_amount: 0
  });

  renderStores();
  alert("Store registered successfully!");
}

function toggleStoreStatus(id) {
  const store = stores.find(s => s.id === id);
  if (store) {
    store.is_open = !store.is_open;
    renderStores();
  }
}

// ── WAREHOUSES PAGE ──
function renderWarehouses() {
  const container = document.getElementById("warehousesContainer");
  container.innerHTML = "";

  const query = document.getElementById("warehouseSearch").value.toLowerCase();

  const filtered = warehouses.filter(w => {
    return w.name.toLowerCase().includes(query) || w.location.toLowerCase().includes(query);
  });

  if (filtered.length === 0) {
    container.innerHTML = `<p style="grid-column: 1/-1; text-align: center; padding: 40px; color: var(--text-secondary);">No warehouses match selected filters.</p>`;
    return;
  }

  filtered.forEach(w => {
    let statusClass = "active";
    let statusLabel = "Active";
    if (w.status === "critical") {
      statusClass = "critical";
      statusLabel = "Critical Capacity";
    } else if (w.status === "inactive") {
      statusClass = "inactive";
      statusLabel = "Inactive";
    }

    container.innerHTML += `
      <div class="store-card">
        <h3>${w.name}</h3>
        <p><i class="ti ti-map-pin"></i> ${w.location}</p>
        <p><i class="ti ti-package"></i> Batches: ${w.batches}</p>
        <p><i class="ti ti-chart-pie"></i> Capacity: ${w.capacity}% Used</p>
        <div style="margin-top: 8px;">
          <span class="badge ${statusClass}">${statusLabel}</span>
        </div>
        <div class="store-actions" style="margin-top: 12px;">
          <button class="btn-primary" onclick="allocateBatchesPrompt(${w.id})">Allocate Batches</button>
        </div>
      </div>
    `;
  });
}

function filterWarehouses() {
  renderWarehouses();
}

function openAddWarehouseModal() {
  const name = prompt("Enter Warehouse Hub Name:");
  if (!name) return;
  const location = prompt("Enter Regional Location:") || "Bangalore East";

  warehouses.push({
    id: warehouses.length + 1,
    name,
    location,
    capacity: 0,
    status: "active",
    batches: 0
  });

  renderWarehouses();
  alert("Warehouse hub created!");
}

function allocateBatchesPrompt(id) {
  const hub = warehouses.find(w => w.id === id);
  if (!hub) return;
  const qty = parseInt(prompt(`Allocate batch units to ${hub.name}:`, 20));
  if (isNaN(qty)) return;

  hub.batches += qty;
  hub.capacity = Math.min(100, hub.capacity + Math.round(qty / 5));
  if (hub.capacity >= 95) hub.status = "critical";
  else if (hub.capacity > 0) hub.status = "active";

  renderWarehouses();
  alert("Batches allocated successfully!");
}

// ── PRODUCTS OPERATIONS ──
function renderProducts() {
  const container = document.getElementById("productsContainer");
  container.innerHTML = "";

  const query = document.getElementById("productSearch").value.toLowerCase();
  const categoryFilter = document.getElementById("productFilterCategory").value;

  const filtered = products.filter(p => {
    const pName = (p.product_name || p.name || "").toLowerCase();
    const matchesSearch = pName.includes(query);
    const matchesCategory = categoryFilter === "All" || p.category === categoryFilter;
    return matchesSearch && matchesCategory;
  });

  if (filtered.length === 0) {
    container.innerHTML = `<p style="grid-column: 1/-1; text-align: center; padding: 40px; color: var(--text-secondary);">No products match catalog filters.</p>`;
    return;
  }

  let htmlString = "";
  // Paginate / limit to 50 items to avoid DOM crashes
  filtered.slice(0, 50).forEach(p => {
    let badgeClass = "in-stock";
    let badgeLabel = `In Stock (${p.quantity || 10})`;
    if (p.stockStatus === "low-stock" || p.quantity < 20) {
      badgeClass = "low-stock";
      badgeLabel = `Low Stock (${p.quantity || 0})`;
    } else if (p.stockStatus === "out-stock" || p.quantity === 0) {
      badgeClass = "out-stock";
      badgeLabel = "Out of Stock";
    }

    const pNameDisplay = p.product_name || p.name || 'Product';

    htmlString += `
      <div class="product-card">
        <div class="product-img"><i class="ti ti-package" style="color: var(--accent); font-size: 3rem;"></i></div>
        <div class="product-body">
          <h3>${pNameDisplay}</h3>
          <div class="product-meta"><i class="ti ti-category"></i> ${p.category}</div>
          <div class="product-price">₹${p.price}</div>
          <div><span class="badge ${badgeClass}">${badgeLabel}</span></div>
          <div class="product-actions">
            <button class="btn-secondary" style="width: 100%;" onclick="editProductPrice(${p.id})">Modify price</button>
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
  const name = prompt("Enter SKU Name:");
  if (!name) return;
  const category = prompt("Category (Dog Food, Cat Food, Toys, Healthcare):") || "Toys";
  const price = parseFloat(prompt("Base Price (INR):")) || 199;
  const quantity = parseInt(prompt("Initial Stock Units:")) || 100;

  let status = "in-stock";
  if (quantity === 0) status = "out-stock";
  else if (quantity < 20) status = "low-stock";

  products.push({
    id: products.length + 1,
    name,
    category,
    price,
    quantity,
    status
  });

  renderProducts();
  alert("SKU added to global catalog!");
}

function editProductPrice(id) {
  const product = products.find(p => p.id === id);
  if (!product) return;
  const newPrice = parseFloat(prompt(`Edit base price for ${product.name}:`, product.price));
  if (newPrice) {
    product.price = newPrice;
    renderProducts();
  }
}

// ── ORDERS OPERATIONS ──
function renderOrders() {
  const container = document.getElementById("ordersContainer");
  container.innerHTML = "";

  const query = document.getElementById("orderSearch").value.toLowerCase();
  const statusFilter = document.getElementById("orderFilterStatus").value;

  const filtered = orders.filter(o => {
    const matchesSearch = o.customer.toLowerCase().includes(query) || o.id.toLowerCase().includes(query) || o.store.toLowerCase().includes(query);
    const matchesStatus = statusFilter === "All" || o.status === statusFilter;
    return matchesSearch && matchesStatus;
  });

  if (filtered.length === 0) {
    container.innerHTML = `<p style="text-align: center; padding: 40px; color: var(--text-secondary);">No orders found.</p>`;
    return;
  }

  filtered.forEach(o => {
    let actionButtons = "";
    if (o.status === "pending") {
      actionButtons = `
        <button class="btn-primary" style="padding: 4px 8px; font-size: 11px;" onclick="updateOrderStatus('${o.id}', 'processing')">Approve</button>
        <button class="btn-danger" style="padding: 4px 8px; font-size: 11px;" onclick="updateOrderStatus('${o.id}', 'cancelled')">Cancel</button>
      `;
    } else if (o.status === "processing") {
      actionButtons = `
        <button class="btn-primary" style="background: var(--green); padding: 4px 8px; font-size: 11px;" onclick="updateOrderStatus('${o.id}', 'delivered')">Ship</button>
        <button class="btn-danger" style="padding: 4px 8px; font-size: 11px;" onclick="updateOrderStatus('${o.id}', 'cancelled')">Cancel</button>
      `;
    } else {
      actionButtons = `<span style="font-size: 11px; color: var(--text-secondary);">Archived</span>`;
    }

    container.innerHTML += `
      <div class="ot-row">
        <span class="ct-cell id">#${o.id}</span>
        <span class="ct-cell customer">${o.customer}</span>
        <span class="ct-cell">${o.store}</span>
        <span class="ct-cell">${o.items}</span>
        <span class="ct-cell amount">₹${o.amount}</span>
        <span class="ct-cell">
          <span class="badge ${o.status}">${o.status.charAt(0).toUpperCase() + o.status.slice(1)}</span>
        </span>
        <div class="ot-actions">
          ${actionButtons}
        </div>
      </div>
    `;
  });
}

function filterOrders() {
  renderOrders();
}

function updateOrderStatus(id, newStatus) {
  const order = orders.find(o => o.id === id);
  if (order) {
    order.status = newStatus;
    renderOrders();
  }
}

// ── COMPLAINTS OPERATIONS ──
function renderComplaints() {
  const container = document.getElementById("complaintsContainer");
  container.innerHTML = "";

  const query = document.getElementById("complaintSearch").value.toLowerCase();
  const priorityFilter = document.getElementById("complaintFilterPriority").value;

  const filtered = complaints.filter(c => {
    const matchesSearch = c.subject.toLowerCase().includes(query) || c.customer.toLowerCase().includes(query);
    const matchesPriority = priorityFilter === "All" || c.priority === priorityFilter;
    return matchesSearch && matchesPriority;
  });

  if (filtered.length === 0) {
    container.innerHTML = `<p style="text-align: center; padding: 40px; color: var(--text-secondary);">No active complaints.</p>`;
    return;
  }

  filtered.forEach(c => {
    const priorityClass = c.priority === "critical" ? "critical" : c.priority === "medium" ? "medium" : "low";
    const statusClass = c.status === "open" ? "open" : c.status === "progress" ? "progress" : "resolved";
    
    let actionButtons = "";
    if (c.status !== "resolved") {
      actionButtons = `
        <button class="btn-primary" style="padding: 4px 8px; font-size: 11px;" onclick="resolveComplaint('${c.id}')">Resolve</button>
      `;
    } else {
      actionButtons = `<span style="font-size: 11px; color: var(--text-secondary);">Resolved</span>`;
    }

    container.innerHTML += `
      <div class="ct-row">
        <span class="ct-cell id">${c.id}</span>
        <span class="ct-cell title">${c.issue_description}</span>
        <span class="ct-cell">${c.customer_email}</span>
        <span class="ct-cell">
          <span class="badge ${priorityClass}">MEDIUM</span>
        </span>
        <span class="ct-cell">Order #${c.order_id || 'N/A'}</span>
        <span class="ct-cell">
          <span class="badge ${statusClass}">${c.status === 'progress' ? 'In Progress' : c.status.charAt(0).toUpperCase() + c.status.slice(1)}</span>
        </span>
        <div class="ct-actions">
          ${actionButtons}
        </div>
      </div>
    `;
  });
}

function filterComplaints() {
  renderComplaints();
}

function resolveComplaint(id) {
  const ticket = complaints.find(c => c.id === id);
  if (ticket) {
    ticket.status = "resolved";
    renderComplaints();
    alert(`Complaint ${id} set as Resolved!`);
  }
}

// ── USERS OPERATIONS ──
function renderUsers() {
  const container = document.getElementById("usersContainer");
  container.innerHTML = "";

  const query = document.getElementById("userSearch").value.toLowerCase();
  const roleFilter = document.getElementById("userFilterRole").value;

  const filtered = users.filter(u => {
    const matchesSearch = u.name.toLowerCase().includes(query) || u.email.toLowerCase().includes(query);
    const matchesRole = roleFilter === "All" || u.role === roleFilter;
    return matchesSearch && matchesRole;
  });

  if (filtered.length === 0) {
    container.innerHTML = `<p style="text-align: center; padding: 40px; color: var(--text-secondary);">No users found.</p>`;
    return;
  }

  filtered.forEach(u => {
    const roleLabel = u.role === "admin" ? "Admin" : u.role === "owner" ? "Store Manager" : "Customer";
    const statusClass = "active";

    container.innerHTML += `
      <div class="ut-row">
        <div class="ut-avatar">${u.email.charAt(0).toUpperCase()}</div>
        <span class="ut-cell name">${u.email}</span>
        <span class="ut-cell">${u.email}</span>
        <span class="ut-cell">Store ${u.store_id || 'N/A'}</span>
        <span class="ut-cell">
          <span class="badge ${u.role}">${roleLabel}</span>
        </span>
        <span class="ut-cell">
          <span class="badge ${statusClass}">Active</span>
        </span>
        <div class="ut-actions">
          <button class="btn-secondary" style="padding: 4px 8px; font-size: 11px;" onclick="toggleUserStatus('${u.email}')">Toggle Status</button>
        </div>
      </div>
    `;
  });
}

function filterUsers() {
  renderUsers();
}

function toggleUserStatus(email) {
  const user = users.find(u => u.email === email);
  if (user) {
    user.status = user.status === "active" ? "inactive" : "active";
    renderUsers();
  }
}

// ── SETTINGS OPERATIONS ──
function switchSettingsTab(tabBtn, panelId) {
  // Toggle active tab class
  document.querySelectorAll(".settings-sidebar button").forEach(btn => btn.classList.remove("active"));
  tabBtn.classList.add("active");

  // Toggle active panel visibility
  document.querySelectorAll(".settings-panel").forEach(panel => panel.style.display = "none");
  document.getElementById("settings-" + panelId).style.display = "block";
}

// ── ANALYSIS & CHARTS OPERATIONS ──
function renderAnalysis() {
  const container = document.getElementById("analysisContainer");
  container.innerHTML = `
    <div class="admin-stats">
      <div class="stat-card">
        <div class="s-icon"><i class="ti ti-chart-arrows-vertical"></i></div>
        <h3>89.4%</h3>
        <p>Customer Retention</p>
        <div class="trend up"><i class="ti ti-trending-up"></i> +2.1% YoY</div>
      </div>
      <div class="stat-card">
        <div class="s-icon" style="color: var(--blue); background: var(--blue-soft);"><i class="ti ti-receipt-2"></i></div>
        <h3>₹2,450</h3>
        <p>Avg Order Value</p>
        <div class="trend up"><i class="ti ti-trending-up"></i> +450 INR</div>
      </div>
      <div class="stat-card">
        <div class="s-icon" style="color: var(--yellow); background: var(--yellow-soft);"><i class="ti ti-users"></i></div>
        <h3>24.2K</h3>
        <p>Monthly Active Users</p>
        <div class="trend up"><i class="ti ti-trending-up"></i> +1.2K MoM</div>
      </div>
    </div>

    <div class="two-col">
      <div class="chart-card">
        <h3><i class="ti ti-category"></i> Revenue by Category (Q2)</h3>
        
        <div class="chart-bar-group">
          <div class="chart-label"><span>Dog Food</span> <strong>₹6.2L</strong></div>
          <div class="chart-track"><div class="chart-fill" style="width: 75%;"></div></div>
        </div>
        
        <div class="chart-bar-group">
          <div class="chart-label"><span>Cat Food</span> <strong>₹3.4L</strong></div>
          <div class="chart-track"><div class="chart-fill" style="width: 45%; background: linear-gradient(90deg, #3B82F6, #2563EB);"></div></div>
        </div>
        
        <div class="chart-bar-group">
          <div class="chart-label"><span>Toys</span> <strong>₹1.8L</strong></div>
          <div class="chart-track"><div class="chart-fill" style="width: 25%; background: linear-gradient(90deg, #F59E0B, #D97706);"></div></div>
        </div>
        
        <div class="chart-bar-group">
          <div class="chart-label"><span>Healthcare</span> <strong>₹0.9L</strong></div>
          <div class="chart-track"><div class="chart-fill" style="width: 15%; background: linear-gradient(90deg, #10B981, #059669);"></div></div>
        </div>
      </div>

      <div class="chart-card">
        <h3><i class="ti ti-map-2"></i> Top Performing Regions</h3>
        <div class="ct-row" style="grid-template-columns: 1fr 100px;">
          <span class="ct-cell title" style="padding-left:0;">Bangalore (Central)</span>
          <span class="ct-cell amount text-success">+14.2%</span>
        </div>
        <div class="ct-row" style="grid-template-columns: 1fr 100px;">
          <span class="ct-cell title" style="padding-left:0;">Mumbai (West)</span>
          <span class="ct-cell amount text-success">+9.8%</span>
        </div>
        <div class="ct-row" style="grid-template-columns: 1fr 100px;">
          <span class="ct-cell title" style="padding-left:0;">Delhi (NCR)</span>
          <span class="ct-cell amount text-success">+6.5%</span>
        </div>
        <div class="ct-row" style="grid-template-columns: 1fr 100px;">
          <span class="ct-cell title" style="padding-left:0;">Chennai (South)</span>
          <span class="ct-cell amount text-danger">-2.1%</span>
        </div>
      </div>
    </div>
  `;
}

// ── AI FORECASTING & INSIGHTS OPERATIONS ──
async function renderForecast() {
  const container = document.getElementById("forecastContainer");
  container.innerHTML = `
    <div class="ai-banner" style="background: linear-gradient(135deg, #1e1b4b 0%, #312e81 100%); padding: 30px; border-radius: 12px; color: white; margin-bottom: 30px;">
      <div style="display: flex; justify-content: space-between; align-items: center;">
        <div class="ai-banner-content">
          <h2 style="color: white; margin-bottom: 10px; font-size: 1.5rem;"><i class="ti ti-brain"></i> AI Platform Intelligence</h2>
          <p style="color: #cbd5e1; max-width: 600px;">Our CatBoost and Temporal Fusion Transformer models have analyzed the latest transaction data to predict customer behavior and network-wide demand.</p>
        </div>
        <button class="btn-primary" style="background: rgba(255,255,255,0.1); border: 1px solid rgba(255,255,255,0.2); color: white;" onclick="renderForecast()">
          <i class="ti ti-refresh"></i> Run AI Sync
        </button>
      </div>
    </div>
    
    <div class="two-col">
      <div class="ai-card" style="background: white; border-radius: 12px; padding: 24px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1);">
        <h3 style="margin-bottom: 20px; color: #1e293b; display: flex; align-items: center; gap: 8px;">
          <i class="ti ti-users" style="color: #6366f1;"></i> High-Probability Customers (Next 7 Days)
        </h3>
        <div id="ai-customers-grid">
          <p style="color: #64748b;"><i class="ti ti-loader"></i> Querying CatBoost Model...</p>
        </div>
      </div>
      
      <div class="ai-card" style="background: white; border-radius: 12px; padding: 24px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1);">
        <h3 style="margin-bottom: 20px; color: #1e293b; display: flex; align-items: center; gap: 8px;">
          <i class="ti ti-chart-bar" style="color: #ec4899;"></i> Network Demand Forecast (TFT)
        </h3>
        <select id="network-forecast-select" onchange="loadNetworkForecast()" style="width: 100%; padding: 10px; margin-bottom: 20px; border-radius: 8px; border: 1px solid #e2e8f0;">
          <option value="1">Dog Food</option>
        </select>
        <div id="ai-demand-grid" style="min-height: 150px;">
          <p style="color: #64748b;"><i class="ti ti-loader"></i> Querying TFT Engine...</p>
        </div>
      </div>
    </div>
  `;

  // 1. Fetch CatBoost Customers
  const custGrid = document.getElementById("ai-customers-grid");
  try {
    const cRes = await fetch('http://localhost:8000/ai/customer-purchase/high-probability');
    if (cRes.ok) {
      const customers = await cRes.json();
      custGrid.innerHTML = "";
      customers.forEach(c => {
        custGrid.innerHTML += `
          <div style="border-bottom: 1px solid #f1f5f9; padding: 12px 0; display: flex; justify-content: space-between; align-items: center;">
            <div>
              <h4 style="margin: 0; color: #334155;">Customer ID: #${c.customer_id}</h4>
              <p style="margin: 4px 0 0 0; font-size: 0.8rem; color: #64748b;">Predicted to buy: <strong>${c.predicted_category || 'General'}</strong></p>
            </div>
            <div style="text-align: right;">
              <span style="background: #dcfce7; color: #166534; padding: 4px 8px; border-radius: 12px; font-size: 0.8rem; font-weight: 600;">${Math.round(c.purchase_probability * 100)}% Probability</span>
            </div>
          </div>
        `;
      });
    } else {
      custGrid.innerHTML = '<p style="color: #ef4444;">Failed to load customer predictions.</p>';
    }
  } catch(e) {
    custGrid.innerHTML = '<p style="color: #ef4444;">API Connection Error.</p>';
  }

  // Populate Select for Demand
  const select = document.getElementById("network-forecast-select");
  if (products.length > 0) {
    select.innerHTML = '';
    products.slice(0, 10).forEach(p => {
      const pNameDisplay = p.product_name || p.name || 'Product';
      select.innerHTML += `<option value="${p.id}">${pNameDisplay}</option>`;
    });
  }
  loadNetworkForecast();
}

async function loadNetworkForecast() {
  const select = document.getElementById("network-forecast-select");
  const grid = document.getElementById("ai-demand-grid");
  if (!select || !grid) return;
  
  const productId = select.value;
  grid.innerHTML = '<p style="color: #64748b;"><i class="ti ti-loader"></i> Loading...</p>';
  
  try {
    const res = await fetch(`http://localhost:8000/ai/forecast/product/${productId}`);
    if (res.ok) {
      const data = await res.json();
      grid.innerHTML = `<div style="display: flex; gap: 10px; overflow-x: auto; padding-top: 10px;"></div>`;
      const innerGrid = grid.querySelector('div');
      
      const forecastArray = [
        { predicted_demand: data.forecast_1_day, label: "Next 24h" },
        { predicted_demand: data.forecast_7_days, label: "Next 7d" },
        { predicted_demand: data.forecast_30_days, label: "Next 30d" }
      ];
      
      const maxDemand = Math.max(...forecastArray.map(d => d.predicted_demand));
      forecastArray.forEach(d => {
        const heightPct = Math.max((d.predicted_demand / maxDemand) * 100, 10);
        innerGrid.innerHTML += `
          <div style="display: flex; flex-direction: column; align-items: center; min-width: 60px;">
            <div style="height: 120px; width: 36px; background: #f1f5f9; border-radius: 4px; display: flex; align-items: flex-end;">
              <div style="width: 100%; height: ${heightPct}%; background: linear-gradient(180deg, #ec4899 0%, #be185d 100%); border-radius: 0 0 4px 4px;"></div>
            </div>
            <span style="font-weight: 700; color: #1e293b; margin-top: 8px; font-size: 0.85rem;">${d.predicted_demand}</span>
            <span style="font-size: 0.7rem; color: #64748b; margin-top: 2px;">${d.label}</span>
          </div>
        `;
      });
    } else {
      grid.innerHTML = '<p style="color: #ef4444;">Failed to load forecast.</p>';
    }
  } catch(e) {
    grid.innerHTML = '<p style="color: #ef4444;">API Connection Error.</p>';
  }
}

// Initialise Dashboard Page
fetchAdminData();
switchPage("overview");
