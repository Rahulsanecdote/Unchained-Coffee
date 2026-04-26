import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Coffee, Sparkles, MapPin, Flame, ArrowUpRight, SlidersHorizontal, RefreshCw } from 'lucide-react';
import { apiCall } from '../utils/api';
import { useSessionId } from '../hooks/useSessionId';

function ScoreBadge({ score }) {
  if (score == null) return null;
  const color = score >= 85 ? '#66BB6A' : score >= 70 ? '#FFB74D' : score >= 50 ? '#FF8A65' : '#EF5350';
  return (
    <div
      className="absolute top-3 right-3 z-10 flex items-center gap-1.5 px-2.5 py-1.5 rounded-full backdrop-blur-md"
      style={{ backgroundColor: `${color}18`, border: `1px solid ${color}40` }}
      data-testid="rec-score-badge"
    >
      <Sparkles size={12} style={{ color }} />
      <span className="text-xs font-bold font-mono" style={{ color }}>{score}%</span>
    </div>
  );
}

function RecommendationCard({ rec, rank }) {
  const lot = rec.lot;
  const explanations = rec.explanation || [];

  return (
    <Link
      to={`/demo/pdp/${lot.handle}`}
      className="group relative bg-white rounded-2xl border border-gray-100 overflow-hidden
        hover:shadow-xl hover:border-gray-200 hover:-translate-y-1 transition-all duration-300"
      data-testid={`rec-card-${lot.lot_id}`}
    >
      {rec.score != null && <ScoreBadge score={rec.score} />}

      {rank <= 2 && rec.score != null && (
        <div className="absolute top-3 left-3 z-10 px-2 py-1 rounded-full bg-[#2C1810] text-white text-[10px] font-bold uppercase tracking-wider"
          data-testid={`rec-rank-${rank}`}>
          {rank === 0 ? 'Top Pick' : rank === 1 ? '#2 Match' : '#3 Match'}
        </div>
      )}

      <div className="aspect-square bg-[#FAF7F5] p-6 relative overflow-hidden">
        <img
          src={lot.image}
          alt={lot.title}
          className="w-full h-full object-contain group-hover:scale-105 transition-transform duration-500"
          loading="lazy"
        />
        <div className="absolute bottom-3 left-3 right-3 flex gap-1 flex-wrap">
          {(lot.tasting_notes || []).map(note => (
            <span key={note} className="px-2 py-0.5 rounded-full text-[9px] font-medium bg-white/80 backdrop-blur-sm text-[#5D4037] border border-[#D7CCC8]/40">
              {note}
            </span>
          ))}
        </div>
      </div>

      <div className="p-4 space-y-3">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="text-[10px] uppercase tracking-wider text-[#8D6E63] font-medium">{lot.process}</span>
            {lot.variety && (
              <>
                <span className="text-gray-300">|</span>
                <span className="text-[10px] uppercase tracking-wider text-gray-400">{lot.variety}</span>
              </>
            )}
          </div>
          <h3 className="font-heading text-lg font-semibold text-[#2C1810] group-hover:text-[#5D4037] transition-colors leading-tight">
            {lot.title}
          </h3>
          <p className="text-xs text-gray-400 mt-0.5">by {lot.producer}</p>
        </div>

        {/* Why recommended */}
        {explanations.length > 0 && (
          <div className="bg-[#FAF7F5] rounded-lg px-3 py-2 space-y-1" data-testid="why-recommended">
            <p className="text-[9px] text-[#8D6E63] uppercase tracking-wider font-medium">Why this matches</p>
            {explanations.map((exp, i) => (
              <p key={i} className="text-[11px] text-[#5D4037] leading-snug">{exp}</p>
            ))}
          </div>
        )}

        <div className="flex items-end justify-between">
          <div className="flex items-center gap-3 text-[10px] text-gray-400">
            <span className="flex items-center gap-0.5"><MapPin size={10} /> {lot.region}</span>
            {lot.ideal_for && (
              <span className="flex items-center gap-0.5"><Flame size={10} /> {lot.ideal_for}</span>
            )}
          </div>
          <div className="text-right">
            <p className="text-lg font-heading font-bold text-[#2C1810]">${lot.price?.toFixed(2)}</p>
          </div>
        </div>

        <div className="flex items-center justify-between pt-2 border-t border-gray-50">
          <div className="flex gap-1 flex-wrap">
            {(lot.expected_flavor_tags || []).slice(0, 3).map(tag => (
              <span key={tag} className="px-1.5 py-0.5 rounded text-[8px] font-mono text-[#8D6E63] bg-[#FAF7F5] capitalize">
                {tag}
              </span>
            ))}
          </div>
          <ArrowUpRight size={16} className="text-gray-300 group-hover:text-[#8D6E63] transition-colors" />
        </div>
      </div>
    </Link>
  );
}

export default function Recommendations() {
  const sessionId = useSessionId();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  const fetchRecs = async () => {
    setLoading(true);
    try {
      const res = await apiCall('/api/recommendations', {
        method: 'POST',
        body: JSON.stringify({ session_id: sessionId, limit: 6 }),
      });
      const result = await res.json();
      setData(result);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchRecs(); }, [sessionId]);

  const isPersonalized = data?.mode === 'personalized';

  return (
    <div className="min-h-screen bg-[#FAFAF8]" data-testid="recommendations-page">
      <header className="border-b border-gray-100 bg-white sticky top-0 z-30">
        <div className="max-w-7xl mx-auto px-6 py-3 flex items-center justify-between">
          <Link to="/demo/collection" className="flex items-center gap-2">
            <Coffee size={20} className="text-[#3E2723]" />
            <span className="font-heading font-semibold text-[#3E2723] text-lg">Unchained Coffee</span>
          </Link>
          <div className="flex items-center gap-4 text-sm text-gray-500">
            <Link to="/demo/collection" className="text-xs text-[#3E2723] font-medium hover:text-[#8D6E63]" data-testid="nav-shop">Shop</Link>
            <Link to="/demo/quiz" className="text-xs text-[#8D6E63] hover:text-[#3E2723]" data-testid="nav-retake">Retake Quiz</Link>
            <span className="px-2 py-0.5 rounded bg-amber-50 text-amber-700 text-[10px] font-medium uppercase">Demo</span>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-6 py-10">
        {/* Hero */}
        {isPersonalized ? (
          <div className="relative overflow-hidden rounded-2xl bg-gradient-to-br from-[#2C1810] to-[#3E2723] p-8 lg:p-12 mb-10" data-testid="recs-hero-personalized">
            <div className="absolute top-0 right-0 w-80 h-80 bg-[#FFB74D]/5 rounded-full blur-3xl" />
            <div className="absolute bottom-0 left-0 w-64 h-64 bg-[#8D6E63]/10 rounded-full blur-3xl" />
            <div className="relative z-10 flex items-center justify-between">
              <div>
                <div className="flex items-center gap-2 mb-3">
                  <Sparkles size={18} className="text-[#FFB74D]" />
                  <span className="text-xs text-[#FFB74D] uppercase tracking-widest font-medium">
                    {data?.model_version || 'rules_v1'} engine
                  </span>
                </div>
                <h1 className="font-heading text-3xl lg:text-4xl font-bold text-white mb-3">
                  Your Personal Picks
                </h1>
                <p className="text-sm text-[#D7CCC8] max-w-lg">
                  Scored and ranked by how well each lot matches your taste profile.
                  The recommendations are unique to you.
                </p>
              </div>
              <button
                onClick={fetchRecs}
                className="hidden lg:flex items-center gap-2 px-4 py-2 rounded-xl bg-white/10 text-white text-xs
                  hover:bg-white/20 transition-colors"
                data-testid="refresh-recs-btn"
              >
                <RefreshCw size={14} /> Refresh
              </button>
            </div>
          </div>
        ) : (
          <div className="relative overflow-hidden rounded-2xl bg-white border border-gray-100 p-8 lg:p-12 mb-10" data-testid="recs-hero-cold">
            <div className="max-w-xl">
              <h1 className="font-heading text-3xl lg:text-4xl font-bold text-[#2C1810] mb-3">
                Editor's Picks
              </h1>
              <p className="text-sm text-gray-500 mb-5">
                Our top-rated coffees. Take the taste quiz to get personalized recommendations.
              </p>
              <Link
                to="/demo/quiz"
                className="inline-flex items-center gap-2 px-4 py-2.5 rounded-xl bg-[#2C1810] text-white text-xs font-medium
                  hover:bg-[#3E2723] transition-colors"
                data-testid="take-quiz-cta"
              >
                <SlidersHorizontal size={14} />
                Take the Taste Quiz
              </Link>
            </div>
          </div>
        )}

        {/* Recommendations grid */}
        {loading ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {[...Array(6)].map((_, i) => (
              <div key={i} className="bg-white rounded-2xl border border-gray-100 overflow-hidden animate-pulse">
                <div className="aspect-square bg-gray-50" />
                <div className="p-4 space-y-3">
                  <div className="h-4 bg-gray-100 rounded w-2/3" />
                  <div className="h-3 bg-gray-100 rounded w-1/2" />
                  <div className="h-10 bg-gray-50 rounded" />
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6" data-testid="recs-grid">
            {(data?.recommendations || []).map((rec, i) => (
              <RecommendationCard key={rec.lot.lot_id} rec={rec} rank={i} />
            ))}
          </div>
        )}

        {/* Footer CTA */}
        <div className="mt-12 text-center">
          {!isPersonalized && (
            <Link
              to="/demo/quiz"
              className="inline-flex items-center gap-2 px-6 py-3 rounded-xl bg-[#FFB74D] text-[#2C1810] text-sm font-bold
                hover:brightness-110 transition-all"
              data-testid="bottom-quiz-cta"
            >
              <Sparkles size={16} /> Tell us what you love — get personalized picks
            </Link>
          )}
          <p className="text-xs text-gray-400 mt-6">
            {isPersonalized
              ? 'Recommendations computed using rules_v1 scoring engine'
              : 'Sorted by average review rating and metadata quality'}
          </p>
        </div>
      </div>
    </div>
  );
}
