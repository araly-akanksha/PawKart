import { useState, useEffect } from 'react';
import { Plus, ChevronRight } from 'lucide-react';
import { fetchOrders, fetchOrderSummary, createOrder, updateOrderStatus, fetchProducts } from '../api';

const statuses = ['all', 'pending', 'confirmed', 'preparing', 'out_for_delivery', 'delivered', 'cancelled'];
const statusBadge = { pending: 'badge-warning', confirmed: 'badge-info', preparing: 'badge-purple', out_for_delivery: 'badge-cyan', delivered: 'badge-success', cancelled: 'badge-danger' };
const nextStatus = { pending: 'confirmed', confirmed: 'preparing', preparing: 'out_for_delivery', out_for_delivery: 'delivered' };

export default function Orders() {
  const [orders, setOrders] = useState([]);
  const [summary, setSummary] = useState(null);
  const [filter, setFilter] = useState('all');
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [products, setProducts] = useState([]);
  const [form, setForm] = useState({ customer_name: '', customer_phone: '', customer_address: '', delivery_slot: '', items: [{ product_id: '', quantity: 1 }] });

  const load = () => {
    setLoading(true);
    Promise.all([fetchOrders(filter), fetchOrderSummary()])
      .then(([o, s]) => { setOrders(o); setSummary(s); })
      .catch(console.error)
      .finally(() => setLoading(false));
  };

  useEffect(load, [filter]);

  const openForm = async () => {
    const p = await fetchProducts();
    setProducts(p);
    setShowForm(true);
  };

  const addItem = () => setForm({ ...form, items: [...form.items, { product_id: '', quantity: 1 }] });

  const handleSubmit = async (e) => {
    e.preventDefault();
    await createOrder({ ...form, items: form.items.filter((i) => i.product_id).map((i) => ({ product_id: parseInt(i.product_id), quantity: parseInt(i.quantity) })) });
    setShowForm(false);
    setForm({ customer_name: '', customer_phone: '', customer_address: '', delivery_slot: '', items: [{ product_id: '', quantity: 1 }] });
    load();
  };

  const advance = async (id, status) => {
    const next = nextStatus[status];
    if (next) {
      await updateOrderStatus(id, next);
      load();
    }
  };

  const cancel = async (id) => {
    if (confirm('Cancel this order?')) {
      await updateOrderStatus(id, 'cancelled');
      load();
    }
  };

  return (
    <div>
      <div className="page-header">
        <div>
          <h2>Order Management</h2>
          <p>{orders.length} orders</p>
        </div>
        <button className="btn btn-primary" onClick={openForm}><Plus size={16} /> New Order</button>
      </div>

      {summary && (
        <div style={{ display: 'flex', gap: 10, marginBottom: 20, flexWrap: 'wrap' }}>
          {Object.entries(statusBadge).map(([s, cls]) => (
            <span key={s} className={`badge ${cls}`} style={{ cursor: 'pointer', padding: '6px 14px', fontSize: '0.78rem' }} onClick={() => setFilter(s)}>
              {s.replace(/_/g, ' ')}: {summary[s] || 0}
            </span>
          ))}
          <span className="badge badge-info" style={{ cursor: 'pointer', padding: '6px 14px' }} onClick={() => setFilter('all')}>Total: {summary.total || 0}</span>
        </div>
      )}

      {loading ? <div className="loading">Loading orders...</div> : (
        <div className="card">
          <div className="table-wrapper">
            <table className="table">
              <thead>
                <tr><th>#</th><th>Customer</th><th>Total</th><th>Items</th><th>Status</th><th>Delivery Slot</th><th>Date</th><th>Actions</th></tr>
              </thead>
              <tbody>
                {orders.map((o) => (
                  <tr key={o.id}>
                    <td>{o.id}</td>
                    <td style={{ fontWeight: 600 }}>{o.customer_name}</td>
                    <td>₹{o.total_amount.toLocaleString('en-IN')}</td>
                    <td>{o.item_count}</td>
                    <td><span className={`badge ${statusBadge[o.status] || 'badge-info'}`}>{o.status.replace(/_/g, ' ')}</span></td>
                    <td>{o.delivery_slot || '—'}</td>
                    <td style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>{new Date(o.created_at).toLocaleDateString('en-IN')}</td>
                    <td style={{ display: 'flex', gap: 6 }}>
                      {nextStatus[o.status] && <button className="btn btn-sm btn-success" onClick={() => advance(o.id, o.status)}><ChevronRight size={14} /> {nextStatus[o.status].replace(/_/g, ' ')}</button>}
                      {o.status === 'pending' && <button className="btn btn-sm btn-danger" onClick={() => cancel(o.id)}>Cancel</button>}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {showForm && (
        <div className="modal-overlay" onClick={() => setShowForm(false)}>
          <div className="modal" onClick={(e) => e.stopPropagation()}>
            <h3>New Order</h3>
            <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
              <div className="form-row">
                <div className="form-group"><label className="form-label">Customer Name *</label><input className="form-input" required value={form.customer_name} onChange={(e) => setForm({ ...form, customer_name: e.target.value })} /></div>
                <div className="form-group"><label className="form-label">Phone</label><input className="form-input" value={form.customer_phone} onChange={(e) => setForm({ ...form, customer_phone: e.target.value })} /></div>
              </div>
              <div className="form-group"><label className="form-label">Address *</label><input className="form-input" required value={form.customer_address} onChange={(e) => setForm({ ...form, customer_address: e.target.value })} /></div>
              <div className="form-group"><label className="form-label">Delivery Slot</label><input className="form-input" placeholder="e.g. 10:00-11:00" value={form.delivery_slot} onChange={(e) => setForm({ ...form, delivery_slot: e.target.value })} /></div>
              <div className="form-label">Items</div>
              {form.items.map((item, i) => (
                <div className="form-row" key={i}>
                  <select className="form-select" value={item.product_id} onChange={(e) => { const items = [...form.items]; items[i].product_id = e.target.value; setForm({ ...form, items }); }}>
                    <option value="">Select product</option>
                    {products.map((p) => <option key={p.id} value={p.id}>{p.product_name} — ₹{p.price}</option>)}
                  </select>
                  <input className="form-input" type="number" min="1" value={item.quantity} onChange={(e) => { const items = [...form.items]; items[i].quantity = e.target.value; setForm({ ...form, items }); }} />
                </div>
              ))}
              <button type="button" className="btn btn-sm" onClick={addItem}><Plus size={14} /> Add Item</button>
              <div className="modal-actions">
                <button type="button" className="btn" onClick={() => setShowForm(false)}>Cancel</button>
                <button type="submit" className="btn btn-primary">Place Order</button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
