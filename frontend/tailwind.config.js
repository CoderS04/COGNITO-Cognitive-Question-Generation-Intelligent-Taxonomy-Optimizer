/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        brand: {
          50: '#f0f7ff',
          100: '#e0effe',
          200: '#bae0fd',
          300: '#7cc7fb',
          400: '#38a9f7',
          500: '#0e8de9',
          600: '#026fc7',
          700: '#0358a1',
          800: '#074b85',
          900: '#0c3f6e',
          950: '#082849',
        },
        bloom: {
          l1: '#10B981', // Remember - Green
          l2: '#06B6D4', // Understand - Cyan
          l3: '#3B82F6', // Apply - Blue
          l4: '#8B5CF6', // Analyze - Purple
          l5: '#F59E0B', // Evaluate - Amber
          l6: '#EF4444', // Create - Red
        }
      }
    },
  },
  plugins: [],
}
