import { useState, useEffect } from 'react';
import { Save, CheckCircle } from 'lucide-react';
import { fetchStore, updateStore } from '../api';

export default function Settings() {
  const [form, setForm] = useState({
    name: '', owner_name: '', email: '', phone: '', address: '',
    opening_time: '09:00', closing_time: '21:00',
    delivery_radius_km: 5, min_order_amount: 200, is_open: true,
  });
  const [loading, setLoading] = useState(true);
  const [saved, setSaved] = useState(false);

  useEffect(() => {
    fetchStore()
      .then((s) => setForm({
        name: s.name || '', owner_name: s.owner_name || '', email: s.email || '', phone: s.phone || '',
        address: s.address || '', opening_time: s.opening_time || '09:00', closing_time: s.closing_time || '21:00',
        delivery_radius_km: s.delivery_radius_km || 5, min_order_amount: s.min_order_amount || 200, is_open: s.is_open ?? true,
      }))
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  const handleSave = async (e) => {
    e.preventDefault();
    await updateStore(form);
    setSaved(true);
    setTimeout(() => setSaved(false), 3000);
  };

  const update = (field, val) => setForm({ ...form, [field]: val });

  if (loading) return <div className="loading">Loading settings...</div>;

  return (
    <div>
      <div className="page-header">
        <div><h2>Store Settings</h2><p>Configure your store profile and operations</p></div>
      </div>

      {saved && <div className="alert alert-success"><CheckCircle size={16} /> Settings saved successfully!</div>}

      <form onSubmit={handleSave} style={{ display: 'flex', flexDirection: 'column', gap: 20, maxWidth: 700 }}>
        <div className="card">
          <div className="card-title">Operating Status</div>
          <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
            <button type="button" className={`toggle ${form.is_open ? 'active' : ''}`} onClick={() => update('is_open', !form.is_open)} />
            <span style={{ fontWeight: 600 }}>{form.is_open ? 'Store Open' : 'Store Closed'}</span>
          </div>
        </div>

        <div className="card">
          <div className="card-title">Profile Details</div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
            <div className="form-row">
              <div className="form-group"><label className="form-label">Store Name</label><input className="form-input" value={form.name} onChange={(e) => update('name', e.target.value)} /></div>
              <div className="form-group"><label className="form-label">Owner Name</label><input className="form-input" value={form.owner_name} onChange={(e) => update('owner_name', e.target.value)} /></div>
            </div>
            <div className="form-row">
              <div className="form-group"><label className="form-label">Email</label><input className="form-input" type="email" value={form.email} onChange={(e) => update('email', e.target.value)} /></div>
              <div className="form-group"><label className="form-label">Phone</label><input className="form-input" value={form.phone} onChange={(e) => update('phone', e.target.value)} /></div>
            </div>
            <div className="form-group"><label className="form-label">Address</label><input className="form-input" value={form.address} onChange={(e) => update('address', e.target.value)} /></div>
          </div>
        </div>

        <div className="card">
          <div className="card-title">Delivery & Hours</div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
            <div className="form-row">
              <div className="form-group"><label className="form-label">Opening Time</label><input className="form-input" type="time" value={form.opening_time} onChange={(e) => update('opening_time', e.target.value)} /></div>
              <div className="form-group"><label className="form-label">Closing Time</label><input className="form-input" type="time" value={form.closing_time} onChange={(e) => update('closing_time', e.target.value)} /></div>
            </div>
            <div className="form-row">
              <div className="form-group"><label className="form-label">Delivery Radius (km)</label><input className="form-input" type="number" value={form.delivery_radius_km} onChange={(e) => update('delivery_radius_km', parseFloat(e.target.value))} /></div>
              <div className="form-group"><label className="form-label">Min Order Amount (₹)</label><input className="form-input" type="number" value={form.min_order_amount} onChange={(e) => update('min_order_amount', parseFloat(e.target.value))} /></div>
            </div>
          </div>
        </div>

        <button type="submit" className="btn btn-primary" style={{ alignSelf: 'flex-end' }}><Save size={16} /> Save Settings</button>
      </form>
    </div>
  );
}
