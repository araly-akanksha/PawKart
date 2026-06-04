import { useState, useEffect } from 'react';
import { Radio, RefreshCw, Zap } from 'lucide-react';
import { fetchRFIDStats, fetchLatestRFIDEvents, fetchProducts, rfidScan } from '../api';

const eventBadge = { SALE: 'badge-success', RESTOCK: 'badge-info', RETURN: 'badge-warning', AUDIT: 'badge-purple' };

export default function RFID() {
  const [stats, setStats] = useState(null);
  const [events, setEvents] = useState([]);
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showScan, setShowScan] = useState(false);
  const [scanResult, setScanResult] = useState(null);
  const [form, setForm] = useState({ product_id: '', event_type: 'SALE', rfid_tag_id: '' });

  const load = () => {
    setLoading(true);
    Promise.all([fetchRFIDStats(), fetchLatestRFIDEvents(20), fetchProducts()])
      .then(([s, e, p]) => { setStats(s); setEvents(e); setProducts(p); })
      .catch(console.error)
      .finally(() => setLoading(false));
  };

  useEffect(load, []);

  const handleScan = async (e) => {
    e.preventDefault();
    const result = await rfidScan({ ...form, product_id: parseInt(form.product_id), rfid_tag_id: form.rfid_tag_id || `TAG-${Date.now()}` });
    setScanResult(result);
    setShowScan(false);
    load();
  };

  if (loading) return <div className="loading">Loading RFID data...</div>;

  return (
    <div>
      <div className="page-header">
        <div>
          <h2>RFID Monitor</h2>
          <p>Real-time inventory tracking via RFID scans</p>
        </div>
        <div style={{ display: 'flex', gap: 10 }}>
          <button className="btn" onClick={load}><RefreshCw size={16} /> Refresh</button>
          <button className="btn btn-primary" onClick={() => setShowScan(true)}><Zap size={16} /> Simulate Scan</button>
        </div>
      </div>

      {stats && (
        <div className="grid-4" style={{ marginBottom: 20 }}>
          <div className="stat-card"><div><div className="stat-value">{stats.total_events}</div><div className="stat-label">Total Events</div></div></div>
          <div className="stat-card"><div><div className="stat-value" style={{ color: 'var(--success)' }}>{stats.sale_count}</div><div className="stat-label">Sales</div></div></div>
          <div className="stat-card"><div><div className="stat-value" style={{ color: 'var(--info)' }}>{stats.restock_count}</div><div className="stat-label">Restocks</div></div></div>
          <div className="stat-card"><div><div className="stat-value" style={{ color: 'var(--warning)' }}>{stats.return_count || 0}</div><div className="stat-label">Returns</div></div></div>
        </div>
      )}

      {scanResult && (
        <div className="alert alert-success" style={{ justifyContent: 'space-between' }}>
          <span>
            <strong>Scan recorded:</strong> {scanResult.event_type} — {scanResult.product_name} — Stock: {scanResult.current_stock}
            {scanResult.stock_alert?.alert && <span className="badge badge-danger" style={{ marginLeft: 8 }}>{scanResult.stock_alert.alert}</span>}
          </span>
          <button className="btn-icon" onClick={() => setScanResult(null)}>✕</button>
        </div>
      )}

      <div className="card">
        <div className="card-title">Latest Events</div>
        <div className="table-wrapper">
          <table className="table">
            <thead>
              <tr><th>ID</th><th>Product ID</th><th>Tag ID</th><th>Event</th><th>Timestamp</th></tr>
            </thead>
            <tbody>
              {events.map((ev) => (
                <tr key={ev.id}>
                  <td>{ev.id}</td>
                  <td>{ev.product_id}</td>
                  <td style={{ fontFamily: 'monospace', fontSize: '0.82rem' }}>{ev.rfid_tag_id}</td>
                  <td><span className={`badge ${eventBadge[ev.event_type] || 'badge-info'}`}>{ev.event_type}</span></td>
                  <td style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>{new Date(ev.timestamp).toLocaleString('en-IN')}</td>
                </tr>
              ))}
              {events.length === 0 && <tr><td colSpan="5" style={{ textAlign: 'center', color: 'var(--text-muted)', padding: 40 }}>No RFID events yet. Simulate a scan to get started.</td></tr>}
            </tbody>
          </table>
        </div>
      </div>

      {showScan && (
        <div className="modal-overlay" onClick={() => setShowScan(false)}>
          <div className="modal" onClick={(e) => e.stopPropagation()}>
            <h3>Simulate RFID Scan</h3>
            <form onSubmit={handleScan} style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
              <div className="form-group">
                <label className="form-label">Product *</label>
                <select className="form-select" required value={form.product_id} onChange={(e) => setForm({ ...form, product_id: e.target.value })}>
                  <option value="">Select product</option>
                  {products.map((p) => <option key={p.id} value={p.id}>{p.product_name}</option>)}
                </select>
              </div>
              <div className="form-group">
                <label className="form-label">Event Type *</label>
                <select className="form-select" value={form.event_type} onChange={(e) => setForm({ ...form, event_type: e.target.value })}>
                  <option value="SALE">SALE</option><option value="RESTOCK">RESTOCK</option><option value="RETURN">RETURN</option><option value="AUDIT">AUDIT</option>
                </select>
              </div>
              <div className="form-group"><label className="form-label">RFID Tag ID</label><input className="form-input" placeholder="Auto-generated if empty" value={form.rfid_tag_id} onChange={(e) => setForm({ ...form, rfid_tag_id: e.target.value })} /></div>
              <div className="modal-actions">
                <button type="button" className="btn" onClick={() => setShowScan(false)}>Cancel</button>
                <button type="submit" className="btn btn-primary">Scan</button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
