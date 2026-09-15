import { useEffect, useRef } from "react";
import { useToast } from "@/context/toast-context";
import type { BoldProviderPayload } from "@/types/billing/billing-types";
import type { BoldPaymentButtonProps } from "@/types/props/bold-payment-button-props";

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

export const BoldPaymentButton: React.FC<BoldPaymentButtonProps> = ({ data, style = "dark-L" }) => {
  const containerRef = useRef<HTMLDivElement>(null);
  const payload = data.providerPayload as BoldProviderPayload;
  const { error: toastError } = useToast();

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
        buttonScript.setAttribute("data-api-key", payload.apiKey);
        buttonScript.setAttribute("data-order-id", data.orderId);
        buttonScript.setAttribute("data-currency", data.currency);
        buttonScript.setAttribute("data-amount", String(data.amount));
        buttonScript.setAttribute("data-integrity-signature", payload.integritySignature);
        buttonScript.setAttribute("data-redirection-url", payload.redirectionUrl);
        buttonScript.setAttribute("data-description", data.description);
        buttonScript.setAttribute("data-render-mode", "embedded");
        if (payload.boldTax) {
          buttonScript.setAttribute("data-tax", payload.boldTax);
        }
        container.appendChild(buttonScript);
      })
      .catch(() => {
        if (!cancelled) toastError("Error", "No se pudo cargar el botón de pagos Bold");
      });

    return () => {
      cancelled = true;
      if (container) container.innerHTML = "";
    };
  }, [data, payload, style, toastError]);

  return <div ref={containerRef} />;
};
