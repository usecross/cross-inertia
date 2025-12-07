/** @type {import('tailwindcss').Config} */
export default {
  darkMode: 'class',
  content: [
    './frontend/**/*.{ts,tsx}',
    './templates/**/*.html',
    // Include @usecross/docs components
    './node_modules/@usecross/docs/src/**/*.{ts,tsx}',
  ],
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
        // Cross-Inertia brand colors (green) - using CSS variable for theming
        primary: {
          50: 'color-mix(in srgb, var(--color-primary-500, #648C57) 5%, white)',
          100: 'color-mix(in srgb, var(--color-primary-500, #648C57) 10%, white)',
          200: 'color-mix(in srgb, var(--color-primary-500, #648C57) 20%, white)',
          300: 'color-mix(in srgb, var(--color-primary-500, #648C57) 40%, white)',
          400: 'color-mix(in srgb, var(--color-primary-500, #648C57) 70%, white)',
          500: 'var(--color-primary-500, #648C57)',
          600: 'color-mix(in srgb, var(--color-primary-500, #648C57) 90%, black)',
          700: 'color-mix(in srgb, var(--color-primary-500, #648C57) 70%, black)',
          800: 'color-mix(in srgb, var(--color-primary-500, #648C57) 50%, black)',
          900: 'color-mix(in srgb, var(--color-primary-500, #648C57) 30%, black)',
          950: 'color-mix(in srgb, var(--color-primary-500, #648C57) 15%, black)',
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
