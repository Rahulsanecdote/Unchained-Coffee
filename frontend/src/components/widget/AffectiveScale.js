import React from 'react';

export default function AffectiveScale({ label, value, onChange, description }) {
  return (
    <div className="space-y-1.5" data-testid={`scale-${label.toLowerCase().replace(/[\s\/]+/g, '-')}`}>
      <div className="flex justify-between items-baseline">
        <span className="text-sm font-medium text-[var(--w-text)]">{label}</span>
        {value && (
          <span className="text-xs text-[var(--w-accent)] font-mono">{value}/9</span>
        )}
      </div>
      {description && (
        <p className="text-[11px] text-[var(--w-text-sec)] leading-tight">{description}</p>
      )}
      <div className="grid grid-cols-9 gap-1">
        {[1, 2, 3, 4, 5, 6, 7, 8, 9].map(n => (
          <button
            key={n}
            type="button"
            onClick={() => onChange(n)}
            data-testid={`scale-${label.toLowerCase().replace(/[\s\/]+/g, '-')}-${n}`}
            className={`aspect-square rounded-md text-xs font-mono flex items-center justify-center
              transition-all duration-200 min-w-[32px] min-h-[32px]
              ${value === n
                ? 'bg-[var(--w-accent)] text-[var(--w-bg)] scale-110 shadow-lg font-bold'
                : 'bg-[var(--w-surface-hl)] text-[var(--w-text-sec)] hover:bg-[var(--w-surface)] hover:scale-105 hover:text-[var(--w-text)]'
              }`}
          >
            {n}
          </button>
        ))}
      </div>
      <div className="flex justify-between text-[10px] text-[var(--w-text-sec)] opacity-60 px-0.5">
        <span>Low</span>
        <span>High</span>
      </div>
    </div>
  );
}
