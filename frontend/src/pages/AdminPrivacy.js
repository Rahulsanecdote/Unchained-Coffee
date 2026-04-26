import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Trash2, AlertTriangle, CheckCircle, Loader2 } from 'lucide-react';
import AdminLayout from '../components/admin/AdminLayout';
import { adminApiCall } from '../utils/api';

export default function AdminPrivacy() {
  const navigate = useNavigate();
  const [identifier, setIdentifier] = useState('');
  const [idType, setIdType] = useState('session_id');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState('');
  const [confirmOpen, setConfirmOpen] = useState(false);
  const role = localStorage.getItem('admin_role');

  const handleDelete = async () => {
    if (!identifier.trim()) {
      setError('Please enter an identifier');
      return;
    }
    setLoading(true);
    setError('');
    setResult(null);
    try {
      const params = new URLSearchParams({ [idType]: identifier.trim() });
      const res = await adminApiCall(`/api/admin/data?${params}`, { method: 'DELETE' });
      const data = await res.json();
      setResult(data.deleted);
      setConfirmOpen(false);
    } catch (err) {
      if (err.message === 'Not authenticated') return navigate('/admin/login');
      setError(err.message || 'Deletion failed');
      setConfirmOpen(false);
    } finally {
      setLoading(false);
    }
  };

  return (
    <AdminLayout title="Privacy Operations">
      <div className="max-w-xl space-y-6" data-testid="admin-privacy-page">
        {role !== 'admin' && (
          <div className="bg-amber-50 border border-amber-200 rounded-lg px-4 py-3" data-testid="viewer-warning">
            <div className="flex items-center gap-2">
              <AlertTriangle size={16} className="text-amber-600" />
              <p className="text-xs text-amber-700">Viewer role cannot perform deletions. Admin access required.</p>
            </div>
          </div>
        )}

        <div className="bg-[var(--a-surface)] border border-[var(--a-border)] rounded-xl p-6 space-y-4">
          <div className="flex items-center gap-2 text-[var(--a-text)]">
            <Trash2 size={18} />
            <h3 className="text-sm font-medium">Delete User Data</h3>
          </div>
          <p className="text-xs text-[var(--a-text-sec)]">
            Permanently delete all taste profiles, responses, and events for a given session or consumer.
            This action cannot be undone.
          </p>

          <div className="space-y-3">
            <div>
              <label className="block text-xs font-medium text-[var(--a-text)] mb-1.5">Identifier Type</label>
              <div className="flex gap-2">
                <button
                  onClick={() => setIdType('session_id')}
                  data-testid="id-type-session-btn"
                  className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-colors
                    ${idType === 'session_id'
                      ? 'bg-[var(--a-primary)] text-white'
                      : 'border border-[var(--a-border)] text-[var(--a-text-sec)] hover:bg-gray-50'
                    }`}
                >
                  Session ID
                </button>
                <button
                  onClick={() => setIdType('consumer_id')}
                  data-testid="id-type-consumer-btn"
                  className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-colors
                    ${idType === 'consumer_id'
                      ? 'bg-[var(--a-primary)] text-white'
                      : 'border border-[var(--a-border)] text-[var(--a-text-sec)] hover:bg-gray-50'
                    }`}
                >
                  Consumer ID
                </button>
              </div>
            </div>

            <div>
              <label className="block text-xs font-medium text-[var(--a-text)] mb-1.5">
                {idType === 'session_id' ? 'Session ID' : 'Consumer ID'}
              </label>
              <input
                value={identifier}
                onChange={(e) => setIdentifier(e.target.value)}
                placeholder={`Enter ${idType.replace('_', ' ')}...`}
                data-testid="privacy-identifier-input"
                className="w-full px-3 py-2 rounded-lg border border-[var(--a-border)] text-sm
                  focus:outline-none focus:ring-2 focus:ring-[var(--a-primary)]/20"
              />
            </div>
          </div>

          {error && (
            <div className="bg-red-50 border border-red-200 rounded-lg px-3 py-2" data-testid="privacy-error">
              <p className="text-xs text-red-600">{error}</p>
            </div>
          )}

          {result && (
            <div className="bg-green-50 border border-green-200 rounded-lg px-4 py-3" data-testid="privacy-success">
              <div className="flex items-center gap-2 mb-2">
                <CheckCircle size={16} className="text-green-600" />
                <span className="text-xs font-medium text-green-700">Data deleted successfully</span>
              </div>
              <div className="text-xs text-green-700 space-y-0.5 font-mono">
                <p>Profiles: {result.profiles}</p>
                <p>Responses: {result.responses}</p>
                <p>Events: {result.events}</p>
              </div>
            </div>
          )}

          {!confirmOpen ? (
            <button
              onClick={() => setConfirmOpen(true)}
              disabled={role !== 'admin' || !identifier.trim()}
              data-testid="delete-initiate-btn"
              className="w-full py-2.5 rounded-lg bg-red-600 text-white text-sm font-medium
                hover:bg-red-700 transition-colors disabled:opacity-40 disabled:cursor-not-allowed"
            >
              Delete Data
            </button>
          ) : (
            <div className="bg-red-50 border border-red-300 rounded-lg p-4 space-y-3">
              <div className="flex items-center gap-2">
                <AlertTriangle size={16} className="text-red-600" />
                <span className="text-xs font-medium text-red-700">This will permanently delete all data for this identifier.</span>
              </div>
              <div className="flex gap-2">
                <button
                  onClick={handleDelete}
                  disabled={loading}
                  data-testid="confirm-delete-btn"
                  className="flex-1 py-2 rounded-lg bg-red-600 text-white text-xs font-medium hover:bg-red-700 disabled:opacity-60"
                >
                  {loading ? <Loader2 size={14} className="animate-spin mx-auto" /> : 'Confirm Delete'}
                </button>
                <button
                  onClick={() => setConfirmOpen(false)}
                  data-testid="cancel-delete-btn"
                  className="flex-1 py-2 rounded-lg border border-[var(--a-border)] text-xs font-medium text-[var(--a-text-sec)]"
                >
                  Cancel
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </AdminLayout>
  );
}
