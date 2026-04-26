import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Coffee, Loader2, Eye, EyeOff } from 'lucide-react';
import { apiCall } from '../utils/api';

export default function AdminLogin() {
  const navigate = useNavigate();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPw, setShowPw] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    try {
      const res = await apiCall('/api/auth/login', {
        method: 'POST',
        body: JSON.stringify({ email, password }),
      }, 1);
      const data = await res.json();
      localStorage.setItem('admin_token', data.token);
      localStorage.setItem('admin_role', data.role);
      localStorage.setItem('admin_email', data.email);
      navigate('/admin/products');
    } catch (err) {
      setError(err.message || 'Invalid credentials');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-[var(--a-bg)] flex items-center justify-center px-4" data-testid="admin-login-page">
      <div className="w-full max-w-sm">
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-14 h-14 rounded-2xl bg-[var(--a-primary)] mb-4">
            <Coffee size={28} className="text-white" />
          </div>
          <h1 className="font-heading text-2xl font-semibold text-[var(--a-text)]">Taste Fit Admin</h1>
          <p className="text-sm text-[var(--a-text-sec)] mt-1">Unchained Coffee Analytics</p>
        </div>

        <form onSubmit={handleSubmit} className="bg-[var(--a-surface)] rounded-xl border border-[var(--a-border)] p-6 space-y-4">
          <div>
            <label className="block text-xs font-medium text-[var(--a-text)] mb-1.5">Email</label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              data-testid="login-email-input"
              className="w-full px-3 py-2 rounded-lg border border-[var(--a-border)] text-sm text-[var(--a-text)]
                focus:outline-none focus:ring-2 focus:ring-[var(--a-primary)]/20 focus:border-[var(--a-primary)]"
              placeholder="admin@unchainedcoffee.com"
              required
            />
          </div>
          <div>
            <label className="block text-xs font-medium text-[var(--a-text)] mb-1.5">Password</label>
            <div className="relative">
              <input
                type={showPw ? 'text' : 'password'}
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                data-testid="login-password-input"
                className="w-full px-3 py-2 pr-10 rounded-lg border border-[var(--a-border)] text-sm text-[var(--a-text)]
                  focus:outline-none focus:ring-2 focus:ring-[var(--a-primary)]/20 focus:border-[var(--a-primary)]"
                placeholder="Enter password"
                required
              />
              <button
                type="button"
                onClick={() => setShowPw(!showPw)}
                className="absolute right-3 top-1/2 -translate-y-1/2 text-[var(--a-text-sec)]"
              >
                {showPw ? <EyeOff size={16} /> : <Eye size={16} />}
              </button>
            </div>
          </div>

          {error && (
            <div className="bg-red-50 border border-red-200 rounded-lg px-3 py-2" data-testid="login-error">
              <p className="text-xs text-red-600">{error}</p>
            </div>
          )}

          <button
            type="submit"
            disabled={loading}
            data-testid="login-submit-btn"
            className="w-full py-2.5 rounded-lg bg-[var(--a-primary)] text-white text-sm font-medium
              hover:opacity-90 transition-opacity disabled:opacity-50"
          >
            {loading ? (
              <span className="flex items-center justify-center gap-2">
                <Loader2 size={16} className="animate-spin" /> Signing in...
              </span>
            ) : 'Sign In'}
          </button>
        </form>
      </div>
    </div>
  );
}
