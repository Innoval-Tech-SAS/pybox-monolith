import { render, waitFor } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import type { PaymentLinkData } from "@/types/billing/billing-types";

const toastErrorMock = vi.fn();
vi.mock("@/context/toast-context", () => ({
  useToast: () => ({
    error: toastErrorMock,
    success: vi.fn(),
    info: vi.fn(),
    warning: vi.fn(),
    toasts: [],
    dismiss: vi.fn(),
  }),
}));

const BOLD_SCRIPT_SRC = "https://checkout.bold.co/library/boldPaymentButton.js";

const paymentData: PaymentLinkData = {
  provider: "BOLD",
  orderId: "ord_1",
  amount: 1000,
  currency: "COP",
  description: "test",
  taxType: "IVA",
  attemptId: "att_1",
  reused: false,
  providerPayload: {
    apiKey: "key",
    integritySignature: "sig",
    redirectionUrl: "https://example.com/return",
    boldTax: null,
  },
};

describe("BoldPaymentButton", () => {
  beforeEach(() => {
    vi.resetModules();
    toastErrorMock.mockClear();
    document.head.innerHTML = "";
  });

  it("shows an error toast when the Bold script fails to load", async () => {
    // El módulo memoriza `boldScriptPromise` a nivel de módulo (singleton entre
    // instancias del botón) -- vi.resetModules + import dinámico da un estado
    // limpio por test en vez de arrastrar la promesa cacheada del test anterior.
    const { BoldPaymentButton } = await import("@/billing/components/bold-payment-button");
    render(<BoldPaymentButton data={paymentData} />);

    const script = document.head.querySelector(`script[src="${BOLD_SCRIPT_SRC}"]`);
    expect(script).not.toBeNull();

    script!.dispatchEvent(new Event("error"));

    await waitFor(() => {
      expect(toastErrorMock).toHaveBeenCalledWith("Error", "No se pudo cargar el botón de pagos Bold");
    });
  });

  it("renders the button script once the loader script resolves", async () => {
    const { BoldPaymentButton } = await import("@/billing/components/bold-payment-button");
    const { container } = render(<BoldPaymentButton data={paymentData} />);

    const script = document.head.querySelector(`script[src="${BOLD_SCRIPT_SRC}"]`);
    script!.dispatchEvent(new Event("load"));

    await waitFor(() => {
      expect(container.querySelector("script[data-bold-button]")).not.toBeNull();
    });
    expect(toastErrorMock).not.toHaveBeenCalled();
  });
});
