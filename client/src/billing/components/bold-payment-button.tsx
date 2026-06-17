import { useEffect, useRef } from "react";
import type { PaymentLinkData } from "@/types/billing/billing-types";

// Docs: https://developers.bold.co/pagos-en-linea/boton-de-pagos/integracion-manual
const BOLD_SCRIPT_SRC = "https://checkout.bold.co/library/boldPaymentButton.js";

let boldScriptPromise: Promise<void> | null = null;

const loadBoldScript = (): Promise<void> => {
  if (boldScriptPromise) return boldScriptPromise;
  boldScriptPromise = new Promise((resolve, reject) => {
    if (document.querySelector(`script[src="${BOLD_SCRIPT_SRC}"]`)) {
      resolve();
      return;
    }
    const script = document.createElement("script");
    script.src = BOLD_SCRIPT_SRC;
    script.async = true;
    script.onload = () => resolve();
    script.onerror = () => reject(new Error("No se pudo cargar el botón de pagos Bold"));
    document.head.appendChild(script);
  });
  return boldScriptPromise;
};

interface BoldPaymentButtonProps {
  data: PaymentLinkData;
  /** Estilo del boton: "dark"|"light" + "S"|"M"|"L", ej. "dark-L" */
  style?: string;
}

export const BoldPaymentButton: React.FC<BoldPaymentButtonProps> = ({ data, style = "dark-L" }) => {
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const container = containerRef.current;
    if (!container) return;
    let cancelled = false;

    loadBoldScript()
      .then(() => {
        if (cancelled || !container) return;
        container.innerHTML = "";

        const buttonScript = document.createElement("script");
        buttonScript.setAttribute("data-bold-button", style);
        buttonScript.setAttribute("data-api-key", data.apiKey);
        buttonScript.setAttribute("data-order-id", data.orderId);
        buttonScript.setAttribute("data-currency", data.currency);
        buttonScript.setAttribute("data-amount", String(data.amount));
        buttonScript.setAttribute("data-integrity-signature", data.integritySignature);
        buttonScript.setAttribute("data-redirection-url", data.redirectionUrl);
        buttonScript.setAttribute("data-description", data.description);
        buttonScript.setAttribute("data-render-mode", "embedded");
        if (data.boldTax) {
          buttonScript.setAttribute("data-tax", data.boldTax);
        }
        container.appendChild(buttonScript);
      })
      .catch(() => {});

    return () => {
      cancelled = true;
      if (container) container.innerHTML = "";
    };
  }, [data, style]);

  return <div ref={containerRef} />;
};
