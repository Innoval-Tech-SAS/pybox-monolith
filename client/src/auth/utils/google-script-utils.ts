const CLIENT_ID = import.meta.env.VITE_GOOGLE_CLIENT_ID as string;
const GOOGLE_SCRIPT_SRC = "https://accounts.google.com/gsi/client";

let activeCallback: ((token: string) => void) | null = null;
let scriptPromise: Promise<void> | null = null;
let initializedClientId: string | null = null;

const initializeGoogle = () => {
  if (!window.google?.accounts.id || initializedClientId === CLIENT_ID) return;

  window.google.accounts.id.initialize({
    client_id: CLIENT_ID,
    callback: (res) => activeCallback?.(res.credential),
  });
  initializedClientId = CLIENT_ID;
};

export const loadGoogleScript = () => {
  if (window.google?.accounts.id) {
    initializeGoogle();
    return Promise.resolve();
  }

  if (scriptPromise) return scriptPromise;

  scriptPromise = new Promise((resolve, reject) => {
    const finish = () => {
      initializeGoogle();
      resolve();
    };

    const existing = document.querySelector<HTMLScriptElement>(
      `script[src="${GOOGLE_SCRIPT_SRC}"]`,
    );
    if (existing) {
      existing.addEventListener("load", finish, { once: true });
      existing.addEventListener("error", () => reject(new Error("No se pudo cargar Google.")), {
        once: true,
      });
      return;
    }

    const script = document.createElement("script");
    script.src = GOOGLE_SCRIPT_SRC;
    script.async = true;
    script.defer = true;
    script.onload = finish;
    script.onerror = () => reject(new Error("No se pudo cargar Google."));
    document.head.appendChild(script);
  });

  return scriptPromise;
};

export const renderGoogleButton = (
  container: HTMLElement,
  width: number,
  onToken: (token: string) => void,
) => {
  activeCallback = onToken;
  return loadGoogleScript().then(() => {
    window.google?.accounts.id.renderButton(container, {
      type: "standard",
      theme: "outline",
      size: "large",
      width: width || 300,
    });
  });
};
