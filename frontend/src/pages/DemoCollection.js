import React, { useState, useEffect, useMemo } from 'react';
import { Link } from 'react-router-dom';
import { Coffee, Sparkles, ArrowUpRight, SlidersHorizontal, MapPin, Flame } from 'lucide-react';
import { MOCK_PRODUCTS } from '../data/mockProducts';
import { apiCall } from '../utils/api';
import { useSessionId } from '../hooks/useSessionId';

function ScoreBadge({ score, label }) {
  const color = score >= 85 ? '#66BB6A' : score >= 70 ? '#FFB74D' : score >= 50 ? '#FF8A65' : '#EF5350';
  return (
    <div
      className="absolute top-3 right-3 z-10 flex items-center gap-1.5 px-2.5 py-1.5 rounded-full backdrop-blur-md"
      style={{ backgroundColor: `${color}18`, border: `1px solid ${color}40` }}
      data-testid="score-badge"
    >
      <Sparkles size={12} style={{ color }} />
      <span className="text-xs font-bold font-mono" style={{ color }}>{score}%</span>
    </div>
  );
}

function MiniSensory({ sensory }) {
  const attrs = [
    { key: 'aroma', label: 'AR' },
    { key: 'flavor', label: 'FL' },
    { key: 'acidity', label: 'AC' },
    { key: 'sweetness', label: 'SW' },
    { key: 'mouthfeel', label: 'MF' },
  ];
  return (
    <div className="flex gap-1 items-end">
      {attrs.map(a => (
        <div key={a.key} className="flex flex-col items-center gap-0.5">
          <div className="w-4 bg-gray-100 rounded-sm overflow-hidden" style={{ height: 32 }}>
            <div
              className="w-full rounded-sm transition-all duration-500"
              style={{
                height: `${(sensory[a.key] / 9) * 100}%`,
                backgroundColor: '#8D6E63',
                marginTop: `${100 - (sensory[a.key] / 9) * 100}%`,
              }}
            />
          </div>
          <span className="text-[8px] text-gray-400 font-mono">{a.label}</span>
        </div>
      ))}
    </div>
  );
}

function ProductCard({ product, score, rank, isPersonalized }) {
  return (
    <Link
      to={`/demo/pdp/${product.handle}`}
      className="group relative bg-white rounded-2xl border border-gray-100 overflow-hidden
        hover:shadow-xl hover:border-gray-200 hover:-translate-y-1 transition-all duration-300"
      data-testid={`product-card-${product.handle}`}
    >
      {score !== null && score !== undefined && <ScoreBadge score={score.score} label={score.label} />}

      {isPersonalized && rank !== null && rank <= 2 && (
        <div className="absolute top-3 left-3 z-10 px-2 py-1 rounded-full bg-[#2C1810] text-white text-[10px] font-bold uppercase tracking-wider">
          {rank === 0 ? 'Top Pick' : rank === 1 ? '#2 Match' : '#3 Match'}
        </div>
      )}

      <div className="aspect-square bg-[#FAF7F5] p-6 relative overflow-hidden">
        <img
          src={product.image}
          alt={product.title}
          className="w-full h-full object-contain group-hover:scale-105 transition-transform duration-500"
          loading="lazy"
        />
        <div className="absolute bottom-3 left-3 right-3 flex gap-1">
          {product.tasting_notes.map(note => (
            <span key={note} className="px-2 py-0.5 rounded-full text-[9px] font-medium bg-white/80 backdrop-blur-sm text-[#5D4037] border border-[#D7CCC8]/40">
              {note}
            </span>
          ))}
        </div>
      </div>

      <div className="p-4 space-y-3">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="text-[10px] uppercase tracking-wider text-[#8D6E63] font-medium">{product.process}</span>
            <span className="text-gray-300">|</span>
            <span className="text-[10px] uppercase tracking-wider text-gray-400">{product.roast}</span>
          </div>
          <h3 className="font-heading text-lg font-semibold text-[#2C1810] group-hover:text-[#5D4037] transition-colors leading-tight">
            {product.title}
          </h3>
          <p className="text-xs text-gray-400 mt-0.5">{product.subtitle}</p>
        </div>

        <div className="flex items-end justify-between">
          <div className="flex items-center gap-3">
            <MiniSensory sensory={product.sensory} />
          </div>
          <div className="text-right">
            <p className="text-lg font-heading font-bold text-[#2C1810]">${product.price.toFixed(2)}</p>
          </div>
        </div>

        <div className="flex items-center justify-between pt-2 border-t border-gray-50">
          <div className="flex items-center gap-3 text-[10px] text-gray-400">
            <span className="flex items-center gap-0.5"><MapPin size={10} /> {product.region}</span>
            <span className="flex items-center gap-0.5"><Flame size={10} /> {product.ideal_for}</span>
          </div>
          <ArrowUpRight size={16} className="text-gray-300 group-hover:text-[#8D6E63] transition-colors" />
        </div>

        {score && score.breakdown && (
          <div className="pt-2 border-t border-gray-50 space-y-1">
            {Object.entries(score.breakdown).slice(0, 3).map(([key, val]) => (
              <div key={key} className="flex items-center gap-2">
                <span className="text-[9px] text-gray-400 w-14 capitalize">{key}</span>
                <div className="flex-1 h-1 bg-gray-100 rounded-full overflow-hidden">
                  <div
                    className="h-full rounded-full"
                    style={{
                      width: `${val.match}%`,
                      backgroundColor: val.match >= 85 ? '#66BB6A' : val.match >= 60 ? '#FFB74D' : '#EF5350',
                    }}
                  />
                </div>
                <span className="text-[9px] font-mono text-gray-400">{val.match}%</span>
              </div>
            ))}
          </div>
        )}
      </div>
    </Link>
  );
}

export default function DemoCollection() {
  const sessionId = useSessionId();
  const [scores, setScores] = useState({});
  const [hasProfile, setHasProfile] = useState(false);
  const [loading, setLoading] = useState(true);
  const [sortBy, setSortBy] = useState('match');
  const [filterProcess, setFilterProcess] = useState('all');
  const [filterRoast, setFilterRoast] = useState('all');

  const allProducts = useMemo(() => Object.values(MOCK_PRODUCTS), []);

  useEffect(() => {
    const fetchScores = async () => {
      try {
        const batchPayload = {
          session_id: sessionId,
          products: allProducts.map(p => ({ product_id: p.id, sensory: p.sensory })),
        };
        const res = await apiCall('/api/affective/taste-fit/batch', {
          method: 'POST',
          body: JSON.stringify(batchPayload),
        });
        const data = await res.json();
        if (data.profile_exists) {
          setHasProfile(true);
          const map = {};
          data.scores.forEach(s => { map[s.product_id] = s; });
          setScores(map);
        }
      } catch (e) {
        // Silent — no profile yet
      } finally {
        setLoading(false);
      }
    };
    fetchScores();
  }, [sessionId, allProducts]);

  const processes = [...new Set(allProducts.map(p => p.process))];
  const roasts = [...new Set(allProducts.map(p => p.roast))];

  const filteredProducts = useMemo(() => {
    let list = [...allProducts];
    if (filterProcess !== 'all') list = list.filter(p => p.process === filterProcess);
    if (filterRoast !== 'all') list = list.filter(p => p.roast === filterRoast);

    if (sortBy === 'match' && hasProfile) {
      list.sort((a, b) => (scores[b.id]?.score || 0) - (scores[a.id]?.score || 0));
    } else if (sortBy === 'price-asc') {
      list.sort((a, b) => a.price - b.price);
    } else if (sortBy === 'price-desc') {
      list.sort((a, b) => b.price - a.price);
    }
    return list;
  }, [allProducts, sortBy, hasProfile, scores, filterProcess, filterRoast]);

  const rankedProducts = useMemo(() => {
    if (!hasProfile || sortBy !== 'match') return filteredProducts.map(p => ({ product: p, rank: null }));
    return filteredProducts.map((p, i) => ({ product: p, rank: i }));
  }, [filteredProducts, hasProfile, sortBy]);

  return (
    <div className="min-h-screen bg-[#FAFAF8]" data-testid="collection-page">
      {/* Header */}
      <header className="border-b border-gray-100 bg-white sticky top-0 z-30">
        <div className="max-w-7xl mx-auto px-6 py-3 flex items-center justify-between">
          <Link to="/demo/collection" className="flex items-center gap-2">
            <Coffee size={20} className="text-[#3E2723]" />
            <span className="font-heading font-semibold text-[#3E2723] text-lg">Unchained Coffee</span>
          </Link>
          <div className="flex items-center gap-4 text-sm text-gray-500">
            <Link to="/demo/collection" className="text-xs text-[#3E2723] font-medium" data-testid="nav-collection">Shop</Link>
            <span className="px-2 py-0.5 rounded bg-amber-50 text-amber-700 text-[10px] font-medium uppercase">Demo</span>
            <Link to="/admin/login" className="text-xs text-[#8D6E63] hover:underline" data-testid="nav-admin">Admin</Link>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-6 py-10">
        {/* Hero section */}
        <div className="mb-10">
          {hasProfile ? (
            <div className="relative overflow-hidden rounded-2xl bg-gradient-to-br from-[#2C1810] to-[#3E2723] p-8 lg:p-12" data-testid="hero-personalized">
              <div className="absolute top-0 right-0 w-80 h-80 bg-[#FFB74D]/5 rounded-full blur-3xl" />
              <div className="absolute bottom-0 left-0 w-64 h-64 bg-[#8D6E63]/10 rounded-full blur-3xl" />
              <div className="relative z-10">
                <div className="flex items-center gap-2 mb-3">
                  <Sparkles size={18} className="text-[#FFB74D]" />
                  <span className="text-xs text-[#FFB74D] uppercase tracking-widest font-medium">Personalized For You</span>
                </div>
                <h1 className="font-heading text-3xl lg:text-4xl font-bold text-white mb-3">
                  Best Matches For Your Palate
                </h1>
                <p className="text-sm text-[#D7CCC8] max-w-lg">
                  Sorted by how well each coffee aligns with your taste profile.
                  The higher the score, the closer it is to what you love.
                </p>
              </div>
            </div>
          ) : (
            <div className="relative overflow-hidden rounded-2xl bg-white border border-gray-100 p-8 lg:p-12" data-testid="hero-default">
              <div className="max-w-xl">
                <h1 className="font-heading text-3xl lg:text-4xl font-bold text-[#2C1810] mb-3">
                  Our Coffees
                </h1>
                <p className="text-sm text-gray-500 mb-5">
                  Direct-trade single-origin Colombian coffees. Each one tells a story of terroir and craft.
                </p>
                <Link
                  to={`/demo/pdp/${allProducts[0]?.handle}`}
                  className="inline-flex items-center gap-2 px-4 py-2.5 rounded-xl bg-[#2C1810] text-white text-xs font-medium
                    hover:bg-[#3E2723] transition-colors"
                  data-testid="hero-cta"
                >
                  <SlidersHorizontal size={14} />
                  Set your taste preferences to unlock personalized matches
                </Link>
              </div>
            </div>
          )}
        </div>

        {/* Filter bar */}
        <div className="flex flex-wrap items-center justify-between gap-4 mb-8" data-testid="filter-bar">
          <div className="flex items-center gap-3">
            <div className="flex items-center gap-2">
              <label className="text-[10px] uppercase tracking-wider text-gray-400 font-medium">Process</label>
              <select
                value={filterProcess}
                onChange={e => setFilterProcess(e.target.value)}
                data-testid="filter-process"
                className="text-xs px-2.5 py-1.5 rounded-lg border border-gray-200 bg-white text-gray-700 focus:outline-none focus:ring-2 focus:ring-[#8D6E63]/20"
              >
                <option value="all">All</option>
                {processes.map(p => <option key={p} value={p}>{p}</option>)}
              </select>
            </div>
            <div className="flex items-center gap-2">
              <label className="text-[10px] uppercase tracking-wider text-gray-400 font-medium">Roast</label>
              <select
                value={filterRoast}
                onChange={e => setFilterRoast(e.target.value)}
                data-testid="filter-roast"
                className="text-xs px-2.5 py-1.5 rounded-lg border border-gray-200 bg-white text-gray-700 focus:outline-none focus:ring-2 focus:ring-[#8D6E63]/20"
              >
                <option value="all">All</option>
                {roasts.map(r => <option key={r} value={r}>{r}</option>)}
              </select>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <label className="text-[10px] uppercase tracking-wider text-gray-400 font-medium">Sort</label>
            <select
              value={sortBy}
              onChange={e => setSortBy(e.target.value)}
              data-testid="sort-select"
              className="text-xs px-2.5 py-1.5 rounded-lg border border-gray-200 bg-white text-gray-700 focus:outline-none focus:ring-2 focus:ring-[#8D6E63]/20"
            >
              {hasProfile && <option value="match">Best Match</option>}
              <option value="default">Default</option>
              <option value="price-asc">Price: Low to High</option>
              <option value="price-desc">Price: High to Low</option>
            </select>
          </div>
        </div>

        {/* Product count */}
        <p className="text-xs text-gray-400 mb-4" data-testid="product-count">
          {filteredProducts.length} {filteredProducts.length === 1 ? 'coffee' : 'coffees'}
          {hasProfile && sortBy === 'match' && ' — sorted by your taste fit'}
        </p>

        {/* Product grid */}
        {loading ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {[...Array(6)].map((_, i) => (
              <div key={i} className="bg-white rounded-2xl border border-gray-100 overflow-hidden animate-pulse">
                <div className="aspect-square bg-gray-50" />
                <div className="p-4 space-y-3">
                  <div className="h-4 bg-gray-100 rounded w-2/3" />
                  <div className="h-3 bg-gray-100 rounded w-1/2" />
                  <div className="h-6 bg-gray-100 rounded w-1/4" />
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6" data-testid="product-grid">
            {rankedProducts.map(({ product, rank }) => (
              <ProductCard
                key={product.id}
                product={product}
                score={scores[product.id] || null}
                rank={rank}
                isPersonalized={hasProfile && sortBy === 'match'}
              />
            ))}
          </div>
        )}

        {/* Footer */}
        <div className="mt-16 pt-8 border-t border-gray-100 text-center">
          <p className="text-xs text-gray-400">
            Demo collection page for Shopify integration preview
          </p>
          <p className="text-[10px] text-gray-300 mt-1">
            Scores are computed live from your taste profile against each product's sensory data.
          </p>
        </div>
      </div>
    </div>
  );
}
