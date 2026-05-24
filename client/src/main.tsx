import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { GoogleOAuthProvider } from "@react-oauth/google";

import "./index.css";
import "flag-icons/css/flag-icons.min.css";
import "driver.js/dist/driver.css";
import "./companies/styles/tour.css";
import { App } from "./app.tsx";
import { AppWrapper } from "./ui/pages/app-wrapper";
import { ThemeProvider } from "./ui/contexts/providers/theme-provider";

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <GoogleOAuthProvider clientId={import.meta.env.VITE_GOOGLE_CLIENT_ID}>
      <AppWrapper>
        <ThemeProvider>
          <App />
        </ThemeProvider>
      </AppWrapper>
    </GoogleOAuthProvider>
  </StrictMode>,
);
