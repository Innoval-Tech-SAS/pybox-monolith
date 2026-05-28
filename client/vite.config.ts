import path from "path";
import svgr from "vite-plugin-svgr";
import { defineConfig } from "vite";
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
    proxy: {
      "/api": {
        target: "http://localhost:5000",
        changeOrigin: true,
        ws: true,
      },
      "/files": {
        target: "http://localhost:5000",
        changeOrigin: true,
      },
    },
  },
});
