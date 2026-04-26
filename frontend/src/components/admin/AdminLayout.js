import React from 'react';
import { NavLink, useNavigate } from 'react-router-dom';
import { BarChart3, Users, Filter, Trash2, LogOut, Coffee } from 'lucide-react';

const NAV_ITEMS = [
  { path: '/admin/products', label: 'Products', icon: BarChart3 },
  { path: '/admin/funnel', label: 'Funnel', icon: Filter },
  { path: '/admin/segments', label: 'Segments', icon: Users },
  { path: '/admin/privacy', label: 'Privacy', icon: Trash2 },
];

export default function AdminLayout({ children, title }) {
  const navigate = useNavigate();
  const role = localStorage.getItem('admin_role');
  const email = localStorage.getItem('admin_email');

  const handleLogout = () => {
    localStorage.removeItem('admin_token');
    localStorage.removeItem('admin_role');
    localStorage.removeItem('admin_email');
    navigate('/admin/login');
  };

  const token = localStorage.getItem('admin_token');
  if (!token) {
    navigate('/admin/login');
    return null;
  }

  return (
    <div className="min-h-screen bg-[var(--a-bg)] flex" data-testid="admin-layout">
      <aside className="w-56 bg-[var(--a-surface)] border-r border-[var(--a-border)] flex flex-col fixed h-full z-10">
        <div className="px-5 py-5 border-b border-[var(--a-border)]">
          <div className="flex items-center gap-2">
            <Coffee size={20} className="text-[var(--a-primary)]" />
            <span className="font-heading font-semibold text-[var(--a-text)]">Taste Fit</span>
          </div>
          <p className="text-[10px] text-[var(--a-text-sec)] mt-1 uppercase tracking-wider">Admin Dashboard</p>
        </div>

        <nav className="flex-1 py-3 px-3 space-y-0.5">
          {NAV_ITEMS.map(item => (
            <NavLink
              key={item.path}
              to={item.path}
              data-testid={`nav-${item.label.toLowerCase()}`}
              className={({ isActive }) =>
                `flex items-center gap-2.5 px-3 py-2 rounded-md text-sm transition-colors
                ${isActive
                  ? 'bg-[var(--a-primary)] text-white font-medium'
                  : 'text-[var(--a-text-sec)] hover:text-[var(--a-text)] hover:bg-gray-50'
                }`
              }
            >
              <item.icon size={16} />
              {item.label}
            </NavLink>
          ))}
        </nav>

        <div className="px-4 py-4 border-t border-[var(--a-border)]">
          <p className="text-xs text-[var(--a-text)] truncate">{email}</p>
          <p className="text-[10px] text-[var(--a-text-sec)] uppercase">{role}</p>
          <button
            onClick={handleLogout}
            data-testid="logout-btn"
            className="flex items-center gap-1.5 text-xs text-[var(--a-text-sec)] hover:text-[var(--a-primary)] mt-2 transition-colors"
          >
            <LogOut size={13} /> Sign out
          </button>
        </div>
      </aside>

      <main className="flex-1 ml-56">
        <div className="px-8 py-6 border-b border-[var(--a-border)] bg-[var(--a-surface)]">
          <h1 className="text-xl font-semibold text-[var(--a-text)]" data-testid="page-title">{title}</h1>
        </div>
        <div className="p-8">
          {children}
        </div>
      </main>
    </div>
  );
}
