import { useCallback, useEffect, useRef } from "react";

interface GoogleCredentialResponse {
  credential: string;
}

declare global {
  interface Window {
    google: {
      accounts: {
        id: {
          initialize: (config: {
            client_id: string;
            callback: (res: GoogleCredentialResponse) => void;
          }) => void;
          prompt: () => void;
          cancel: () => void;
        };
      };
    };
  }
}

const CLIENT_ID = import.meta.env.VITE_GOOGLE_CLIENT_ID as string;

export const useGoogleAuth = () => {
  const callbackRef = useRef<((token: string) => void) | null>(null);
  const initialized = useRef(false);

  useEffect(() => {
    const existing = document.querySelector('script[src="https://accounts.google.com/gsi/client"]');
    if (existing) return;

    const script = document.createElement("script");
    script.src = "https://accounts.google.com/gsi/client";
    script.async = true;
    script.defer = true;
    script.onload = () => {
      window.google.accounts.id.initialize({
        client_id: CLIENT_ID,
        callback: (res) => callbackRef.current?.(res.credential),
      });
      initialized.current = true;
    };
    document.head.appendChild(script);
  }, []);

  const signIn = useCallback((onToken: (token: string) => void) => {
    callbackRef.current = onToken;
    if (initialized.current) {
      window.google.accounts.id.prompt();
    }
  }, []);

  return { signIn };
};
