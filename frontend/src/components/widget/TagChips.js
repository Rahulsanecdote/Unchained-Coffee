import React from 'react';

export default function TagChips({ tags, selected, onToggle, maxSelect = 5, label }) {
  return (
    <div className="space-y-2" data-testid={`tag-chips-${label.toLowerCase().replace(/\s+/g, '-')}`}>
      <div className="flex justify-between items-baseline">
        <span className="text-sm font-medium text-[var(--w-text)]">{label}</span>
        <span className="text-[10px] text-[var(--w-text-sec)]">{selected.length}/{maxSelect} max</span>
      </div>
      <div className="flex flex-wrap gap-1.5">
        {tags.map(tag => {
          const isSelected = selected.includes(tag);
          const disabled = !isSelected && selected.length >= maxSelect;
          return (
            <button
              key={tag}
              type="button"
              onClick={() => !disabled && onToggle(tag)}
              disabled={disabled}
              data-testid={`tag-${tag.toLowerCase().replace(/[\s\/]+/g, '-')}`}
              className={`px-3 py-1.5 rounded-full text-xs font-medium transition-all duration-200
                ${isSelected
                  ? 'bg-[var(--w-accent)] text-[var(--w-bg)]'
                  : disabled
                    ? 'border border-[var(--w-surface-hl)] text-[var(--w-text-sec)] opacity-30 cursor-not-allowed'
                    : 'border border-[var(--w-text-sec)] text-[var(--w-text-sec)] hover:border-[var(--w-accent)] hover:text-[var(--w-accent)]'
                }`}
            >
              {tag}
            </button>
          );
        })}
      </div>
    </div>
  );
}
