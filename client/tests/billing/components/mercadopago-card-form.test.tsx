import { fireEvent, render, waitFor } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
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

const MP_SCRIPT_SRC = "https://sdk.mercadopago.com/js/v2";

const paymentData: PaymentLinkData = {
  provider: "MERCADO_PAGO",
  orderId: "ord_1",
  amount: 5000,
  currency: "COP",
  description: "test",
  taxType: "IVA",
  attemptId: "att_1",
  reused: false,
  providerPayload: {
    publicKey: "TEST-public-key",
    orderId: "ord_1",
    clientToken: null,
  },
};

// Fake mínimo del Secure Field del SDK: expone on()/emit() para simular el evento
// binChange que el componente usa para resolver paymentMethodId/paymentTypeId.
class FakeSecureField {
  private handlers: Record<string, (data: { bin?: string }) => void | Promise<void>> = {};
  mount() {
    return this;
  }
  on(event: string, handler: (data: { bin?: string }) => void | Promise<void>) {
    this.handlers[event] = handler;
  }
  unmount() {}
  async emit(event: string, data: { bin?: string }) {
    await this.handlers[event]?.(data);
  }
}

let lastCardNumberField: FakeSecureField | null = null;
const createCardTokenMock = vi.fn();
const getPaymentMethodsMock = vi.fn();
const getIdentificationTypesMock = vi.fn();

function MockMercadoPago(this: any) {
  this.fields = {
    create: (field: string) => ({
      mount: () => {
        const instance = new FakeSecureField();
        if (field === "cardNumber") lastCardNumberField = instance;
        return instance;
      },
    }),
    createCardToken: createCardTokenMock,
  };
  this.getIdentificationTypes = getIdentificationTypesMock;
  this.getPaymentMethods = getPaymentMethodsMock;
}

// Espera a que el script del SDK "cargue" y a que el componente termine su
// inicialización async (getIdentificationTypes) antes de habilitar el submit.
const renderReady = async (onCharge = vi.fn().mockResolvedValue(undefined)) => {
  const { MercadoPagoCardForm } = await import("@/billing/components/mercadopago-card-form");
  const utils = render(<MercadoPagoCardForm data={paymentData} onCharge={onCharge} />);

  const script = document.head.querySelector(`script[src="${MP_SCRIPT_SRC}"]`);
  script!.dispatchEvent(new Event("load"));

  await waitFor(() => {
    expect(utils.getByRole("button", { name: /Pagar con tarjeta/ })).not.toBeDisabled();
  });

  return { ...utils, onCharge };
};

describe("MercadoPagoCardForm", () => {
  beforeEach(() => {
    // mpScriptPromise vive a nivel de módulo (singleton entre instancias del
    // formulario) -- vi.resetModules + import dinámico da un estado limpio por
    // test, igual que el patrón usado para bold-payment-button.
    vi.resetModules();
    document.head.innerHTML = "";
    lastCardNumberField = null;
    toastErrorMock.mockClear();
    createCardTokenMock.mockReset();
    getPaymentMethodsMock.mockReset().mockResolvedValue({ results: [] });
    getIdentificationTypesMock.mockReset().mockResolvedValue([]);
    vi.stubGlobal("MercadoPago", MockMercadoPago as unknown as typeof window.MercadoPago);
  });

  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("shows a toast and skips tokenization when the cardholder name is empty", async () => {
    await renderReady();
    const form = document.querySelector("form")!;

    fireEvent.submit(form);

    await waitFor(() => {
      expect(toastErrorMock).toHaveBeenCalledWith("Error", "Completa los datos del titular de la tarjeta");
    });
    expect(createCardTokenMock).not.toHaveBeenCalled();
  });

  it("shows an error toast and re-enables the submit button when the SDK rejects the token", async () => {
    getPaymentMethodsMock.mockResolvedValue({ results: [{ id: "visa", payment_type_id: "credit_card" }] });
    createCardTokenMock.mockRejectedValue(new Error("token error"));
    const { getByRole, getByPlaceholderText } = await renderReady();

    await lastCardNumberField!.emit("binChange", { bin: "411111" });

    fireEvent.change(getByPlaceholderText("Como aparece en la tarjeta"), { target: { value: "Ana Test" } });

    const form = document.querySelector("form")!;
    fireEvent.submit(form);

    await waitFor(() => {
      expect(toastErrorMock).toHaveBeenCalledWith(
        "Error",
        "No se pudo procesar el pago, verifica los datos de la tarjeta",
      );
    });
    expect(getByRole("button", { name: /Pagar con tarjeta/ })).not.toBeDisabled();
  });

  it("invokes onCharge only once on a rapid double submit", async () => {
    getPaymentMethodsMock.mockResolvedValue({ results: [{ id: "visa", payment_type_id: "credit_card" }] });
    createCardTokenMock.mockResolvedValue({ id: "tok_123" });
    const onCharge = vi.fn().mockResolvedValue(undefined);
    const { getByPlaceholderText } = await renderReady(onCharge);

    await lastCardNumberField!.emit("binChange", { bin: "411111" });

    fireEvent.change(getByPlaceholderText("Como aparece en la tarjeta"), { target: { value: "Ana Test" } });

    const form = document.querySelector("form")!;
    fireEvent.submit(form);
    fireEvent.submit(form);

    await waitFor(() => {
      expect(onCharge).toHaveBeenCalledTimes(1);
    });
  });
});
