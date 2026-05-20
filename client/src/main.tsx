import { StrictMode } from "react";
import { createRoot } from "react-dom/client";

import { AppWrapper } from "./ui/pages/app-wrapper";
import { ThemeProvider } from "./ui/contexts/providers/theme-provider";
import "./index.css";
import { App } from "./app.tsx";

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <AppWrapper>
      <ThemeProvider>
        <App />
      </ThemeProvider>
    </AppWrapper>
  </StrictMode>
);
