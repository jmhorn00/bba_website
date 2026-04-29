/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    // All Django templates
    '../../**/templates/**/*.html',
    // Python files (for class strings in views)
    '../../**/*.py',
  ],
  theme: {
    extend: {
      colors: {
        navy:   '#1c3a5e',
        gold:   '#c9a84c',
        cream:  '#f7f5f0',
        dark:   '#1c1c1c',
        muted:  '#555555',
        border: '#e8e3d8',
      },
      fontFamily: {
        serif: ['"Playfair Display"', 'Georgia', 'serif'],
        sans:  ['"DM Sans"', 'Arial', 'sans-serif'],
      },
      typography: {
        DEFAULT: {
          css: {
            color: '#555555',
            a: { color: '#c9a84c' },
            h1: { color: '#1c3a5e', fontFamily: '"Playfair Display", Georgia, serif' },
            h2: { color: '#1c3a5e', fontFamily: '"Playfair Display", Georgia, serif' },
            h3: { color: '#1c3a5e' },
          },
        },
      },
    },
  },
  plugins: [],
};
