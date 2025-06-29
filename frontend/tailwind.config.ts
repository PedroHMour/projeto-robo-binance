import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      // Aqui estamos adicionando nossa paleta de cores customizada
      colors: {
        background: '#131722', // Nosso fundo principal
        primary: '#1e222d',    // Cor dos cards e elementos
        secondary: '#2a2f3b',  // Cor para hover e detalhes
        accent: {
          DEFAULT: '#818cf8', // Nosso violeta/índigo principal
          green: '#4ade80',  // Verde para ganhos
          red: '#f87171',    // Vermelho para perdas
        },
        'text-main': '#e2e8f0', // Texto principal (slate-200)
        'text-secondary': '#94a3b8', // Texto secundário (slate-400)
      },
    },
  },
  plugins: [],
};
export default config;