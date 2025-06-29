import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        background: '#131722',
        primary: '#1e222d',
        secondary: '#2a2f3b',
        accent: {
          DEFAULT: '#818cf8',
          green: '#4ade80',
          red: '#f87171',
        },
        'text-main': '#e2e8f0',
        'text-secondary': '#94a3b8',
      },
    },
  },
  plugins: [],
};
export default config;