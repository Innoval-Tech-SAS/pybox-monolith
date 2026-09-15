const scriptPromises = new Map<string, Promise<void>>();

/** Inyecta un <script> externo una sola vez y cachea la promesa de carga por src. */
export const loadExternalScript = (src: string, errorMessage: string): Promise<void> => {
  const cached = scriptPromises.get(src);
  if (cached) return cached;

  const promise = new Promise<void>((resolve, reject) => {
    if (document.querySelector(`script[src="${src}"]`)) {
      resolve();
      return;
    }
    const script = document.createElement("script");
    script.src = src;
    script.async = true;
    script.onload = () => resolve();
    script.onerror = () => reject(new Error(errorMessage));
    document.head.appendChild(script);
  });

  scriptPromises.set(src, promise);
  return promise;
};
