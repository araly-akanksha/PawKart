import { NavLink } from 'react-router-dom';
import {
  PawPrint, LayoutDashboard, Package, Warehouse,
  ShoppingCart, Radio, Brain, BarChart3, Settings
} from 'lucide-react';

const navItems = [
  { to: '/', icon: LayoutDashboard, label: 'Dashboard' },
  { to: '/products', icon: Package, label: 'Products' },
  { to: '/inventory', icon: Warehouse, label: 'Inventory' },
  { to: '/orders', icon: ShoppingCart, label: 'Orders' },
  { to: '/rfid', icon: Radio, label: 'RFID Monitor' },
  { to: '/forecast', icon: Brain, label: 'AI Forecast' },
  { to: '/analytics', icon: BarChart3, label: 'Analytics' },
  { to: '/settings', icon: Settings, label: 'Settings' },
];

export default function Sidebar() {
  return (
    <aside className="sidebar">
      <div className="sidebar-logo">
        <PawPrint size={28} />
        <h1>PawKart</h1>
      </div>
      <nav className="sidebar-nav">
        {navItems.map(({ to, icon: Icon, label }) => (
          <NavLink
            key={to}
            to={to}
            end={to === '/'}
            className={({ isActive }) => isActive ? 'active' : ''}
          >
            <Icon size={20} />
            {label}
          </NavLink>
        ))}
      </nav>
      <div className="sidebar-footer">PawKart v2.0 — AI Inventory System</div>
    </aside>
  );
}
