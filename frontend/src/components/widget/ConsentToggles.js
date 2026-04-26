import React from 'react';
import { Shield, ShieldCheck } from 'lucide-react';

export default function ConsentToggles({ consentAnalytics, consentMarketing, onChange }) {
  return (
    <div className="space-y-3 pt-2 border-t border-[var(--w-surface-hl)]" data-testid="consent-section">
      <p className="text-[11px] text-[var(--w-text-sec)] uppercase tracking-wider font-medium">Data & Privacy</p>
      <label className="flex items-start gap-3 cursor-pointer group" data-testid="consent-analytics-toggle">
        <div className="relative mt-0.5">
          <input
            type="checkbox"
            checked={consentAnalytics}
            onChange={(e) => onChange('consent_analytics', e.target.checked)}
            className="sr-only"
          />
          <div className={`w-9 h-5 rounded-full transition-colors duration-200
            ${consentAnalytics ? 'bg-[var(--w-accent)]' : 'bg-[var(--w-surface-hl)]'}`}>
            <div className={`w-4 h-4 rounded-full bg-white shadow-sm transform transition-transform duration-200
              ${consentAnalytics ? 'translate-x-4.5 ml-[18px]' : 'ml-[2px]'} mt-[2px]`} />
          </div>
        </div>
        <div>
          <div className="flex items-center gap-1.5">
            <ShieldCheck size={13} className="text-[var(--w-accent)]" />
            <span className="text-xs font-medium text-[var(--w-text)]">Analytics</span>
          </div>
          <p className="text-[10px] text-[var(--w-text-sec)] mt-0.5">Help us understand taste preferences</p>
        </div>
      </label>
      <label className="flex items-start gap-3 cursor-pointer group" data-testid="consent-marketing-toggle">
        <div className="relative mt-0.5">
          <input
            type="checkbox"
            checked={consentMarketing}
            onChange={(e) => onChange('consent_marketing', e.target.checked)}
            className="sr-only"
          />
          <div className={`w-9 h-5 rounded-full transition-colors duration-200
            ${consentMarketing ? 'bg-[var(--w-accent)]' : 'bg-[var(--w-surface-hl)]'}`}>
            <div className={`w-4 h-4 rounded-full bg-white shadow-sm transform transition-transform duration-200
              ${consentMarketing ? 'translate-x-4.5 ml-[18px]' : 'ml-[2px]'} mt-[2px]`} />
          </div>
        </div>
        <div>
          <div className="flex items-center gap-1.5">
            <Shield size={13} className="text-[var(--w-text-sec)]" />
            <span className="text-xs font-medium text-[var(--w-text)]">Marketing</span>
          </div>
          <p className="text-[10px] text-[var(--w-text-sec)] mt-0.5">Receive personalized coffee recommendations</p>
        </div>
      </label>
    </div>
  );
}
