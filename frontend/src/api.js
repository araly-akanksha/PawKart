// ============================================================
// PAWKART API CLIENT
// ============================================================

const API_BASE = 'http://localhost:8000';

async function fetchJSON(url) {
  const res = await fetch(`${API_BASE}${url}`);
  if (!res.ok) throw new Error(`API error: ${res.status}`);
  return res.json();
}

async function postJSON(url, data) {
  const res = await fetch(`${API_BASE}${url}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });
  if (!res.ok) throw new Error(`API error: ${res.status}`);
  return res.json();
}

async function putJSON(url, data) {
  const res = await fetch(`${API_BASE}${url}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });
  if (!res.ok) throw new Error(`API error: ${res.status}`);
  return res.json();
}

async function patchJSON(url, data) {
  const res = await fetch(`${API_BASE}${url}`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });
  if (!res.ok) throw new Error(`API error: ${res.status}`);
  return res.json();
}

async function deleteJSON(url) {
  const res = await fetch(`${API_BASE}${url}`, { method: 'DELETE' });
  if (!res.ok && res.status !== 204) throw new Error(`API error: ${res.status}`);
  return res.status === 204 ? null : res.json();
}

// ── Products ──────────────────────────────────────────────
export const fetchProducts = (category) =>
  fetchJSON(category ? `/products?category=${category}` : '/products');
export const fetchProduct = (id) => fetchJSON(`/products/${id}`);
export const createProduct = (data) => postJSON('/products', data);
export const updateProduct = (id, data) => putJSON(`/products/${id}`, data);
export const deleteProduct = (id) => deleteJSON(`/products/${id}`);
export const fetchCategories = () => fetchJSON('/products/categories');
export const toggleAvailability = (id) => patchJSON(`/products/${id}/availability`, {});

// ── Inventory ─────────────────────────────────────────────
export const fetchInventory = () => fetchJSON('/inventory');
export const addInventory = (data) => postJSON('/inventory', data);
export const updateInventory = (productId, data) => patchJSON(`/inventory/${productId}`, data);
export const updateStock = (data) => putJSON('/inventory/update-stock', data);
export const fetchLowStockAlerts = () => fetchJSON('/inventory/low-stock');

// ── RFID ──────────────────────────────────────────────────
export const rfidScan = (data) => postJSON('/rfid-scan', data);
export const fetchRFIDEvents = (params = '') => fetchJSON(`/rfid-events${params ? '?' + params : ''}`);
export const fetchLatestRFIDEvents = (count = 20) => fetchJSON(`/rfid-events/latest?count=${count}`);
export const fetchRFIDStats = () => fetchJSON('/rfid-events/stats');

// ── Orders ────────────────────────────────────────────────
export const createOrder = (data) => postJSON('/orders', data);
export const fetchOrders = (status) =>
  fetchJSON(status && status !== 'all' ? `/orders?status=${status}` : '/orders');
export const fetchOrderSummary = () => fetchJSON('/orders/summary');
export const fetchOrder = (id) => fetchJSON(`/orders/${id}`);
export const updateOrderStatus = (id, status) =>
  patchJSON(`/orders/${id}/status`, { status });

// ── Store ─────────────────────────────────────────────────
export const fetchStore = () => fetchJSON('/store');
export const updateStore = (data) => patchJSON('/store', data);

// ── Analytics ─────────────────────────────────────────────
export const fetchDashboard = () => fetchJSON('/analytics/dashboard');
export const fetchSales = () => fetchJSON('/analytics/sales');
export const fetchFulfillment = () => fetchJSON('/analytics/fulfillment');
export const fetchTopProducts = () => fetchJSON('/analytics/top-products');

// ── Forecasting ───────────────────────────────────────────
export const fetchForecast = (productId) => fetchJSON(`/forecast/${productId}`);

// ── Optimization ──────────────────────────────────────────
export const fetchReorder = (productId) => fetchJSON(`/optimize-reorder/${productId}`);
