import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Search, ChevronRight, FileBarChart } from 'lucide-react';
import AdminLayout from '../components/admin/AdminLayout';
import { adminApiCall } from '../utils/api';

export default function AdminProducts() {
  const navigate = useNavigate();
  const [products, setProducts] = useState([]);
  const [search, setSearch] = useState('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchProducts = async () => {
      try {
        const res = await adminApiCall(`/api/admin/products${search ? `?search=${search}` : ''}`);
        const data = await res.json();
        setProducts(data.products);
      } catch (err) {
        if (err.message === 'Not authenticated') navigate('/admin/login');
      } finally {
        setLoading(false);
      }
    };
    fetchProducts();
  }, [search, navigate]);

  return (
    <AdminLayout title="Products">
      <div className="space-y-6" data-testid="admin-products-page">
        <div className="relative max-w-md">
          <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-[var(--a-text-sec)]" />
          <input
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search by product ID..."
            data-testid="product-search-input"
            className="w-full pl-9 pr-4 py-2 rounded-lg border border-[var(--a-border)] text-sm
              focus:outline-none focus:ring-2 focus:ring-[var(--a-primary)]/20 focus:border-[var(--a-primary)]"
          />
        </div>

        {loading ? (
          <div className="text-center py-12 text-[var(--a-text-sec)]">Loading...</div>
        ) : products.length === 0 ? (
          <div className="text-center py-12" data-testid="no-products">
            <FileBarChart size={40} className="mx-auto text-[var(--a-text-sec)] opacity-40 mb-3" />
            <p className="text-sm text-[var(--a-text-sec)]">No product responses yet.</p>
            <p className="text-xs text-[var(--a-text-sec)] mt-1">Submit some tastings via the widget to see data here.</p>
          </div>
        ) : (
          <div className="bg-[var(--a-surface)] rounded-xl border border-[var(--a-border)] overflow-hidden">
            <table className="w-full">
              <thead>
                <tr className="border-b border-[var(--a-border)]">
                  <th className="text-left px-4 py-3 text-xs font-medium text-[var(--a-text-sec)] uppercase tracking-wider">Product ID</th>
                  <th className="text-left px-4 py-3 text-xs font-medium text-[var(--a-text-sec)] uppercase tracking-wider">Responses</th>
                  <th className="text-left px-4 py-3 text-xs font-medium text-[var(--a-text-sec)] uppercase tracking-wider">Modes</th>
                  <th className="text-left px-4 py-3 text-xs font-medium text-[var(--a-text-sec)] uppercase tracking-wider">Last Activity</th>
                  <th className="px-4 py-3"></th>
                </tr>
              </thead>
              <tbody>
                {products.map(p => (
                  <tr
                    key={p.product_id}
                    onClick={() => navigate(`/admin/products/${encodeURIComponent(p.product_id)}`)}
                    className="border-b border-[var(--a-border)] last:border-0 hover:bg-gray-50 cursor-pointer transition-colors"
                    data-testid={`product-row-${p.product_id}`}
                  >
                    <td className="px-4 py-3 text-sm font-medium text-[var(--a-text)] font-mono">{p.product_id}</td>
                    <td className="px-4 py-3 text-sm text-[var(--a-text)]">{p.response_count}</td>
                    <td className="px-4 py-3">
                      <div className="flex gap-1">
                        {p.modes.map(m => (
                          <span key={m} className="px-2 py-0.5 rounded-full text-[10px] font-medium bg-gray-100 text-[var(--a-text-sec)]">
                            {m}
                          </span>
                        ))}
                      </div>
                    </td>
                    <td className="px-4 py-3 text-xs text-[var(--a-text-sec)] font-mono">
                      {new Date(p.last_response).toLocaleDateString()}
                    </td>
                    <td className="px-4 py-3">
                      <ChevronRight size={16} className="text-[var(--a-text-sec)]" />
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </AdminLayout>
  );
}
