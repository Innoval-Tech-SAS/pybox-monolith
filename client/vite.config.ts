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
        configure: (proxy) => {
          // Vite registers its own error logger first; we replace it so socket hang ups
          // (expected when the API container restarts) don't pollute the terminal.
          proxy.removeAllListeners("error");
          proxy.on("error", (_err, _req, res) => {
            if (res && "writeHead" in res && !res.headersSent) {
              res.writeHead(502);
              res.end();
            }
            // WS errors: res is a Socket — nothing to write, browser reconnects automatically
          });
        },
      },
      "/files": {
        target: "http://localhost:5000",
        changeOrigin: true,
      },
    },
  },
});
