import { useState, useEffect } from 'react';
import { AlertTriangle, TrendingDown, Brain } from 'lucide-react';
import { fetchInventory, fetchLowStockAlerts, fetchReorder } from '../api';

export default function Inventory() {
  const [inventory, setInventory] = useState([]);
  const [alerts, setAlerts] = useState([]);
  const [reorder, setReorder] = useState(null);
  const [loading, setLoading] = useState(true);

  const load = () => {
    setLoading(true);
    Promise.all([fetchInventory(), fetchLowStockAlerts()])
      .then(([inv, al]) => { setInventory(inv); setAlerts(al); })
      .catch(console.error)
      .finally(() => setLoading(false));
  };

  useEffect(load, []);

  const handleReorder = async (productId) => {
    const result = await fetchReorder(productId);
    setReorder(result);
  };

  if (loading) return <div className="loading">Loading inventory...</div>;

  return (
    <div>
      <div className="page-header">
        <div>
          <h2>Inventory Management</h2>
          <p>{inventory.length} tracked items</p>
        </div>
      </div>

      {alerts.length > 0 && (
        <div className="alert alert-danger">
          <AlertTriangle size={18} />
          <strong>{alerts.length} low-stock item{alerts.length > 1 ? 's' : ''}:</strong>
          {alerts.map((a) => a.product_name).join(', ')}
        </div>
      )}

      <div className="card" style={{ marginBottom: 20 }}>
        <div className="table-wrapper">
          <table className="table">
            <thead>
              <tr><th>Product</th><th>Stock</th><th>Reorder Level</th><th>Unit</th><th>Status</th><th>Actions</th></tr>
            </thead>
            <tbody>
              {inventory.map((item) => {
                const low = item.current_stock <= item.reorder_level;
                return (
                  <tr key={item.id}>
                    <td style={{ fontWeight: 600 }}>{item.product_name || `Product #${item.product_id}`}</td>
                    <td style={{ color: low ? 'var(--danger)' : 'var(--success)', fontWeight: 700 }}>{item.current_stock}</td>
                    <td>{item.reorder_level}</td>
                    <td>{item.unit}</td>
                    <td><span className={`badge ${low ? 'badge-danger' : 'badge-success'}`}>{low ? 'Low Stock' : 'Healthy'}</span></td>
                    <td><button className="btn btn-sm" onClick={() => handleReorder(item.product_id)}><Brain size={14} /> AI Reorder</button></td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>

      {reorder && (
        <div className="card" style={{ borderColor: reorder.risk_level === 'Critical' || reorder.risk_level === 'High Risk' ? 'var(--danger)' : 'var(--border)' }}>
          <div className="card-title" style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
            <TrendingDown size={16} /> AI Reorder Recommendation
          </div>
          <div className="grid-3" style={{ marginBottom: 16 }}>
            <div>
              <div style={{ color: 'var(--text-muted)', fontSize: '0.75rem' }}>Current Stock</div>
              <div style={{ fontSize: '1.3rem', fontWeight: 700 }}>{reorder.current_stock}</div>
            </div>
            <div>
              <div style={{ color: 'var(--text-muted)', fontSize: '0.75rem' }}>Risk Level</div>
              <div><span className={`badge ${reorder.risk_level === 'Low Risk' ? 'badge-success' : reorder.risk_level === 'Moderate Risk' ? 'badge-warning' : 'badge-danger'}`}>{reorder.risk_level}</span></div>
            </div>
            <div>
              <div style={{ color: 'var(--text-muted)', fontSize: '0.75rem' }}>Recommended Order</div>
              <div style={{ fontSize: '1.3rem', fontWeight: 700, color: 'var(--primary)' }}>{reorder.recommended_reorder_quantity} units</div>
            </div>
          </div>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.85rem', lineHeight: 1.6 }}>{reorder.explanation}</p>
          <button className="btn" style={{ marginTop: 12 }} onClick={() => setReorder(null)}>Dismiss</button>
        </div>
      )}
    </div>
  );
}
