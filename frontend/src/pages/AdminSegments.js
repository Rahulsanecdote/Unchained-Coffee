import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Legend, Cell } from 'recharts';
import AdminLayout from '../components/admin/AdminLayout';
import { adminApiCall } from '../utils/api';

const ATTR_LABELS = {
  aroma_pref_1to9: 'Aroma',
  flavor_pref_1to9: 'Flavor',
  aftertaste_pref_1to9: 'Aftertaste',
  acidity_pref_1to9: 'Acidity',
  sweetness_pref_1to9: 'Sweetness',
  mouthfeel_pref_1to9: 'Mouthfeel',
};

const BAND_COLORS = { low_1_3: '#8D6E63', mid_4_6: '#D7CCC8', high_7_9: '#FFB74D' };
const BAND_LABELS = { low_1_3: 'Low (1-3)', mid_4_6: 'Mid (4-6)', high_7_9: 'High (7-9)' };

export default function AdminSegments() {
  const navigate = useNavigate();
  const [segments, setSegments] = useState(null);
  const [totalProfiles, setTotalProfiles] = useState(0);
  const [dateFrom, setDateFrom] = useState('');
  const [dateTo, setDateTo] = useState('');
  const [loading, setLoading] = useState(true);

  const fetchSegments = async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams();
      if (dateFrom) params.set('from', dateFrom);
      if (dateTo) params.set('to', dateTo);
      const res = await adminApiCall(`/api/admin/segments?${params}`);
      const data = await res.json();
      setSegments(data.segments);
      setTotalProfiles(data.total_profiles);
    } catch (err) {
      if (err.message === 'Not authenticated') navigate('/admin/login');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchSegments(); }, []);

  const chartData = segments
    ? Object.entries(segments).map(([attr, bands]) => ({
        attribute: ATTR_LABELS[attr] || attr,
        ...bands,
      }))
    : [];

  return (
    <AdminLayout title="Preference Segments">
      <div className="space-y-6" data-testid="admin-segments-page">
        <div className="flex gap-3 items-end">
          <div>
            <label className="block text-[10px] text-[var(--a-text-sec)] mb-1">From</label>
            <input type="date" value={dateFrom} onChange={e => setDateFrom(e.target.value)}
              className="px-2 py-1.5 rounded border border-[var(--a-border)] text-xs" data-testid="segments-date-from" />
          </div>
          <div>
            <label className="block text-[10px] text-[var(--a-text-sec)] mb-1">To</label>
            <input type="date" value={dateTo} onChange={e => setDateTo(e.target.value)}
              className="px-2 py-1.5 rounded border border-[var(--a-border)] text-xs" data-testid="segments-date-to" />
          </div>
          <button onClick={fetchSegments} data-testid="segments-apply-btn"
            className="px-3 py-1.5 rounded-lg bg-[var(--a-primary)] text-white text-xs font-medium hover:opacity-90">
            Apply
          </button>
        </div>

        {loading ? (
          <div className="text-center py-12 text-[var(--a-text-sec)]">Loading...</div>
        ) : (
          <>
            <div className="bg-[var(--a-surface)] border border-[var(--a-border)] rounded-lg p-4">
              <p className="text-[10px] text-[var(--a-text-sec)] uppercase tracking-wider">Total Profiles</p>
              <p className="text-2xl font-semibold text-[var(--a-text)] font-mono" data-testid="total-profiles">{totalProfiles}</p>
            </div>

            <div className="bg-[var(--a-surface)] border border-[var(--a-border)] rounded-xl p-6">
              <h3 className="text-sm font-medium text-[var(--a-text)] mb-4">Preference Bands by Attribute</h3>
              <ResponsiveContainer width="100%" height={350}>
                <BarChart data={chartData} margin={{ left: 10, right: 20, top: 10, bottom: 10 }}>
                  <XAxis dataKey="attribute" tick={{ fontSize: 11 }} />
                  <YAxis tick={{ fontSize: 11 }} allowDecimals={false} />
                  <Tooltip contentStyle={{ fontSize: 12 }} />
                  <Legend wrapperStyle={{ fontSize: 11 }} />
                  {Object.entries(BAND_COLORS).map(([band, color]) => (
                    <Bar key={band} dataKey={band} name={BAND_LABELS[band]} fill={color} stackId="a" radius={[2, 2, 0, 0]} />
                  ))}
                </BarChart>
              </ResponsiveContainer>
            </div>

            <div className="grid grid-cols-3 gap-4">
              {chartData.map(item => (
                <div key={item.attribute} className="bg-[var(--a-surface)] border border-[var(--a-border)] rounded-lg p-4">
                  <h4 className="text-xs font-medium text-[var(--a-text)] mb-3">{item.attribute}</h4>
                  {Object.entries(BAND_LABELS).map(([band, label]) => {
                    const total = item.low_1_3 + item.mid_4_6 + item.high_7_9;
                    const pct = total > 0 ? ((item[band] / total) * 100).toFixed(0) : 0;
                    return (
                      <div key={band} className="flex items-center gap-2 mb-2">
                        <div className="w-2 h-2 rounded-full" style={{ backgroundColor: BAND_COLORS[band] }} />
                        <span className="text-[11px] text-[var(--a-text-sec)] flex-1">{label}</span>
                        <span className="text-xs font-mono text-[var(--a-text)]">{item[band]}</span>
                        <span className="text-[10px] text-[var(--a-text-sec)] font-mono w-10 text-right">{pct}%</span>
                      </div>
                    );
                  })}
                </div>
              ))}
            </div>
          </>
        )}
      </div>
    </AdminLayout>
  );
}
