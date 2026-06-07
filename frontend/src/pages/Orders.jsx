import { useState, useEffect, useRef } from 'react';
import { Plus, ChevronRight, Zap, Clock, CheckCircle, AlertCircle } from 'lucide-react';
import { fetchOrders, fetchOrderSummary, createOrder, updateOrderStatus, fetchProducts, dispatchOrder, fetchDispatchStatus } from '../api';

const statuses = ['all', 'pending', 'confirmed', 'preparing', 'out_for_delivery', 'delivered', 'cancelled'];
const statusBadge = {
  pending: 'badge-warning',
  confirmed: 'badge-info',
  preparing: 'badge-purple',
  out_for_delivery: 'badge-cyan',
  delivered: 'badge-success',
  cancelled: 'badge-danger',
};
const nextStatus = {
  pending: 'confirmed',
  confirmed: 'preparing',
  preparing: 'out_for_delivery',
  out_for_delivery: 'delivered',
};

// SLA = 90s demo (represents 30 min real-world)
const SLA_SECONDS = 90;

// ── Live Delivery Timer ──────────────────────────────────────
function DeliveryTimer({ dispatchedAt, status }) {
  const [elapsed, setElapsed] = useState(0);

  useEffect(() => {
    if (!dispatchedAt || status === 'delivered' || status === 'cancelled') return;
    const start = new Date(dispatchedAt).getTime();
    const interval = setInterval(() => {
      setElapsed(Math.floor((Date.now() - start) / 1000));
    }, 1000);
    return () => clearInterval(interval);
  }, [dispatchedAt, status]);

  if (!dispatchedAt) return null;

  if (status === 'delivered') {
    const deliveryTime = Math.floor((Date.now() - new Date(dispatchedAt).getTime()) / 1000);
    const slaColor = deliveryTime <= SLA_SECONDS ? '#22C55E' : '#EF4444';
    const slaIcon = deliveryTime <= SLA_SECONDS ? '✅' : '⚠️';
    return (
      <span style={{ fontSize: '0.75rem', color: slaColor, fontWeight: 600 }}>
        {slaIcon} {deliveryTime}s delivery
      </span>
    );
  }

  const remaining = Math.max(0, SLA_SECONDS - elapsed);
  const isUrgent = remaining < 20;
  return (
    <span style={{
      fontSize: '0.75rem',
      color: isUrgent ? '#EF4444' : '#F59E0B',
      fontWeight: 600,
      display: 'flex',
      alignItems: 'center',
      gap: 4,
    }}>
      <Clock size={12} />
      {remaining}s left
    </span>
  );
}

export default function Orders() {
  const [orders, setOrders] = useState([]);
  const [summary, setSummary] = useState(null);
  const [filter, setFilter] = useState('all');
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [products, setProducts] = useState([]);
  const [dispatching, setDispatching] = useState({});    // orderId -> true
  const [dispatchInfo, setDispatchInfo] = useState({});  // orderId -> { dispatched_at, estimated_delivery_at }
  const [form, setForm] = useState({
    customer_name: '', customer_phone: '', customer_address: '',
    delivery_slot: '', items: [{ product_id: '', quantity: 1 }],
  });

  // Auto-refresh every 5s to pick up background status changes
  const refreshRef = useRef(null);

  const load = () => {
    setLoading(true);
    Promise.all([fetchOrders(filter), fetchOrderSummary()])
      .then(([o, s]) => { setOrders(o); setSummary(s); })
      .catch(console.error)
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    load();
    // Poll every 5 seconds while any order is dispatched
    refreshRef.current = setInterval(() => {
      if (Object.keys(dispatchInfo).length > 0) load();
    }, 5000);
    return () => clearInterval(refreshRef.current);
  }, [filter]);

  // Re-start polling when dispatch info changes
  useEffect(() => {
    clearInterval(refreshRef.current);
    if (Object.keys(dispatchInfo).length > 0) {
      refreshRef.current = setInterval(load, 5000);
    }
    return () => clearInterval(refreshRef.current);
  }, [dispatchInfo, filter]);

  const openForm = async () => {
    const p = await fetchProducts();
    setProducts(p);
    setShowForm(true);
  };

  const addItem = () => setForm({ ...form, items: [...form.items, { product_id: '', quantity: 1 }] });

  const handleSubmit = async (e) => {
    e.preventDefault();
    await createOrder({
      ...form,
      items: form.items
        .filter((i) => i.product_id)
        .map((i) => ({ product_id: parseInt(i.product_id), quantity: parseInt(i.quantity) })),
    });
    setShowForm(false);
    setForm({ customer_name: '', customer_phone: '', customer_address: '', delivery_slot: '', items: [{ product_id: '', quantity: 1 }] });
    load();
  };

  const advance = async (id, status) => {
    const next = nextStatus[status];
    if (next) { await updateOrderStatus(id, next); load(); }
  };

  const cancel = async (id) => {
    if (confirm('Cancel this order?')) { await updateOrderStatus(id, 'cancelled'); load(); }
  };

  // ── Dispatch Handler ───────────────────────────────────────
  const handleDispatch = async (id) => {
    setDispatching((d) => ({ ...d, [id]: true }));
    try {
      const res = await dispatchOrder(id);
      setDispatchInfo((d) => ({
        ...d,
        [id]: {
          dispatched_at: res.dispatched_at,
          estimated_delivery_at: res.estimated_delivery_at,
          pipeline: res.pipeline,
        },
      }));
      load();
    } catch (e) {
      alert('Dispatch failed: ' + e.message);
    } finally {
      setDispatching((d) => ({ ...d, [id]: false }));
    }
  };

  const isDispatched = (id) => !!dispatchInfo[id];

  return (
    <div>
      <div className="page-header">
        <div>
          <h2>Order Management</h2>
          <p>{orders.length} orders · Auto-refreshing every 5s when dispatched</p>
        </div>
        <button className="btn btn-primary" onClick={openForm}><Plus size={16} /> New Order</button>
      </div>

      {/* SLA Info Banner */}
      <div style={{
        background: 'linear-gradient(135deg, rgba(108,99,255,0.15), rgba(34,197,94,0.1))',
        border: '1px solid rgba(108,99,255,0.3)',
        borderRadius: 10,
        padding: '12px 18px',
        marginBottom: 20,
        display: 'flex',
        alignItems: 'center',
        gap: 12,
        fontSize: '0.85rem',
        color: 'var(--text-secondary)',
      }}>
        <Zap size={18} style={{ color: '#6C63FF', flexShrink: 0 }} />
        <span>
          <strong style={{ color: 'var(--text-primary)' }}>🚀 Automated Delivery Pipeline:</strong>
          &nbsp;Click <em>Dispatch</em> on any order to trigger automatic fulfillment —
          confirmed → preparing → out for delivery → delivered in ~90s (demo = 30-min SLA).
        </span>
      </div>

      {summary && (
        <div style={{ display: 'flex', gap: 10, marginBottom: 20, flexWrap: 'wrap' }}>
          {Object.entries(statusBadge).map(([s, cls]) => (
            <span
              key={s}
              className={`badge ${cls}`}
              style={{ cursor: 'pointer', padding: '6px 14px', fontSize: '0.78rem' }}
              onClick={() => setFilter(s)}
            >
              {s.replace(/_/g, ' ')}: {summary[s] || 0}
            </span>
          ))}
          <span
            className="badge badge-info"
            style={{ cursor: 'pointer', padding: '6px 14px' }}
            onClick={() => setFilter('all')}
          >
            Total: {summary.total || 0}
          </span>
        </div>
      )}

      {loading ? <div className="loading">Loading orders...</div> : (
        <div className="card">
          <div className="table-wrapper">
            <table className="table">
              <thead>
                <tr>
                  <th>#</th>
                  <th>Customer</th>
                  <th>Total</th>
                  <th>Items</th>
                  <th>Status</th>
                  <th>Delivery Slot</th>
                  <th>Date</th>
                  <th>SLA Timer</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {orders.map((o) => (
                  <tr key={o.id} style={{
                    background: isDispatched(o.id) && o.status !== 'delivered' && o.status !== 'cancelled'
                      ? 'rgba(108,99,255,0.06)' : undefined,
                  }}>
                    <td>{o.id}</td>
                    <td style={{ fontWeight: 600 }}>{o.customer_name}</td>
                    <td>₹{o.total_amount.toLocaleString('en-IN')}</td>
                    <td>{o.item_count}</td>
                    <td>
                      <span className={`badge ${statusBadge[o.status] || 'badge-info'}`}>
                        {o.status.replace(/_/g, ' ')}
                      </span>
                    </td>
                    <td>{o.delivery_slot || '—'}</td>
                    <td style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                      {new Date(o.created_at).toLocaleDateString('en-IN')}
                    </td>
                    <td>
                      {isDispatched(o.id) ? (
                        <DeliveryTimer
                          dispatchedAt={dispatchInfo[o.id]?.dispatched_at}
                          status={o.status}
                        />
                      ) : (
                        o.status === 'delivered'
                          ? <span style={{ color: '#22C55E', fontSize: '0.75rem', fontWeight: 600 }}>✅ Delivered</span>
                          : <span style={{ color: 'var(--text-muted)', fontSize: '0.75rem' }}>—</span>
                      )}
                    </td>
                    <td style={{ display: 'flex', gap: 6, flexWrap: 'wrap' }}>
                      {/* Dispatch button — automated pipeline trigger */}
                      {!isDispatched(o.id) && o.status !== 'delivered' && o.status !== 'cancelled' && (
                        <button
                          className="btn btn-sm btn-primary"
                          onClick={() => handleDispatch(o.id)}
                          disabled={dispatching[o.id]}
                          title="Auto-advance through full delivery pipeline"
                        >
                          <Zap size={13} />
                          {dispatching[o.id] ? 'Dispatching...' : 'Dispatch'}
                        </button>
                      )}
                      {/* Manual advance */}
                      {nextStatus[o.status] && !isDispatched(o.id) && (
                        <button className="btn btn-sm btn-success" onClick={() => advance(o.id, o.status)}>
                          <ChevronRight size={14} /> {nextStatus[o.status].replace(/_/g, ' ')}
                        </button>
                      )}
                      {o.status === 'pending' && (
                        <button className="btn btn-sm btn-danger" onClick={() => cancel(o.id)}>Cancel</button>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Active Dispatch Panel */}
      {Object.keys(dispatchInfo).length > 0 && (
        <div className="card" style={{ marginTop: 16, borderColor: 'var(--primary)' }}>
          <div className="card-title" style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
            <Zap size={16} style={{ color: 'var(--primary)' }} /> Active Deliveries
          </div>
          {Object.entries(dispatchInfo).map(([id, info]) => {
            const order = orders.find((o) => o.id === parseInt(id));
            if (!order) return null;
            return (
              <div key={id} style={{
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
                padding: '10px 0',
                borderBottom: '1px solid var(--border)',
                fontSize: '0.85rem',
              }}>
                <div>
                  <strong>Order #{id}</strong> — {order.customer_name}
                  <div style={{ color: 'var(--text-muted)', marginTop: 2, fontSize: '0.75rem' }}>
                    Pipeline: {info.pipeline}
                  </div>
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                  <span className={`badge ${statusBadge[order.status]}`}>{order.status.replace(/_/g, ' ')}</span>
                  <DeliveryTimer dispatchedAt={info.dispatched_at} status={order.status} />
                </div>
              </div>
            );
          })}
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
