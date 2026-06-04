import { useState, useEffect } from 'react';
import { Plus, Pencil, Trash2 } from 'lucide-react';
import { fetchProducts, fetchCategories, createProduct, deleteProduct, toggleAvailability } from '../api';

export default function Products() {
  const [products, setProducts] = useState([]);
  const [categories, setCategories] = useState([]);
  const [filter, setFilter] = useState('');
  const [showForm, setShowForm] = useState(false);
  const [loading, setLoading] = useState(true);
  const [form, setForm] = useState({ product_name: '', category: '', price: '', sku: '', description: '' });

  const load = () => {
    setLoading(true);
    Promise.all([fetchProducts(filter || undefined), fetchCategories()])
      .then(([p, c]) => { setProducts(p); setCategories(c); })
      .catch(console.error)
      .finally(() => setLoading(false));
  };

  useEffect(load, [filter]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    await createProduct({ ...form, price: parseFloat(form.price) });
    setForm({ product_name: '', category: '', price: '', sku: '', description: '' });
    setShowForm(false);
    load();
  };

  const handleDelete = async (id, name) => {
    if (!confirm(`Delete "${name}"?`)) return;
    await deleteProduct(id);
    load();
  };

  const handleToggle = async (id) => {
    await toggleAvailability(id);
    load();
  };

  return (
    <div>
      <div className="page-header">
        <div>
          <h2>Product Catalog</h2>
          <p>{products.length} products</p>
        </div>
        <button className="btn btn-primary" onClick={() => setShowForm(true)}><Plus size={16} /> Add Product</button>
      </div>

      <div className="card" style={{ marginBottom: 20, padding: '12px 16px' }}>
        <select className="form-select" value={filter} onChange={(e) => setFilter(e.target.value)} style={{ maxWidth: 200 }}>
          <option value="">All Categories</option>
          {categories.map((c) => <option key={c} value={c}>{c}</option>)}
        </select>
      </div>

      {loading ? <div className="loading">Loading products...</div> : (
        <div className="card">
          <div className="table-wrapper">
            <table className="table">
              <thead>
                <tr><th>ID</th><th>Name</th><th>Category</th><th>Price</th><th>SKU</th><th>Available</th><th>Actions</th></tr>
              </thead>
              <tbody>
                {products.map((p) => (
                  <tr key={p.id}>
                    <td>{p.id}</td>
                    <td style={{ fontWeight: 600 }}>{p.product_name}</td>
                    <td><span className="badge badge-purple">{p.category}</span></td>
                    <td>₹{p.price.toLocaleString('en-IN')}</td>
                    <td style={{ color: 'var(--text-muted)' }}>{p.sku || '—'}</td>
                    <td><button className={`toggle ${p.available ? 'active' : ''}`} onClick={() => handleToggle(p.id)} /></td>
                    <td>
                      <button className="btn-icon" title="Delete" onClick={() => handleDelete(p.id, p.product_name)}><Trash2 size={16} /></button>
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
            <h3>Add New Product</h3>
            <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
              <div className="form-group"><label className="form-label">Product Name *</label><input className="form-input" required value={form.product_name} onChange={(e) => setForm({ ...form, product_name: e.target.value })} /></div>
              <div className="form-row">
                <div className="form-group"><label className="form-label">Category *</label><input className="form-input" required value={form.category} onChange={(e) => setForm({ ...form, category: e.target.value })} /></div>
                <div className="form-group"><label className="form-label">Price (₹) *</label><input className="form-input" type="number" step="0.01" required value={form.price} onChange={(e) => setForm({ ...form, price: e.target.value })} /></div>
              </div>
              <div className="form-group"><label className="form-label">SKU</label><input className="form-input" value={form.sku} onChange={(e) => setForm({ ...form, sku: e.target.value })} /></div>
              <div className="form-group"><label className="form-label">Description</label><textarea className="form-textarea" value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} /></div>
              <div className="modal-actions">
                <button type="button" className="btn" onClick={() => setShowForm(false)}>Cancel</button>
                <button type="submit" className="btn btn-primary">Create Product</button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
