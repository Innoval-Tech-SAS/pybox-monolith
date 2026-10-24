import { useEffect, useRef } from "react";
import { useToast } from "@/context/toast-context";
import type { BoldProviderPayload, PaymentLinkData } from "@/types/billing/billing-types";
import { BOLD_SCRIPT_SRC } from "../constants/payment-provider-scripts";
import { loadExternalScript } from "../utils/load-external-script";

/** Monta el botón embebido de Bold dentro del contenedor referenciado, cargando su script una sola vez. */
export const useBoldPaymentButton = (data: PaymentLinkData, style: string) => {
  const containerRef = useRef<HTMLDivElement>(null);
  const payload = data.providerPayload as BoldProviderPayload;
  const { error: toastError } = useToast();

  useEffect(() => {
    const container = containerRef.current;
    if (!container) return;
    let cancelled = false;

    loadExternalScript(BOLD_SCRIPT_SRC, "No se pudo cargar el botón de pagos Bold")
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

  return containerRef;
};
