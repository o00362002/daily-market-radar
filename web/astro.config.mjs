import { defineConfig } from 'astro/config';

// GitHub Pages: site + base come from the environment so the repository subpath
// is never hardcoded. Static, zero-JS-first output.
const site = process.env.PAGES_SITE || 'https://o00362002.github.io';
const base = process.env.PAGES_BASE || '/daily-market-radar';

export default defineConfig({
  site,
  base,
  output: 'static',
  trailingSlash: 'ignore',
  build: { format: 'directory' },
  devToolbar: { enabled: false },
});
