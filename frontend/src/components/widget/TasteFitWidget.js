import React, { useState, useEffect, useCallback } from 'react';
import { Coffee, Zap, CheckCircle, Loader2 } from 'lucide-react';
import AffectiveScale from './AffectiveScale';
import TagChips from './TagChips';
import ConsentToggles from './ConsentToggles';
import { apiCall } from '../../utils/api';
import { useSessionId } from '../../hooks/useSessionId';
import { CANONICAL_TAGS, PROCESS_TAGS, FIT_ISSUE_TAGS } from '../../data/mockProducts';

const ATTRIBUTES = [
  { key: 'aroma', label: 'Aroma Intensity', prefDesc: 'How intense do you prefer aroma?', tasteDesc: 'How intense is the aroma?' },
  { key: 'flavor', label: 'Flavor Intensity', prefDesc: 'How bold should the flavor be?', tasteDesc: 'How bold is the flavor?' },
  { key: 'aftertaste', label: 'Aftertaste Length', prefDesc: 'How long should the aftertaste linger?', tasteDesc: 'How long does the aftertaste linger?' },
  { key: 'acidity', label: 'Acidity', prefDesc: 'How bright/acidic do you prefer?', tasteDesc: 'How bright/acidic is this coffee?' },
  { key: 'sweetness', label: 'Sweetness', prefDesc: 'How sweet do you prefer?', tasteDesc: 'How sweet is this coffee?' },
  { key: 'mouthfeel', label: 'Mouthfeel / Body', prefDesc: 'How full-bodied do you prefer?', tasteDesc: 'How full-bodied is this coffee?' },
];

export default function TasteFitWidget({ productId, variantId, productHandle, tastingNotes = [], onSubmitSuccess }) {
  const sessionId = useSessionId();
  const [mode, setMode] = useState('preference_only');
  const [ratings, setRatings] = useState({});
  const [overallLiking, setOverallLiking] = useState(null);
  const [standoutTags, setStandoutTags] = useState([]);
  const [fitTags, setFitTags] = useState([]);
  const [notes, setNotes] = useState('');
  const [consentAnalytics, setConsentAnalytics] = useState(true);
  const [consentMarketing, setConsentMarketing] = useState(false);
  const [loading, setLoading] = useState(false);
  const [submitted, setSubmitted] = useState(false);
  const [error, setError] = useState(null);
  const [prefilled, setPrefilled] = useState(false);

  const fetchProfile = useCallback(async () => {
    try {
      const res = await apiCall(`/api/affective/profile?session_id=${sessionId}`);
      const data = await res.json();
      if (data.profile) {
        const p = data.profile;
        setRatings({
          aroma: p.aroma_pref_1to9,
          flavor: p.flavor_pref_1to9,
          aftertaste: p.aftertaste_pref_1to9,
          acidity: p.acidity_pref_1to9,
          sweetness: p.sweetness_pref_1to9,
          mouthfeel: p.mouthfeel_pref_1to9,
        });
        setConsentAnalytics(p.consent_analytics);
        setConsentMarketing(p.consent_marketing);
        setPrefilled(true);
      }
    } catch (e) {
      // Silent fail for prefill
    }
  }, [sessionId]);

  useEffect(() => {
    fetchProfile();
    apiCall('/api/events', {
      method: 'POST',
      body: JSON.stringify({
        event_name: 'affective_form_viewed',
        session_id: sessionId,
        product_id: productId,
      }),
    }).catch(() => {});
  }, [sessionId, productId, fetchProfile]);

  const handleModeChange = (newMode) => {
    setMode(newMode);
    setSubmitted(false);
    setError(null);
    apiCall('/api/events', {
      method: 'POST',
      body: JSON.stringify({
        event_name: 'affective_form_opened',
        session_id: sessionId,
        product_id: productId,
        metadata: { mode: newMode },
      }),
    }).catch(() => {});
  };

  const handleRatingChange = (key, value) => {
    setRatings(prev => ({ ...prev, [key]: value }));
  };

  const handleTagToggle = (tag) => {
    setStandoutTags(prev =>
      prev.includes(tag) ? prev.filter(t => t !== tag) : [...prev, tag]
    );
  };

  const handleFitToggle = (tag) => {
    setFitTags(prev =>
      prev.includes(tag) ? prev.filter(t => t !== tag) : [...prev, tag]
    );
  };

  const handleConsentChange = (field, value) => {
    if (field === 'consent_analytics') setConsentAnalytics(value);
    if (field === 'consent_marketing') setConsentMarketing(value);
  };

  const allRatingsFilled = ATTRIBUTES.every(a => ratings[a.key] != null);

  const handleSubmit = async () => {
    if (!allRatingsFilled) {
      setError('Please rate all attributes before submitting.');
      return;
    }
    if (mode === 'tasted' && !overallLiking) {
      setError('Please rate your overall liking.');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      await apiCall('/api/affective/profile', {
        method: 'POST',
        body: JSON.stringify({
          session_id: sessionId,
          aroma_pref_1to9: ratings.aroma,
          flavor_pref_1to9: ratings.flavor,
          aftertaste_pref_1to9: ratings.aftertaste,
          acidity_pref_1to9: ratings.acidity,
          sweetness_pref_1to9: ratings.sweetness,
          mouthfeel_pref_1to9: ratings.mouthfeel,
          consent_analytics: consentAnalytics,
          consent_marketing: consentMarketing,
        }),
      });

      await apiCall('/api/affective/response', {
        method: 'POST',
        body: JSON.stringify({
          session_id: sessionId,
          product_id: productId,
          variant_id: variantId,
          mode,
          aroma_1to9: ratings.aroma,
          flavor_1to9: ratings.flavor,
          aftertaste_1to9: ratings.aftertaste,
          acidity_1to9: ratings.acidity,
          sweetness_1to9: ratings.sweetness,
          mouthfeel_1to9: ratings.mouthfeel,
          overall_liking_1to9: mode === 'tasted' ? overallLiking : null,
          notes: notes || null,
          standout_tags: standoutTags.length > 0 ? standoutTags : null,
          standout_tags_source: standoutTags.length > 0 ? 'canonical' : null,
          fit_tags: fitTags.length > 0 ? fitTags : null,
          consent_analytics: consentAnalytics,
          consent_marketing: consentMarketing,
        }),
      });

      setSubmitted(true);
      if (onSubmitSuccess) onSubmitSuccess();
    } catch (err) {
      setError(err.message || 'Something went wrong. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const availableTags = [
    ...tastingNotes,
    ...CANONICAL_TAGS.filter(t => !tastingNotes.includes(t)).slice(0, 8 - tastingNotes.length),
  ];

  if (submitted) {
    return (
      <div className="flex flex-col items-center justify-center py-12 px-6 text-center" data-testid="submit-confirmation">
        <div className="w-16 h-16 rounded-full bg-[var(--w-success)]/20 flex items-center justify-center mb-4">
          <CheckCircle size={32} className="text-[var(--w-success)]" />
        </div>
        <h3 className="font-heading text-xl font-semibold text-[var(--w-text)] mb-2">Saved</h3>
        <p className="text-sm text-[var(--w-text-sec)] max-w-xs">
          We'll use this to recommend coffees you'll actually like.
        </p>
        <button
          onClick={() => { setSubmitted(false); }}
          className="mt-6 text-xs text-[var(--w-accent)] hover:underline"
          data-testid="submit-another-btn"
        >
          Submit another response
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-5" data-testid="taste-fit-widget">
      <div className="text-center pb-2">
        <h3 className="font-heading text-xl font-semibold text-[var(--w-text)]">Your Taste Fit</h3>
        <p className="text-xs text-[var(--w-text-sec)] mt-1">
          {prefilled ? 'Your preferences are loaded. Update anytime.' : 'Tell us what you like. Takes 30 seconds.'}
        </p>
      </div>

      <div className="flex rounded-lg overflow-hidden border border-[var(--w-surface-hl)]" data-testid="mode-toggle">
        <button
          onClick={() => handleModeChange('preference_only')}
          data-testid="mode-preferences-btn"
          className={`flex-1 py-2.5 px-3 text-xs font-medium flex items-center justify-center gap-1.5 transition-all
            ${mode === 'preference_only'
              ? 'bg-[var(--w-accent)] text-[var(--w-bg)]'
              : 'bg-[var(--w-surface)] text-[var(--w-text-sec)] hover:text-[var(--w-text)]'
            }`}
        >
          <Coffee size={14} /> My Preferences
        </button>
        <button
          onClick={() => handleModeChange('tasted')}
          data-testid="mode-tasting-btn"
          className={`flex-1 py-2.5 px-3 text-xs font-medium flex items-center justify-center gap-1.5 transition-all
            ${mode === 'tasted'
              ? 'bg-[var(--w-accent)] text-[var(--w-bg)]'
              : 'bg-[var(--w-surface)] text-[var(--w-text-sec)] hover:text-[var(--w-text)]'
            }`}
        >
          <Zap size={14} /> I'm drinking it now
        </button>
      </div>

      <div className="space-y-4">
        {ATTRIBUTES.map(attr => (
          <AffectiveScale
            key={attr.key}
            label={attr.label}
            value={ratings[attr.key]}
            onChange={(v) => handleRatingChange(attr.key, v)}
            description={mode === 'preference_only' ? attr.prefDesc : attr.tasteDesc}
          />
        ))}

        {mode === 'tasted' && (
          <>
            <div className="border-t border-[var(--w-surface-hl)] pt-4">
              <AffectiveScale
                label="Overall Liking"
                value={overallLiking}
                onChange={setOverallLiking}
                description="How much do you enjoy this coffee overall?"
              />
            </div>

            <TagChips
              label="Standout Notes"
              tags={availableTags}
              selected={standoutTags}
              onToggle={handleTagToggle}
              maxSelect={5}
            />

            <TagChips
              label="Fit Feedback"
              tags={FIT_ISSUE_TAGS}
              selected={fitTags}
              onToggle={handleFitToggle}
              maxSelect={3}
            />

            <div className="space-y-1.5" data-testid="notes-section">
              <label className="text-sm font-medium text-[var(--w-text)]">Notes</label>
              <textarea
                value={notes}
                onChange={(e) => setNotes(e.target.value.slice(0, 280))}
                placeholder="Any thoughts on this coffee..."
                rows={2}
                data-testid="notes-input"
                className="w-full bg-[var(--w-surface)] border border-[var(--w-surface-hl)] rounded-lg px-3 py-2
                  text-sm text-[var(--w-text)] placeholder:text-[var(--w-text-sec)]/50
                  focus:outline-none focus:border-[var(--w-accent)] transition-colors resize-none"
              />
              <p className="text-[10px] text-[var(--w-text-sec)] text-right">{notes.length}/280</p>
            </div>
          </>
        )}
      </div>

      <ConsentToggles
        consentAnalytics={consentAnalytics}
        consentMarketing={consentMarketing}
        onChange={handleConsentChange}
      />

      {error && (
        <div className="bg-[var(--w-error)]/10 border border-[var(--w-error)]/30 rounded-lg px-3 py-2" data-testid="error-message">
          <p className="text-xs text-[var(--w-error)]">{error}</p>
        </div>
      )}

      <button
        onClick={handleSubmit}
        disabled={loading || !allRatingsFilled}
        data-testid="submit-btn"
        className={`w-full py-3 rounded-lg font-medium text-sm transition-all duration-300
          ${loading || !allRatingsFilled
            ? 'bg-[var(--w-surface-hl)] text-[var(--w-text-sec)] cursor-not-allowed'
            : 'bg-[var(--w-accent)] text-[var(--w-bg)] hover:brightness-110 active:scale-[0.98]'
          }`}
      >
        {loading ? (
          <span className="flex items-center justify-center gap-2">
            <Loader2 size={16} className="animate-spin" /> Saving...
          </span>
        ) : (
          mode === 'preference_only' ? 'Save My Preferences' : 'Submit Tasting'
        )}
      </button>
    </div>
  );
}
