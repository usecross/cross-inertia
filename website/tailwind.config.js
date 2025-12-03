/** @type {import('tailwindcss').Config} */
export default {
  darkMode: 'class',
  content: ['./frontend/**/*.{ts,tsx}', './templates/**/*.html'],
  theme: {
    extend: {
      maxWidth: {
        '8xl': '88rem',
      },
      fontFamily: {
        sans: ['system-ui', '-apple-system', 'Segoe UI', 'Roboto', 'Helvetica', 'Arial', 'sans-serif', 'Apple Color Emoji', 'Segoe UI Emoji', 'Segoe UI Symbol'],
        heading: ['"roc-grotesk"', 'sans-serif'],
        mono: ['Fira Code', 'Consolas', 'Monaco', 'Andale Mono', 'monospace'],
      },
      colors: {
        // Cross-Inertia brand colors (green)
        primary: {
          50: '#f4f7f3',
          100: '#e6ece4',
          200: '#cddac9',
          300: '#a9c1a2',
          400: '#7fa276',
          500: '#648C57',
          600: '#4d7043',
          700: '#3e5937',
          800: '#34482f',
          900: '#2c3c28',
          950: '#151f13',
        },
        // Dark colors for code blocks
        dark: {
          800: '#1e293b',
          900: '#0f172a',
        },
      },
      typography: (theme) => ({
        DEFAULT: {
          css: {
            maxWidth: 'none',
            color: theme('colors.gray.700'),
            a: {
              color: theme('colors.primary.600'),
              '&:hover': {
                color: theme('colors.primary.700'),
              },
            },
            'code::before': {
              content: '""',
            },
            'code::after': {
              content: '""',
            },
            code: {
              backgroundColor: theme('colors.gray.100'),
              padding: '0.25rem 0.375rem',
              borderRadius: '0.25rem',
              fontWeight: '500',
            },
          },
        },
        invert: {
          css: {
            color: theme('colors.gray.300'),
            a: {
              color: theme('colors.primary.400'),
              '&:hover': {
                color: theme('colors.primary.300'),
              },
            },
            code: {
              backgroundColor: theme('colors.gray.800'),
            },
          },
        },
      }),
    },
  },
  plugins: [
    require('@tailwindcss/typography'),
  ],
}
