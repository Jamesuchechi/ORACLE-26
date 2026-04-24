/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        bg: "#0a0b0d",
        bg1: "#0f1114",
        bg2: "#141720",
        bg3: "#1a1f2e",
        amber: "#e8a030",
        teal: "#2dd4a0",
        red: "#e85d4a",
        blue: "#5b9cf6",
        coral: "#e87060",
      },
      fontFamily: {
        mono: ['DM Mono', 'monospace'],
        sans: ['Syne', 'sans-serif'],
      },
      animation: {
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
      },
    },
  },
  plugins: [],
}
