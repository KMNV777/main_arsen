import { defineConfig } from "vite";

export default defineConfig({
  root: ".",
  server: {
    host: "0.0.0.0",
    port: 8080,
    strictPort: true,
    open: false,
  },
  preview: {
    host: "0.0.0.0",
    port: 8080,
    strictPort: true,
  },
});
