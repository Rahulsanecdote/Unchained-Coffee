import React, { useState, useEffect, useCallback } from 'react';
import { Sparkles, TrendingUp, TrendingDown, Minus, RefreshCw } from 'lucide-react';
import { apiCall } from '../../utils/api';
import { useSessionId } from '../../hooks/useSessionId';

const ATTR_LABELS = {
  aroma: 'Aroma',
  flavor: 'Flavor',
  aftertaste: 'Aftertaste',
  acidity: 'Acidity',
  sweetness: 'Sweetness',
  mouthfeel: 'Mouthfeel',
};

function ScoreRing({ score, size = 120, strokeWidth = 8 }) {
  const radius = (size - strokeWidth) / 2;
  const circumference = 2 * Math.PI * radius;
  const [offset, setOffset] = useState(circumference);

  useEffect(() => {
    const timer = setTimeout(() => {
      setOffset(circumference - (score / 100) * circumference);
    }, 300);
    return () => clearTimeout(timer);
  }, [score, circumference]);

  const color = score >= 85 ? '#66BB6A' : score >= 70 ? '#FFB74D' : score >= 50 ? '#FF8A65' : '#EF5350';

  return (
    <div className="relative inline-flex items-center justify-center" style={{ width: size, height: size }}>
      <svg width={size} height={size} className="-rotate-90">
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          stroke="currentColor"
          strokeWidth={strokeWidth}
          className="text-[var(--w-surface-hl)]"
        />
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          stroke={color}
          strokeWidth={strokeWidth}
          strokeDasharray={circumference}
          strokeDashoffset={offset}
          strokeLinecap="round"
          className="transition-all duration-1000 ease-out"
        />
      </svg>
      <div className="absolute inset-0 flex flex-col items-center justify-center">
        <span className="text-2xl font-bold font-mono" style={{ color }} data-testid="taste-fit-score-value">
          {score}%
        </span>
      </div>
    </div>
  );
}

function DeltaIcon({ delta }) {
  if (delta > 1) return <TrendingUp size={12} className="text-[var(--w-accent)]" />;
  if (delta < -1) return <TrendingDown size={12} className="text-[var(--w-error)]" />;
  return <Minus size={12} className="text-[var(--w-success)]" />;
}

export default function TasteFitScore({ productId, productSensory, onScoreLoad }) {
  const sessionId = useSessionId();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [expanded, setExpanded] = useState(false);

  const fetchScore = useCallback(async () => {
    setLoading(true);
    try {
      const res = await apiCall('/api/affective/taste-fit', {
        method: 'POST',
        body: JSON.stringify({
          session_id: sessionId,
          product_sensory: productSensory,
        }),
      });
      const result = await res.json();
      setData(result);
      if (onScoreLoad) onScoreLoad(result);
    } catch (e) {
      setData(null);
    } finally {
      setLoading(false);
    }
  }, [sessionId, productSensory, onScoreLoad]);

  useEffect(() => {
    fetchScore();
  }, [fetchScore]);

  if (loading) {
    return (
      <div className="bg-[var(--w-bg)] rounded-2xl p-5 animate-pulse" data-testid="taste-fit-score-loading">
        <div className="flex items-center gap-3">
          <div className="w-20 h-20 rounded-full bg-[var(--w-surface)]" />
          <div className="space-y-2 flex-1">
            <div className="h-4 bg-[var(--w-surface)] rounded w-32" />
            <div className="h-3 bg-[var(--w-surface)] rounded w-24" />
          </div>
        </div>
      </div>
    );
  }

  if (!data || !data.profile_exists) {
    return (
      <div className="bg-[var(--w-bg)] rounded-2xl p-5 border border-[var(--w-surface-hl)]" data-testid="taste-fit-score-no-profile">
        <div className="flex items-center gap-3">
          <div className="w-12 h-12 rounded-full bg-[var(--w-surface)] flex items-center justify-center">
            <Sparkles size={20} className="text-[var(--w-accent)]" />
          </div>
          <div>
            <p className="text-sm font-medium text-[var(--w-text)]">Discover your Taste Fit</p>
            <p className="text-xs text-[var(--w-text-sec)]">Set your preferences below to see how this coffee matches you</p>
          </div>
        </div>
      </div>
    );
  }

  const { score, label, breakdown } = data;

  return (
    <div className="bg-[var(--w-bg)] rounded-2xl overflow-hidden border border-[var(--w-surface-hl)]" data-testid="taste-fit-score-card">
      <div
        className="p-5 cursor-pointer hover:bg-[var(--w-surface)]/30 transition-colors"
        onClick={() => setExpanded(!expanded)}
      >
        <div className="flex items-center gap-4">
          <ScoreRing score={score} size={88} strokeWidth={6} />
          <div className="flex-1">
            <div className="flex items-center gap-2 mb-1">
              <Sparkles size={14} className="text-[var(--w-accent)]" />
              <span className="text-xs text-[var(--w-accent)] font-medium uppercase tracking-wider">Your Taste Fit</span>
            </div>
            <p className="font-heading text-lg font-semibold text-[var(--w-text)]" data-testid="taste-fit-label">
              {label}
            </p>
            <p className="text-xs text-[var(--w-text-sec)] mt-0.5">
              {score >= 85
                ? "This coffee is right in your sweet spot"
                : score >= 70
                ? "Strong alignment with your taste preferences"
                : score >= 50
                ? "Some attributes match, others differ from your usual"
                : "This coffee explores different territory for you"}
            </p>
          </div>
          <button
            onClick={(e) => { e.stopPropagation(); fetchScore(); }}
            className="p-1.5 rounded-lg hover:bg-[var(--w-surface)] transition-colors"
            title="Refresh score"
            data-testid="refresh-score-btn"
          >
            <RefreshCw size={14} className="text-[var(--w-text-sec)]" />
          </button>
        </div>
      </div>

      <div className={`overflow-hidden transition-all duration-500 ease-out ${expanded ? 'max-h-96' : 'max-h-0'}`}>
        <div className="px-5 pb-5 space-y-2.5 border-t border-[var(--w-surface-hl)] pt-4">
          <p className="text-[10px] text-[var(--w-text-sec)] uppercase tracking-wider font-medium">Attribute Breakdown</p>
          {Object.entries(breakdown).map(([key, val]) => (
            <div key={key} className="flex items-center gap-3">
              <span className="text-xs text-[var(--w-text-sec)] w-20">{ATTR_LABELS[key]}</span>
              <div className="flex-1 h-2 bg-[var(--w-surface-hl)] rounded-full overflow-hidden">
                <div
                  className="h-full rounded-full transition-all duration-700"
                  style={{
                    width: `${val.match}%`,
                    backgroundColor: val.match >= 85 ? '#66BB6A' : val.match >= 60 ? '#FFB74D' : '#EF5350',
                  }}
                />
              </div>
              <span className="text-[10px] font-mono text-[var(--w-text-sec)] w-8 text-right">{val.match}%</span>
              <DeltaIcon delta={val.delta} />
              <span className="text-[10px] font-mono text-[var(--w-text-sec)] w-12">
                {val.pref} vs {val.product}
              </span>
            </div>
          ))}
          <p className="text-[10px] text-[var(--w-text-sec)] pt-1 italic">
            Arrow shows if product is higher or lower than your preference
          </p>
        </div>
      </div>
    </div>
  );
}
