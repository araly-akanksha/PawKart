import { useState, useEffect } from 'react';
import { Brain, TrendingUp, AlertTriangle, RefreshCw, ChevronDown } from 'lucide-react';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid, Cell } from 'recharts';
import { fetchProducts, fetchForecast, fetchReorder } from '../api';

const demandColor = {
  'High Demand': '#22C55E',
  'Medium Demand': '#F59E0B',
  'Low Demand': '#6C63FF',
  'Very Low Demand': '#6B7280',
};

export default function Forecast() {
  const [products, setProducts] = useState([]);
  const [forecasts, setForecasts] = useState({});
  const [reorders, setReorders] = useState({});
  const [loading, setLoading] = useState(true);
  const [analyzing, setAnalyzing] = useState(false);
  const [selected, setSelected] = useState(null);

  useEffect(() => {
    fetchProducts()
      .then(setProducts)
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  const runAnalysis = async () => {
    setAnalyzing(true);
    const results = {};
    const reorderResults = {};

    for (const p of products.slice(0, 15)) {
      try {
        const [forecast, reorder] = await Promise.all([
          fetchForecast(p.id),
          fetchReorder(p.id),
        ]);
        results[p.id] = forecast;
        reorderResults[p.id] = reorder;
      } catch (e) {
        console.error(`Forecast failed for ${p.id}:`, e);
      }
    }

    setForecasts(results);
    setReorders(reorderResults);
    setAnalyzing(false);
  };

  const chartData = products
    .filter((p) => forecasts[p.id])
    .map((p) => ({
      name: p.product_name.length > 18 ? p.product_name.slice(0, 16) + '…' : p.product_name,
      demand: forecasts[p.id].predicted_demand_next_week,
      category: forecasts[p.id].demand_category,
      id: p.id,
    }))
    .sort((a, b) => b.demand - a.demand);

  const summaryStats = Object.values(forecasts);
  const highCount = summaryStats.filter((f) => f.demand_category === 'High Demand').length;
  const medCount = summaryStats.filter((f) => f.demand_category === 'Medium Demand').length;
  const lowCount = summaryStats.filter((f) => f.demand_category === 'Low Demand' || f.demand_category === 'Very Low Demand').length;

  if (loading) return <div className="loading">Loading products...</div>;

  return (
    <div>
      <div className="page-header">
        <div>
          <h2>AI Demand Forecast</h2>
          <p>LSTM neural network predictions for inventory planning</p>
        </div>
        <button
          className="btn btn-primary"
          onClick={runAnalysis}
          disabled={analyzing}
        >
          {analyzing ? (
            <><RefreshCw size={16} className="spin" /> Analyzing...</>
          ) : (
            <><Brain size={16} /> Run Forecast</>
          )}
        </button>
      </div>

      {Object.keys(forecasts).length === 0 ? (
        <div className="card" style={{ textAlign: 'center', padding: '60px 20px' }}>
          <Brain size={48} style={{ color: 'var(--primary)', marginBottom: 16, opacity: 0.5 }} />
          <h3 style={{ marginBottom: 8, color: 'var(--text-primary)' }}>Ready to Forecast</h3>
          <p style={{ color: 'var(--text-muted)', marginBottom: 20 }}>
            Click "Run Forecast" to analyze demand for all products using the
            LSTM neural network trained on 98,875 sales records.
          </p>
        </div>
      ) : (
        <>
          {/* Summary KPIs */}
          <div className="grid-4" style={{ marginBottom: 20 }}>
            <div className="stat-card">
              <div>
                <div className="stat-value">{summaryStats.length}</div>
                <div className="stat-label">Products Analyzed</div>
              </div>
            </div>
            <div className="stat-card">
              <div>
                <div className="stat-value" style={{ color: '#22C55E' }}>{highCount}</div>
                <div className="stat-label">High Demand</div>
              </div>
            </div>
            <div className="stat-card">
              <div>
                <div className="stat-value" style={{ color: '#F59E0B' }}>{medCount}</div>
                <div className="stat-label">Medium Demand</div>
              </div>
            </div>
            <div className="stat-card">
              <div>
                <div className="stat-value" style={{ color: '#6C63FF' }}>{lowCount}</div>
                <div className="stat-label">Low / Very Low</div>
              </div>
            </div>
          </div>

          {/* Demand Chart */}
          <div className="card" style={{ marginBottom: 20 }}>
            <div className="card-title">Predicted Weekly Demand by Product</div>
            <div className="chart-container">
              <ResponsiveContainer width="100%" height={320}>
                <BarChart data={chartData} layout="vertical" margin={{ left: 120 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#2A2D3A" />
                  <XAxis type="number" tick={{ fill: '#6B7280', fontSize: 11 }} />
                  <YAxis type="category" dataKey="name" tick={{ fill: '#9CA3AF', fontSize: 11 }} width={110} />
                  <Tooltip
                    contentStyle={{ background: '#1A1D26', border: '1px solid #2A2D3A', borderRadius: 8, color: '#F0F0F5' }}
                    formatter={(val) => [`${val} units/week`, 'Demand']}
                  />
                  <Bar dataKey="demand" radius={[0, 4, 4, 0]} barSize={18}>
                    {chartData.map((entry, i) => (
                      <Cell key={i} fill={demandColor[entry.category] || '#6C63FF'} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* Product Details Table */}
          <div className="card">
            <div className="card-title">Forecast Details</div>
            <div className="table-wrapper">
              <table className="table">
                <thead>
                  <tr>
                    <th>Product</th>
                    <th>Weekly Demand</th>
                    <th>Category</th>
                    <th>Confidence</th>
                    <th>Risk Level</th>
                    <th>Reorder Qty</th>
                    <th>Details</th>
                  </tr>
                </thead>
                <tbody>
                  {products
                    .filter((p) => forecasts[p.id])
                    .sort((a, b) => (forecasts[b.id]?.predicted_demand_next_week || 0) - (forecasts[a.id]?.predicted_demand_next_week || 0))
                    .map((p) => {
                      const f = forecasts[p.id];
                      const r = reorders[p.id];
                      return (
                        <tr key={p.id}>
                          <td style={{ fontWeight: 600 }}>{p.product_name}</td>
                          <td style={{ fontWeight: 700, color: demandColor[f.demand_category] || 'var(--text-primary)' }}>
                            {f.predicted_demand_next_week}
                          </td>
                          <td>
                            <span className={`badge ${f.demand_category === 'High Demand' ? 'badge-success' : f.demand_category === 'Medium Demand' ? 'badge-warning' : 'badge-info'}`}>
                              {f.demand_category}
                            </span>
                          </td>
                          <td>
                            <span className={`badge ${f.confidence === 'high' ? 'badge-success' : f.confidence === 'medium' ? 'badge-warning' : 'badge-danger'}`}>
                              {f.confidence}
                            </span>
                          </td>
                          <td>
                            {r && (
                              <span className={`badge ${r.risk_level === 'Low Risk' ? 'badge-success' : r.risk_level === 'Moderate Risk' ? 'badge-warning' : 'badge-danger'}`}>
                                {r.risk_level}
                              </span>
                            )}
                          </td>
                          <td style={{ fontWeight: 700, color: r?.recommended_reorder_quantity > 0 ? 'var(--warning)' : 'var(--success)' }}>
                            {r?.recommended_reorder_quantity || 0} units
                          </td>
                          <td>
                            <button
                              className="btn btn-sm"
                              onClick={() => setSelected(selected === p.id ? null : p.id)}
                            >
                              <ChevronDown size={14} style={{ transform: selected === p.id ? 'rotate(180deg)' : 'none', transition: '0.2s' }} />
                            </button>
                          </td>
                        </tr>
                      );
                    })}
                </tbody>
              </table>
            </div>
          </div>

          {/* Expanded Explanation */}
          {selected && forecasts[selected] && (
            <div className="card" style={{ marginTop: 16, borderColor: 'var(--primary)' }}>
              <div className="card-title" style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                <Brain size={16} /> AI Explanation
              </div>
              <pre style={{
                whiteSpace: 'pre-wrap',
                fontFamily: 'Inter, sans-serif',
                fontSize: '0.85rem',
                lineHeight: 1.7,
                color: 'var(--text-secondary)',
                margin: 0,
              }}>
                {forecasts[selected].explanation}
              </pre>
              {reorders[selected] && (
                <>
                  <hr style={{ border: 'none', borderTop: '1px solid var(--border)', margin: '16px 0' }} />
                  <pre style={{
                    whiteSpace: 'pre-wrap',
                    fontFamily: 'Inter, sans-serif',
                    fontSize: '0.85rem',
                    lineHeight: 1.7,
                    color: 'var(--text-secondary)',
                    margin: 0,
                  }}>
                    {reorders[selected].explanation}
                  </pre>
                </>
              )}
              <button className="btn" style={{ marginTop: 12 }} onClick={() => setSelected(null)}>Close</button>
            </div>
          )}
        </>
      )}
    </div>
  );
}
