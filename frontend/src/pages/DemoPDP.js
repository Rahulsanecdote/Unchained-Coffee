import React, { useState, useEffect, useCallback } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { Coffee, MapPin, Mountain, Thermometer, ChevronDown } from 'lucide-react';
import TasteFitWidget from '../components/widget/TasteFitWidget';
import TasteFitScore from '../components/widget/TasteFitScore';
import BottomDrawer from '../components/widget/BottomDrawer';
import { MOCK_PRODUCTS } from '../data/mockProducts';
import { apiCall } from '../utils/api';
import { useSessionId } from '../hooks/useSessionId';

function SensoryBar({ label, value, maxValue = 9 }) {
  const pct = (value / maxValue) * 100;
  return (
    <div className="flex items-center gap-3">
      <span className="text-xs text-gray-500 w-20 text-right">{label}</span>
      <div className="flex-1 h-2 bg-gray-100 rounded-full overflow-hidden">
        <div
          className="h-full rounded-full transition-all duration-700"
          style={{ width: `${pct}%`, backgroundColor: '#8D6E63' }}
        />
      </div>
      <span className="text-xs font-mono text-gray-400 w-5">{value}</span>
    </div>
  );
}

export default function DemoPDP() {
  const { productHandle } = useParams();
  const navigate = useNavigate();
  const sessionId = useSessionId();
  const product = MOCK_PRODUCTS[productHandle];
  const [selectedVariant, setSelectedVariant] = useState(null);
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [isMobile, setIsMobile] = useState(false);
  const [scoreKey, setScoreKey] = useState(0);

  useEffect(() => {
    const check = () => setIsMobile(window.innerWidth < 1024);
    check();
    window.addEventListener('resize', check);
    return () => window.removeEventListener('resize', check);
  }, []);

  useEffect(() => {
    if (product) {
      setSelectedVariant(product.variants[0]);
      apiCall('/api/events', {
        method: 'POST',
        body: JSON.stringify({
          event_name: 'product_viewed',
          session_id: sessionId,
          product_id: product.id,
          metadata: { handle: product.handle },
        }),
      }).catch(() => {});
    }
  }, [product, sessionId]);

  if (!product) {
    return (
      <div className="min-h-screen bg-white flex items-center justify-center">
        <div className="text-center">
          <h2 className="font-heading text-2xl text-gray-800 mb-2">Product not found</h2>
          <p className="text-sm text-gray-500 mb-4">Try one of our demo products:</p>
          <div className="space-y-2">
            {Object.values(MOCK_PRODUCTS).map(p => (
              <Link key={p.handle} to={`/demo/pdp/${p.handle}`}
                className="block text-sm text-[#8D6E63] hover:underline">{p.title}</Link>
            ))}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-white" data-testid="demo-pdp-page">
      <header className="border-b border-gray-100 px-6 py-3 flex items-center justify-between bg-white sticky top-0 z-30">
        <div className="flex items-center gap-2">
          <Coffee size={20} className="text-[#3E2723]" />
          <span className="font-heading font-semibold text-[#3E2723] text-lg">Unchained Coffee</span>
        </div>
        <div className="flex items-center gap-4 text-sm text-gray-500">
          <span className="px-2 py-0.5 rounded bg-amber-50 text-amber-700 text-[10px] font-medium uppercase">Demo Mode</span>
          <Link to="/admin/login" className="text-xs text-[#8D6E63] hover:underline" data-testid="admin-link">Admin</Link>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-6 py-8">
        <div className="flex flex-col lg:flex-row gap-8">
          <div className="lg:w-1/2 xl:w-5/12">
            <div className="sticky top-20">
              <img
                src={product.image}
                alt={product.title}
                className="w-full max-w-md mx-auto rounded-2xl"
                data-testid="product-image"
              />
            </div>
          </div>

          <div className="lg:w-1/2 xl:w-7/12 space-y-6">
            <div>
              <p className="text-xs uppercase tracking-widest text-[#8D6E63] mb-2 font-medium">
                Ideal for {product.ideal_for}
              </p>
              <h1 className="font-heading text-3xl lg:text-4xl font-bold text-[#2C1810]" data-testid="product-title">
                {product.title}
              </h1>
              <p className="text-sm text-gray-500 mt-1">{product.subtitle}</p>
            </div>

            <div className="flex items-center gap-4 text-sm text-gray-600">
              <span className="flex items-center gap-1"><Thermometer size={14} /> {product.roast}</span>
              <span className="flex items-center gap-1"><MapPin size={14} /> {product.region}</span>
              <span className="flex items-center gap-1"><Mountain size={14} /> {product.altitude}</span>
            </div>

            <div className="flex gap-2">
              {product.tasting_notes.map(note => (
                <span key={note} className="px-3 py-1 rounded-full text-xs font-medium bg-[#EFEBE9] text-[#5D4037]">
                  {note}
                </span>
              ))}
            </div>

            <div className="space-y-2.5 py-4 border-y border-gray-100">
              <h3 className="text-xs uppercase tracking-widest text-gray-400 font-medium mb-3">Sensory Profile</h3>
              <SensoryBar label="Aroma" value={product.sensory.aroma} />
              <SensoryBar label="Flavor" value={product.sensory.flavor} />
              <SensoryBar label="Aftertaste" value={product.sensory.aftertaste} />
              <SensoryBar label="Acidity" value={product.sensory.acidity} />
              <SensoryBar label="Sweetness" value={product.sensory.sweetness} />
              <SensoryBar label="Mouthfeel" value={product.sensory.mouthfeel} />
              <p className="text-xs text-gray-400 text-right">{product.mouthfeel_descriptor}</p>
            </div>

            <TasteFitScore
              key={`${product.id}-${scoreKey}`}
              productId={product.id}
              productSensory={product.sensory}
            />

            <div className="space-y-3">
              <p className="text-3xl font-heading font-bold text-[#2C1810]">${product.price.toFixed(2)}</p>

              <div>
                <label className="block text-xs text-gray-500 mb-1.5">Variant</label>
                <div className="relative">
                  <select
                    value={selectedVariant?.id || ''}
                    onChange={(e) => {
                      const v = product.variants.find(v => v.id === e.target.value);
                      setSelectedVariant(v);
                    }}
                    data-testid="variant-selector"
                    className="w-full appearance-none px-3 py-2.5 rounded-lg border border-gray-200 text-sm
                      focus:outline-none focus:ring-2 focus:ring-[#8D6E63]/20 pr-8"
                  >
                    {product.variants.map(v => (
                      <option key={v.id} value={v.id}>{v.size} - {v.grind}</option>
                    ))}
                  </select>
                  <ChevronDown size={16} className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 pointer-events-none" />
                </div>
              </div>

              <button className="w-full py-3 rounded-lg bg-[#3E2723] text-white text-sm font-medium hover:bg-[#2C1810] transition-colors"
                data-testid="add-to-cart-btn">
                Add to Cart
              </button>
            </div>

            {!isMobile && (
              <div
                id="taste-fit-widget"
                data-product-id={product.id}
                data-variant-id={selectedVariant?.id}
                data-product-handle={product.handle}
                className="bg-[var(--w-bg)] rounded-2xl p-6 mt-6"
                data-testid="widget-desktop-panel"
              >
                <TasteFitWidget
                  productId={product.id}
                  variantId={selectedVariant?.id}
                  productHandle={product.handle}
                  tastingNotes={product.tasting_notes}
                  onSubmitSuccess={() => setScoreKey(k => k + 1)}
                />
              </div>
            )}
          </div>
        </div>

        <div className="mt-16 text-center text-xs text-gray-400">
          <p>Demo PDP for Shopify integration preview</p>
          <div className="flex justify-center gap-4 mt-2">
            {Object.values(MOCK_PRODUCTS).map(p => (
              <Link key={p.handle} to={`/demo/pdp/${p.handle}`}
                className={`hover:text-[#8D6E63] transition-colors ${p.handle === productHandle ? 'text-[#8D6E63] font-medium' : ''}`}>
                {p.title}
              </Link>
            ))}
          </div>
        </div>
      </div>

      {isMobile && (
        <>
          <button
            onClick={() => setDrawerOpen(true)}
            data-testid="mobile-widget-trigger"
            className="fixed bottom-4 left-4 right-4 z-30 py-3.5 rounded-xl bg-[var(--w-bg)] text-[var(--w-accent)]
              font-heading font-semibold text-sm shadow-2xl flex items-center justify-center gap-2
              hover:brightness-110 transition-all active:scale-[0.98]"
          >
            <Coffee size={18} /> Your Taste Fit
          </button>
          <BottomDrawer isOpen={drawerOpen} onClose={() => setDrawerOpen(false)} title="Your Taste Fit">
            <div className="mb-4">
              <TasteFitScore
                key={`mobile-${product.id}-${scoreKey}`}
                productId={product.id}
                productSensory={product.sensory}
              />
            </div>
            <TasteFitWidget
              productId={product.id}
              variantId={selectedVariant?.id}
              productHandle={product.handle}
              tastingNotes={product.tasting_notes}
              onSubmitSuccess={() => setScoreKey(k => k + 1)}
            />
          </BottomDrawer>
        </>
      )}
    </div>
  );
}
