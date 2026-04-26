import React, { useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { Coffee, ChevronRight, ChevronLeft, Sparkles, Check } from 'lucide-react';
import { apiCall } from '../utils/api';
import { useSessionId } from '../hooks/useSessionId';

const FLAVOR_TAGS = [
  { id: 'chocolate', label: 'Chocolate', emoji: '' },
  { id: 'caramel', label: 'Caramel', emoji: '' },
  { id: 'nutty', label: 'Nutty', emoji: '' },
  { id: 'citrus', label: 'Citrus', emoji: '' },
  { id: 'berry', label: 'Berry', emoji: '' },
  { id: 'tropical', label: 'Tropical', emoji: '' },
  { id: 'floral', label: 'Floral', emoji: '' },
  { id: 'tea-like', label: 'Tea-like', emoji: '' },
  { id: 'spicy', label: 'Spicy', emoji: '' },
  { id: 'funky', label: 'Funky', emoji: '' },
];

const STEPS = [
  { id: 'acidity', title: 'Acidity', subtitle: 'How bright or tangy do you like your coffee?' },
  { id: 'bitterness', title: 'Bitterness', subtitle: 'How much bitterness do you enjoy?' },
  { id: 'body', title: 'Body', subtitle: 'How does your ideal coffee feel in your mouth?' },
  { id: 'roast', title: 'Roast Level', subtitle: 'What roast do you usually reach for?' },
  { id: 'flavors', title: 'Flavor Notes', subtitle: 'Pick the flavors you love (up to 4)' },
  { id: 'drink_style', title: 'How You Drink', subtitle: 'How do you usually take your coffee?' },
  { id: 'budget', title: 'Budget', subtitle: 'What do you typically spend on a bag?' },
  { id: 'brew', title: 'Brew Method', subtitle: 'How do you make your coffee?' },
];

function ScaleStep({ value, onChange, labels, min = 1, max = 5 }) {
  const range = [];
  for (let i = min; i <= max; i++) range.push(i);
  return (
    <div className="flex flex-col items-center gap-6 py-4">
      <div className="flex gap-3">
        {range.map(n => (
          <button
            key={n}
            onClick={() => onChange(n)}
            data-testid={`quiz-scale-${n}`}
            className={`w-14 h-14 rounded-xl text-lg font-bold font-mono transition-all duration-300
              ${value === n
                ? 'bg-[#FFB74D] text-[#2C1810] scale-110 shadow-lg'
                : 'bg-[#3E2723] text-[#D7CCC8] hover:bg-[#4E342E] hover:scale-105'
              }`}
          >
            {n}
          </button>
        ))}
      </div>
      <div className="flex justify-between w-full max-w-xs text-xs text-[#8D6E63]">
        <span>{labels[0]}</span>
        <span>{labels[1]}</span>
      </div>
    </div>
  );
}

function OptionStep({ options, value, onChange, multi = false }) {
  const handleClick = (id) => {
    if (multi) {
      if (Array.isArray(value) && value.includes(id)) {
        onChange(value.filter(v => v !== id));
      } else {
        const arr = Array.isArray(value) ? value : [];
        if (arr.length < 4) onChange([...arr, id]);
      }
    } else {
      onChange(id);
    }
  };
  const isSelected = (id) => multi ? (Array.isArray(value) && value.includes(id)) : value === id;

  return (
    <div className="grid grid-cols-2 gap-3 py-4 max-w-md mx-auto">
      {options.map(opt => (
        <button
          key={opt.id}
          onClick={() => handleClick(opt.id)}
          data-testid={`quiz-option-${opt.id}`}
          className={`relative px-4 py-3.5 rounded-xl text-left text-sm font-medium transition-all duration-200
            ${isSelected(opt.id)
              ? 'bg-[#FFB74D] text-[#2C1810] ring-2 ring-[#FFB74D]'
              : 'bg-[#3E2723] text-[#D7CCC8] hover:bg-[#4E342E]'
            }`}
        >
          {isSelected(opt.id) && (
            <Check size={14} className="absolute top-2 right-2" />
          )}
          <span>{opt.label}</span>
          {opt.desc && <p className="text-[10px] mt-0.5 opacity-70">{opt.desc}</p>}
        </button>
      ))}
    </div>
  );
}

export default function TasteQuiz() {
  const navigate = useNavigate();
  const sessionId = useSessionId();
  const [step, setStep] = useState(0);
  const [answers, setAnswers] = useState({
    acidity_pref: null,
    bitterness_pref: null,
    body_pref: null,
    roast_pref: null,
    flavor_love_tags: [],
    drink_style: null,
    budget_band: null,
    brew_methods: [],
  });
  const [submitting, setSubmitting] = useState(false);
  const [existingProfile, setExistingProfile] = useState(false);

  useEffect(() => {
    apiCall(`/api/quiz/profile?session_id=${sessionId}`)
      .then(r => r.json())
      .then(d => {
        if (d.profile) {
          setAnswers({
            acidity_pref: d.profile.acidity_pref,
            bitterness_pref: d.profile.bitterness_pref,
            body_pref: d.profile.body_pref,
            roast_pref: d.profile.roast_pref,
            flavor_love_tags: d.profile.flavor_love_tags || [],
            drink_style: d.profile.drink_style,
            budget_band: d.profile.budget_band,
            brew_methods: d.profile.brew_methods || [],
          });
          setExistingProfile(true);
        }
      })
      .catch(() => {});
  }, [sessionId]);

  const currentStep = STEPS[step];
  const isLast = step === STEPS.length - 1;
  const progress = ((step + 1) / STEPS.length) * 100;

  const canAdvance = () => {
    const s = currentStep.id;
    if (s === 'acidity') return answers.acidity_pref != null;
    if (s === 'bitterness') return answers.bitterness_pref != null;
    if (s === 'body') return answers.body_pref != null;
    if (s === 'roast') return answers.roast_pref != null;
    if (s === 'flavors') return answers.flavor_love_tags.length > 0;
    if (s === 'drink_style') return answers.drink_style != null;
    if (s === 'budget') return answers.budget_band != null;
    if (s === 'brew') return answers.brew_methods.length > 0;
    return true;
  };

  const handleSubmit = async () => {
    setSubmitting(true);
    try {
      await apiCall('/api/quiz/submit', {
        method: 'POST',
        body: JSON.stringify({
          session_id: sessionId,
          acidity_pref: answers.acidity_pref,
          bitterness_pref: answers.bitterness_pref,
          body_pref: answers.body_pref,
          roast_pref: answers.roast_pref,
          budget_band: answers.budget_band,
          brew_methods: answers.brew_methods,
          drink_style: answers.drink_style,
          flavor_love_tags: answers.flavor_love_tags,
          consent_analytics: true,
          consent_marketing: false,
        }),
      });
      navigate('/demo/recommendations');
    } catch (err) {
      alert('Failed to save: ' + err.message);
    } finally {
      setSubmitting(false);
    }
  };

  const renderStepContent = () => {
    switch (currentStep.id) {
      case 'acidity':
        return <ScaleStep value={answers.acidity_pref} onChange={v => setAnswers(a => ({ ...a, acidity_pref: v }))} labels={['Mellow & smooth', 'Bright & tangy']} />;
      case 'bitterness':
        return <ScaleStep value={answers.bitterness_pref} onChange={v => setAnswers(a => ({ ...a, bitterness_pref: v }))} labels={['Minimal bitterness', 'Bold & bitter']} />;
      case 'body':
        return (
          <OptionStep
            value={answers.body_pref}
            onChange={v => setAnswers(a => ({ ...a, body_pref: v }))}
            options={[
              { id: 'light', label: 'Light', desc: 'Tea-like, delicate' },
              { id: 'balanced', label: 'Balanced', desc: 'Medium, versatile' },
              { id: 'thick', label: 'Full', desc: 'Thick, creamy, heavy' },
              { id: 'tea-like', label: 'Tea-like', desc: 'Silky, clean, airy' },
            ]}
          />
        );
      case 'roast':
        return (
          <OptionStep
            value={answers.roast_pref}
            onChange={v => setAnswers(a => ({ ...a, roast_pref: v }))}
            options={[
              { id: 'light', label: 'Light', desc: 'Fruity, acidic, complex' },
              { id: 'medium', label: 'Medium', desc: 'Balanced, sweet, smooth' },
              { id: 'dark', label: 'Dark', desc: 'Bold, chocolatey, smoky' },
              { id: 'not_sure', label: "I'm not sure", desc: 'Open to suggestions' },
            ]}
          />
        );
      case 'flavors':
        return (
          <div>
            <OptionStep
              value={answers.flavor_love_tags}
              onChange={v => setAnswers(a => ({ ...a, flavor_love_tags: v }))}
              multi
              options={FLAVOR_TAGS}
            />
            <p className="text-center text-[10px] text-[#8D6E63] mt-1">{answers.flavor_love_tags.length}/4 selected</p>
          </div>
        );
      case 'drink_style':
        return (
          <OptionStep
            value={answers.drink_style}
            onChange={v => setAnswers(a => ({ ...a, drink_style: v }))}
            options={[
              { id: 'black', label: 'Black', desc: 'Nothing added' },
              { id: 'with_milk', label: 'With milk', desc: 'Milk or cream' },
              { id: 'with_sugar', label: 'With sugar', desc: 'Sweetened' },
              { id: 'milk_sugar', label: 'Milk + sugar', desc: 'Both' },
              { id: 'depends', label: 'Depends', desc: 'Changes daily' },
            ]}
          />
        );
      case 'budget':
        return (
          <OptionStep
            value={answers.budget_band}
            onChange={v => setAnswers(a => ({ ...a, budget_band: v }))}
            options={[
              { id: 'under_15', label: 'Under $15', desc: 'Value picks' },
              { id: '15_20', label: '$15 – $20', desc: 'Solid range' },
              { id: '20_30', label: '$20 – $30', desc: 'Premium single-origin' },
              { id: '30_plus', label: '$30+', desc: 'Rare & exceptional' },
            ]}
          />
        );
      case 'brew':
        return (
          <OptionStep
            value={answers.brew_methods}
            onChange={v => setAnswers(a => ({ ...a, brew_methods: v }))}
            multi
            options={[
              { id: 'pour_over', label: 'Pour Over', desc: 'V60, Chemex, Kalita' },
              { id: 'espresso', label: 'Espresso', desc: 'Machine, Moka pot' },
              { id: 'french_press', label: 'French Press', desc: 'Immersion' },
              { id: 'aeropress', label: 'AeroPress', desc: 'Versatile' },
              { id: 'drip', label: 'Drip Machine', desc: 'Auto-brew' },
              { id: 'cold_brew', label: 'Cold Brew', desc: 'Overnight steep' },
            ]}
          />
        );
      default:
        return null;
    }
  };

  return (
    <div className="min-h-screen bg-[#2C1810] flex flex-col" data-testid="taste-quiz-page">
      {/* Header */}
      <header className="border-b border-[#3E2723] px-6 py-3 flex items-center justify-between">
        <Link to="/demo/collection" className="flex items-center gap-2">
          <Coffee size={20} className="text-[#FFB74D]" />
          <span className="font-heading font-semibold text-[#EFEBE9] text-lg">Unchained Coffee</span>
        </Link>
        <Link to="/demo/collection" className="text-xs text-[#8D6E63] hover:text-[#D7CCC8]" data-testid="skip-quiz-btn">
          Skip for now
        </Link>
      </header>

      {/* Progress bar */}
      <div className="h-1 bg-[#3E2723]">
        <div
          className="h-full bg-[#FFB74D] transition-all duration-500 ease-out"
          style={{ width: `${progress}%` }}
          data-testid="quiz-progress"
        />
      </div>

      {/* Content */}
      <div className="flex-1 flex flex-col items-center justify-center px-6 py-8">
        <div className="w-full max-w-lg">
          <div className="text-center mb-8">
            <p className="text-xs text-[#FFB74D] uppercase tracking-widest font-medium mb-2">
              Step {step + 1} of {STEPS.length}
            </p>
            <h2 className="font-heading text-3xl font-bold text-[#EFEBE9] mb-2" data-testid="quiz-step-title">
              {currentStep.title}
            </h2>
            <p className="text-sm text-[#8D6E63]">{currentStep.subtitle}</p>
          </div>

          {renderStepContent()}
        </div>
      </div>

      {/* Navigation */}
      <div className="px-6 py-5 border-t border-[#3E2723] flex items-center justify-between max-w-lg mx-auto w-full">
        <button
          onClick={() => setStep(s => Math.max(0, s - 1))}
          disabled={step === 0}
          data-testid="quiz-back-btn"
          className="flex items-center gap-1 px-4 py-2 rounded-lg text-sm text-[#8D6E63] hover:text-[#D7CCC8]
            disabled:opacity-30 disabled:cursor-not-allowed transition-colors"
        >
          <ChevronLeft size={16} /> Back
        </button>

        {isLast ? (
          <button
            onClick={handleSubmit}
            disabled={!canAdvance() || submitting}
            data-testid="quiz-submit-btn"
            className="flex items-center gap-2 px-6 py-2.5 rounded-xl bg-[#FFB74D] text-[#2C1810] text-sm font-bold
              hover:brightness-110 disabled:opacity-40 disabled:cursor-not-allowed transition-all"
          >
            <Sparkles size={16} /> {submitting ? 'Saving...' : 'Get My Matches'}
          </button>
        ) : (
          <button
            onClick={() => setStep(s => Math.min(STEPS.length - 1, s + 1))}
            disabled={!canAdvance()}
            data-testid="quiz-next-btn"
            className="flex items-center gap-1 px-5 py-2.5 rounded-xl bg-[#FFB74D] text-[#2C1810] text-sm font-bold
              hover:brightness-110 disabled:opacity-40 disabled:cursor-not-allowed transition-all"
          >
            Next <ChevronRight size={16} />
          </button>
        )}
      </div>
    </div>
  );
}
