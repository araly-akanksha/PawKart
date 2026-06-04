import { useState, useEffect } from 'react';
import { IndianRupee, ShoppingBag, Clock, AlertTriangle, CheckCircle, Package } from 'lucide-react';
import { AreaChart, Area, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts';
import { fetchDashboard, fetchSales, fetchOrderSummary } from '../api';

const statusColors = {
  pending: 'badge-warning', confirmed: 'badge-info', preparing: 'badge-purple',
  out_for_delivery: 'badge-cyan', delivered: 'badge-success', cancelled: 'badge-danger',
};

export default function Dashboard() {
  const [kpi, setKpi] = useState(null);
  const [sales, setSales] = useState([]);
  const [orders, setOrders] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([fetchDashboard(), fetchSales(), fetchOrderSummary()])
      .then(([k, s, o]) => { setKpi(k); setSales(s); setOrders(o); })
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <div className="loading">Loading dashboard...</div>;

  const fmt = (n) => Number(n || 0).toLocaleString('en-IN');

  return (
    <div>
      <div className="page-header">
        <div>
          <h2>Dashboard</h2>
          <p>{new Date().toLocaleDateString('en-IN', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' })}</p>
        </div>
      </div>

      <div className="grid-4" style={{ marginBottom: 20 }}>
        <div className="stat-card">
          <div className="stat-icon" style={{ background: 'var(--primary-glow)', color: 'var(--primary)' }}><IndianRupee size={22} /></div>
          <div>
            <div className="stat-value">₹{fmt(kpi?.today_revenue)}</div>
            <div className="stat-label">Today's Revenue</div>
            {kpi?.revenue_change != null && <div className={`stat-change ${kpi.revenue_change >= 0 ? 'positive' : 'negative'}`}>{kpi.revenue_change >= 0 ? '+' : ''}{kpi.revenue_change?.toFixed(1)}% from yesterday</div>}
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-icon" style={{ background: 'var(--info-bg)', color: 'var(--info)' }}><ShoppingBag size={22} /></div>
          <div>
            <div className="stat-value">{kpi?.today_orders || 0}</div>
            <div className="stat-label">Today's Orders</div>
            {kpi?.orders_change != null && <div className={`stat-change ${kpi.orders_change >= 0 ? 'positive' : 'negative'}`}>{kpi.orders_change >= 0 ? '+' : ''}{kpi.orders_change?.toFixed(1)}%</div>}
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-icon" style={{ background: 'var(--warning-bg)', color: 'var(--warning)' }}><Clock size={22} /></div>
          <div>
            <div className="stat-value">{kpi?.pending_orders || 0}</div>
            <div className="stat-label">Pending Orders</div>
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-icon" style={{ background: kpi?.low_stock_count > 0 ? 'var(--danger-bg)' : 'var(--success-bg)', color: kpi?.low_stock_count > 0 ? 'var(--danger)' : 'var(--success)' }}><AlertTriangle size={22} /></div>
          <div>
            <div className="stat-value">{kpi?.low_stock_count || 0}</div>
            <div className="stat-label">Low Stock Items</div>
          </div>
        </div>
      </div>

      <div className="grid-2" style={{ marginBottom: 20 }}>
        <div className="stat-card">
          <div className="stat-icon" style={{ background: 'var(--success-bg)', color: 'var(--success)' }}><CheckCircle size={22} /></div>
          <div>
            <div className="stat-value">{kpi?.fulfillment_rate || 0}%</div>
            <div className="stat-label">Fulfillment Rate (30d)</div>
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-icon" style={{ background: 'var(--primary-glow)', color: 'var(--primary)' }}><Package size={22} /></div>
          <div>
            <div className="stat-value">{kpi?.active_products || 0}</div>
            <div className="stat-label">Active Products</div>
          </div>
        </div>
      </div>

      <div className="card" style={{ marginBottom: 20 }}>
        <div className="card-title">30-Day Sales Trend</div>
        <div className="chart-container">
          <ResponsiveContainer width="100%" height={300}>
            <AreaChart data={sales}>
              <defs>
                <linearGradient id="salesGrad" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#6C63FF" stopOpacity={0.3} />
                  <stop offset="95%" stopColor="#6C63FF" stopOpacity={0} />
                </linearGradient>
              </defs>
              <XAxis dataKey="date" tick={{ fill: '#6B7280', fontSize: 11 }} tickFormatter={(d) => d.slice(5)} />
              <YAxis tick={{ fill: '#6B7280', fontSize: 11 }} />
              <Tooltip contentStyle={{ background: '#1A1D26', border: '1px solid #2A2D3A', borderRadius: 8, color: '#F0F0F5' }} />
              <Area type="monotone" dataKey="revenue" stroke="#6C63FF" fill="url(#salesGrad)" strokeWidth={2} />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      </div>

      {orders && (
        <div className="card">
          <div className="card-title">Order Status Summary</div>
          <div style={{ display: 'flex', gap: 12, flexWrap: 'wrap' }}>
            {Object.entries(statusColors).map(([status, cls]) => (
              <span key={status} className={`badge ${cls}`}>
                {status.replace(/_/g, ' ')}: {orders[status] || 0}
              </span>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
