import { useState, useEffect } from 'react';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from 'recharts';
import { fetchSales, fetchFulfillment, fetchTopProducts } from '../api';

export default function Analytics() {
  const [sales, setSales] = useState([]);
  const [fulfill, setFulfill] = useState(null);
  const [top, setTop] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([fetchSales(), fetchFulfillment(), fetchTopProducts()])
      .then(([s, f, t]) => { setSales(s); setFulfill(f); setTop(t); })
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <div className="loading">Loading analytics...</div>;

  return (
    <div>
      <div className="page-header">
        <div><h2>Analytics & Reports</h2><p>Performance metrics and trends</p></div>
      </div>

      {fulfill && (
        <div className="grid-4" style={{ marginBottom: 20 }}>
          <div className="stat-card"><div><div className="stat-value" style={{ color: 'var(--success)' }}>{fulfill.fulfillment_rate}%</div><div className="stat-label">Fulfillment Rate</div></div></div>
          <div className="stat-card"><div><div className="stat-value">{fulfill.avg_delivery_minutes || '—'}</div><div className="stat-label">Avg Delivery (min)</div></div></div>
          <div className="stat-card"><div><div className="stat-value" style={{ color: 'var(--success)' }}>{fulfill.on_time_rate || 0}%</div><div className="stat-label">On-Time Rate</div></div></div>
          <div className="stat-card"><div><div className="stat-value" style={{ color: 'var(--danger)' }}>{fulfill.cancel_rate || 0}%</div><div className="stat-label">Cancel Rate</div></div></div>
        </div>
      )}

      <div className="card" style={{ marginBottom: 20 }}>
        <div className="card-title">Revenue & Orders (30 Days)</div>
        <div className="chart-container">
          <ResponsiveContainer width="100%" height={320}>
            <BarChart data={sales}>
              <CartesianGrid strokeDasharray="3 3" stroke="#2A2D3A" />
              <XAxis dataKey="date" tick={{ fill: '#6B7280', fontSize: 11 }} tickFormatter={(d) => d.slice(5)} />
              <YAxis tick={{ fill: '#6B7280', fontSize: 11 }} />
              <Tooltip contentStyle={{ background: '#1A1D26', border: '1px solid #2A2D3A', borderRadius: 8, color: '#F0F0F5' }} />
              <Bar dataKey="revenue" fill="#6C63FF" radius={[4, 4, 0, 0]} name="Revenue (₹)" />
              <Bar dataKey="order_count" fill="#00D9FF" radius={[4, 4, 0, 0]} name="Orders" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      <div className="card">
        <div className="card-title">Top Products by Revenue</div>
        <div className="table-wrapper">
          <table className="table">
            <thead><tr><th>#</th><th>Product</th><th>Units Sold</th><th>Revenue</th></tr></thead>
            <tbody>
              {top.map((p, i) => (
                <tr key={i}>
                  <td style={{ fontWeight: 700, color: 'var(--primary)' }}>{i + 1}</td>
                  <td style={{ fontWeight: 600 }}>{p.product_name}</td>
                  <td>{p.total_sold}</td>
                  <td>₹{(p.revenue || 0).toLocaleString('en-IN')}</td>
                </tr>
              ))}
              {top.length === 0 && <tr><td colSpan="4" style={{ textAlign: 'center', color: 'var(--text-muted)', padding: 40 }}>No sales data yet</td></tr>}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
