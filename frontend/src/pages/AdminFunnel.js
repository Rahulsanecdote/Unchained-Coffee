import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from 'recharts';
import AdminLayout from '../components/admin/AdminLayout';
import { adminApiCall } from '../utils/api';

const FUNNEL_LABELS = {
  product_viewed: 'Product Viewed',
  affective_form_viewed: 'Widget Loaded',
  affective_form_opened: 'Form Opened',
  affective_form_submitted: 'Form Submitted',
};

const COLORS = ['#3E2723', '#6D4C41', '#8D6E63', '#FFB74D'];

export default function AdminFunnel() {
  const navigate = useNavigate();
  const [funnel, setFunnel] = useState(null);
  const [dateFrom, setDateFrom] = useState('');
  const [dateTo, setDateTo] = useState('');
  const [loading, setLoading] = useState(true);

  const fetchFunnel = async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams();
      if (dateFrom) params.set('from', dateFrom);
      if (dateTo) params.set('to', dateTo);
      const res = await adminApiCall(`/api/admin/funnel?${params}`);
      const data = await res.json();
      setFunnel(data.funnel);
    } catch (err) {
      if (err.message === 'Not authenticated') navigate('/admin/login');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchFunnel(); }, []);

  const chartData = funnel
    ? Object.entries(funnel).map(([key, count]) => ({
        step: FUNNEL_LABELS[key] || key,
        count,
      }))
    : [];

  const maxCount = Math.max(...chartData.map(d => d.count), 1);

  return (
    <AdminLayout title="Funnel Analytics">
      <div className="space-y-6" data-testid="admin-funnel-page">
        <div className="flex gap-3 items-end">
          <div>
            <label className="block text-[10px] text-[var(--a-text-sec)] mb-1">From</label>
            <input type="date" value={dateFrom} onChange={e => setDateFrom(e.target.value)}
              className="px-2 py-1.5 rounded border border-[var(--a-border)] text-xs" data-testid="funnel-date-from" />
          </div>
          <div>
            <label className="block text-[10px] text-[var(--a-text-sec)] mb-1">To</label>
            <input type="date" value={dateTo} onChange={e => setDateTo(e.target.value)}
              className="px-2 py-1.5 rounded border border-[var(--a-border)] text-xs" data-testid="funnel-date-to" />
          </div>
          <button onClick={fetchFunnel} data-testid="funnel-apply-btn"
            className="px-3 py-1.5 rounded-lg bg-[var(--a-primary)] text-white text-xs font-medium hover:opacity-90">
            Apply
          </button>
        </div>

        {loading ? (
          <div className="text-center py-12 text-[var(--a-text-sec)]">Loading...</div>
        ) : (
          <>
            <div className="bg-[var(--a-surface)] border border-[var(--a-border)] rounded-xl p-6">
              <h3 className="text-sm font-medium text-[var(--a-text)] mb-4">Conversion Funnel</h3>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={chartData} layout="vertical" margin={{ left: 20, right: 20, top: 10, bottom: 10 }}>
                  <XAxis type="number" tick={{ fontSize: 11 }} allowDecimals={false} />
                  <YAxis type="category" dataKey="step" tick={{ fontSize: 11 }} width={130} />
                  <Tooltip contentStyle={{ fontSize: 12 }} />
                  <Bar dataKey="count" radius={[0, 4, 4, 0]}>
                    {chartData.map((_, i) => (
                      <Cell key={i} fill={COLORS[i % COLORS.length]} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>

            <div className="grid grid-cols-4 gap-4">
              {chartData.map((item, i) => {
                const rate = i > 0 && chartData[i - 1].count > 0
                  ? ((item.count / chartData[i - 1].count) * 100).toFixed(1)
                  : null;
                return (
                  <div key={item.step} className="bg-[var(--a-surface)] border border-[var(--a-border)] rounded-lg p-4">
                    <p className="text-[10px] text-[var(--a-text-sec)] uppercase tracking-wider">{item.step}</p>
                    <p className="text-2xl font-semibold text-[var(--a-text)] mt-1 font-mono" data-testid={`funnel-count-${i}`}>{item.count}</p>
                    {rate !== null && (
                      <p className="text-xs text-[var(--a-text-sec)] mt-0.5">
                        <span className="font-mono">{rate}%</span> from prev
                      </p>
                    )}
                    <div className="mt-2 h-1.5 bg-gray-100 rounded-full overflow-hidden">
                      <div
                        className="h-full rounded-full transition-all"
                        style={{
                          width: `${(item.count / maxCount) * 100}%`,
                          backgroundColor: COLORS[i % COLORS.length],
                        }}
                      />
                    </div>
                  </div>
                );
              })}
            </div>
          </>
        )}
      </div>
    </AdminLayout>
  );
}
