import path from "path";
import svgr from "vite-plugin-svgr";
// `vitest/config` reexporta `defineConfig` de vite con el campo `test` tipado --
// mismo archivo sirve para `vite build/dev` y para `vitest`, sin cambiar nada del
// comportamiento normal de Vite.
import { defineConfig } from "vitest/config";
import tailwindcss from "@tailwindcss/vite";
import react from "@vitejs/plugin-react-swc";

export default defineConfig({
  plugins: [
    react(),
    tailwindcss(),
    svgr({
      svgrOptions: {
        icon: true,
        exportType: "named",
        namedExport: "ReactComponent",
      },
    }),
  ],
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },
  server: {
    port: 4200,
  },
  test: {
    environment: "jsdom",
    globals: true,
    setupFiles: ["./vitest.setup.ts"],
    // Los tests viven en tests/ (espejo de src/), nunca junto al código fuente.
    include: ["tests/**/*.test.{ts,tsx}"],
  },
});
