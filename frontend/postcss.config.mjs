/** @type {import('postcss-load-config').Config} */
const config = {
  plugins: {
    '@tailwindcss/postcss': {}, // A correção foi aplicada nesta linha
    autoprefixer: {},
  },
};

export default config;