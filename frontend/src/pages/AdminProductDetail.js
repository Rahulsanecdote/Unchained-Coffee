import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ArrowLeft, Download } from 'lucide-react';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from 'recharts';
import AdminLayout from '../components/admin/AdminLayout';
import { adminApiCall } from '../utils/api';

const ATTR_LABELS = {
  aroma_1to9: 'Aroma',
  flavor_1to9: 'Flavor',
  aftertaste_1to9: 'Aftertaste',
  acidity_1to9: 'Acidity',
  sweetness_1to9: 'Sweetness',
  mouthfeel_1to9: 'Mouthfeel',
  overall_liking_1to9: 'Overall Liking',
};

const CHART_COLORS = ['#3E2723', '#5D4037', '#6D4C41', '#795548', '#8D6E63', '#A1887F', '#BCAAA4', '#D7CCC8', '#FFB74D'];

function DistributionChart({ data, label }) {
  const chartData = Object.entries(data).map(([k, v]) => ({ score: k, count: v }));
  return (
    <div className="bg-[var(--a-surface)] border border-[var(--a-border)] rounded-lg p-4" data-testid={`dist-chart-${label.toLowerCase()}`}>
      <h4 className="text-xs font-medium text-[var(--a-text)] mb-3">{label}</h4>
      <ResponsiveContainer width="100%" height={120}>
        <BarChart data={chartData} margin={{ top: 0, right: 0, left: -20, bottom: 0 }}>
          <XAxis dataKey="score" tick={{ fontSize: 10 }} />
          <YAxis tick={{ fontSize: 10 }} allowDecimals={false} />
          <Tooltip contentStyle={{ fontSize: 11 }} />
          <Bar dataKey="count" radius={[3, 3, 0, 0]}>
            {chartData.map((_, i) => (
              <Cell key={i} fill={CHART_COLORS[i]} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}

export default function AdminProductDetail() {
  const { productId } = useParams();
  const navigate = useNavigate();
  const [summary, setSummary] = useState(null);
  const [dateFrom, setDateFrom] = useState('');
  const [dateTo, setDateTo] = useState('');
  const [loading, setLoading] = useState(true);
  const role = localStorage.getItem('admin_role');

  const fetchSummary = async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams({ product_id: decodeURIComponent(productId) });
      if (dateFrom) params.set('from', dateFrom);
      if (dateTo) params.set('to', dateTo);
      const res = await adminApiCall(`/api/admin/products/summary?${params}`);
      const data = await res.json();
      setSummary(data);
    } catch (err) {
      if (err.message === 'Not authenticated') navigate('/admin/login');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchSummary(); }, [productId]);

  const handleExport = async () => {
    try {
      const token = localStorage.getItem('admin_token');
      const params = new URLSearchParams({ product_id: decodeURIComponent(productId) });
      if (dateFrom) params.set('from', dateFrom);
      if (dateTo) params.set('to', dateTo);
      const res = await fetch(
        `${process.env.REACT_APP_BACKEND_URL}/api/admin/export.csv?${params}`,
        { headers: { Authorization: `Bearer ${token}` } }
      );
      const blob = await res.blob();
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `responses_${productId}.csv`;
      a.click();
    } catch (err) {
      alert('Export failed: ' + err.message);
    }
  };

  return (
    <AdminLayout title={`Product: ${decodeURIComponent(productId)}`}>
      <div className="space-y-6" data-testid="admin-product-detail-page">
        <div className="flex items-center justify-between">
          <button
            onClick={() => navigate('/admin/products')}
            className="flex items-center gap-1.5 text-sm text-[var(--a-text-sec)] hover:text-[var(--a-text)] transition-colors"
            data-testid="back-to-products-btn"
          >
            <ArrowLeft size={16} /> Back to Products
          </button>
          {role === 'admin' && (
            <button
              onClick={handleExport}
              data-testid="export-csv-btn"
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg border border-[var(--a-border)]
                text-xs font-medium text-[var(--a-text)] hover:bg-gray-50 transition-colors"
            >
              <Download size={14} /> Export CSV
            </button>
          )}
        </div>

        <div className="flex gap-3 items-end">
          <div>
            <label className="block text-[10px] text-[var(--a-text-sec)] mb-1">From</label>
            <input type="date" value={dateFrom} onChange={e => setDateFrom(e.target.value)}
              className="px-2 py-1.5 rounded border border-[var(--a-border)] text-xs" data-testid="date-from-input" />
          </div>
          <div>
            <label className="block text-[10px] text-[var(--a-text-sec)] mb-1">To</label>
            <input type="date" value={dateTo} onChange={e => setDateTo(e.target.value)}
              className="px-2 py-1.5 rounded border border-[var(--a-border)] text-xs" data-testid="date-to-input" />
          </div>
          <button onClick={fetchSummary} data-testid="apply-filter-btn"
            className="px-3 py-1.5 rounded-lg bg-[var(--a-primary)] text-white text-xs font-medium hover:opacity-90">
            Apply
          </button>
        </div>

        {loading ? (
          <div className="text-center py-12 text-[var(--a-text-sec)]">Loading...</div>
        ) : summary && summary.count === 0 ? (
          <div className="text-center py-12 text-[var(--a-text-sec)]">No responses found.</div>
        ) : summary && (
          <>
            <div className="grid grid-cols-4 gap-4">
              <div className="bg-[var(--a-surface)] border border-[var(--a-border)] rounded-lg p-4">
                <p className="text-[10px] text-[var(--a-text-sec)] uppercase tracking-wider">Total Responses</p>
                <p className="text-2xl font-semibold text-[var(--a-text)] mt-1 font-mono" data-testid="total-responses">{summary.count}</p>
              </div>
              <div className="bg-[var(--a-surface)] border border-[var(--a-border)] rounded-lg p-4">
                <p className="text-[10px] text-[var(--a-text-sec)] uppercase tracking-wider">With Notes</p>
                <p className="text-2xl font-semibold text-[var(--a-text)] mt-1 font-mono">{summary.notes_count}</p>
              </div>
              <div className="bg-[var(--a-surface)] border border-[var(--a-border)] rounded-lg p-4">
                <p className="text-[10px] text-[var(--a-text-sec)] uppercase tracking-wider">Preferences</p>
                <p className="text-2xl font-semibold text-[var(--a-text)] mt-1 font-mono">{summary.mode_breakdown?.preference_only || 0}</p>
              </div>
              <div className="bg-[var(--a-surface)] border border-[var(--a-border)] rounded-lg p-4">
                <p className="text-[10px] text-[var(--a-text-sec)] uppercase tracking-wider">Tasted</p>
                <p className="text-2xl font-semibold text-[var(--a-text)] mt-1 font-mono">{summary.mode_breakdown?.tasted || 0}</p>
              </div>
            </div>

            <div>
              <h3 className="text-sm font-medium text-[var(--a-text)] mb-3">Averages</h3>
              <div className="grid grid-cols-4 gap-3">
                {Object.entries(summary.averages).map(([key, avg]) => (
                  <div key={key} className="bg-[var(--a-surface)] border border-[var(--a-border)] rounded-lg p-3 text-center">
                    <p className="text-[10px] text-[var(--a-text-sec)]">{ATTR_LABELS[key] || key}</p>
                    <p className="text-xl font-semibold text-[var(--a-primary)] mt-1 font-mono">{avg}</p>
                  </div>
                ))}
              </div>
            </div>

            <div>
              <h3 className="text-sm font-medium text-[var(--a-text)] mb-3">Distributions</h3>
              <div className="grid grid-cols-2 gap-4">
                {Object.entries(summary.distributions).map(([key, dist]) => (
                  <DistributionChart key={key} data={dist} label={ATTR_LABELS[key] || key} />
                ))}
              </div>
            </div>

            {Object.keys(summary.standout_tags).length > 0 && (
              <div>
                <h3 className="text-sm font-medium text-[var(--a-text)] mb-3">Standout Tags</h3>
                <div className="flex flex-wrap gap-2">
                  {Object.entries(summary.standout_tags).sort((a, b) => b[1] - a[1]).map(([tag, count]) => (
                    <span key={tag} className="px-3 py-1.5 rounded-full text-xs font-medium bg-[var(--a-primary)]/10 text-[var(--a-primary)]">
                      {tag} <span className="font-mono ml-1 opacity-60">({count})</span>
                    </span>
                  ))}
                </div>
              </div>
            )}

            {Object.keys(summary.fit_tags).length > 0 && (
              <div>
                <h3 className="text-sm font-medium text-[var(--a-text)] mb-3">Fit Feedback</h3>
                <div className="flex flex-wrap gap-2">
                  {Object.entries(summary.fit_tags).sort((a, b) => b[1] - a[1]).map(([tag, count]) => (
                    <span key={tag} className="px-3 py-1.5 rounded-full text-xs font-medium bg-red-50 text-red-700">
                      {tag} <span className="font-mono ml-1 opacity-60">({count})</span>
                    </span>
                  ))}
                </div>
              </div>
            )}
          </>
        )}
      </div>
    </AdminLayout>
  );
}
