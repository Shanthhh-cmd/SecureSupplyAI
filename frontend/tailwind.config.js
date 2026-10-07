/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        dark: {
          bg: '#0B0F19',
          card: '#111827',
          border: '#1F2937',
          hover: '#1F2937'
        },
        cyber: {
          blue: '#00F0FF',
          green: '#00FF66',
          purple: '#7000FF',
          red: '#FF0055',
          warning: '#FFB800'
        }
      }
    },
  },
  plugins: [],
}
