module.exports = {
  content: ['./src/**/*.{js,jsx}'],
  theme: {
    extend: {
      fontFamily: {
        heading: ['Fraunces', 'serif'],
        body: ['Inter', 'sans-serif'],
        mono: ['JetBrains Mono', 'monospace'],
      },
      colors: {
        widget: {
          bg: 'var(--w-bg)',
          surface: 'var(--w-surface)',
          'surface-hl': 'var(--w-surface-hl)',
          text: 'var(--w-text)',
          'text-sec': 'var(--w-text-sec)',
          accent: 'var(--w-accent)',
          error: 'var(--w-error)',
          success: 'var(--w-success)',
        },
        admin: {
          bg: 'var(--a-bg)',
          surface: 'var(--a-surface)',
          border: 'var(--a-border)',
          text: 'var(--a-text)',
          'text-sec': 'var(--a-text-sec)',
          primary: 'var(--a-primary)',
        }
      }
    }
  },
  plugins: []
};
