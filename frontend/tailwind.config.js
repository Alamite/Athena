/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  theme: {
    extend: {
      keyframes: {
        'owl-bob': {
          '0%, 100%': { transform: 'translateY(0) rotate(0deg)' },
          '50%': { transform: 'translateY(-3px) rotate(-3deg)' },
        },
        'owl-blink': {
          '0%, 90%, 100%': { transform: 'scaleY(1)' },
          '95%': { transform: 'scaleY(0.1)' },
        },
      },
      animation: {
        'owl-bob': 'owl-bob 1.6s ease-in-out infinite',
        'owl-blink': 'owl-blink 3s ease-in-out infinite',
      },
    },
  },
  plugins: [],
}
