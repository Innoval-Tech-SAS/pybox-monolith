import { useCallback, useState } from "react";
import { useApiClient } from "@/hooks/use-api-client";
import type { Invoice, PaymentLinkData } from "@/types/billing/billing-types";

/** Acciones sobre una factura puntual (consultar, generar enlace de pago, sincronizar). */
export const useBillingActions = (organizationId: string) => {
  const { apiClient } = useApiClient();
  const [saving, setSaving] = useState(false);

  const getInvoice = useCallback(
    async (invoiceId: string): Promise<Invoice | null> => {
      try {
        return await apiClient(`/billing/invoices/${invoiceId}?organizationId=${organizationId}`, {
          method: "GET",
        });
      } catch {
        return null;
      }
    },
    [organizationId, apiClient],
  );

  const createPaymentLink = async (invoiceId: string): Promise<PaymentLinkData | null> => {
    setSaving(true);
    try {
      return await apiClient(`/billing/invoices/${invoiceId}/payment-link?organizationId=${organizationId}`, {
        method: "POST",
      });
    } catch {
      return null;
    } finally {
      setSaving(false);
    }
  };

  const syncInvoice = async (invoiceId: string): Promise<Invoice | null> => {
    setSaving(true);
    try {
      return await apiClient(`/billing/invoices/${invoiceId}/sync?organizationId=${organizationId}`, {
        method: "POST",
      });
    } catch {
      return null;
    } finally {
      setSaving(false);
    }
  };

  const chargeMercadoPago = async (
    invoiceId: string,
    attemptId: string,
    token: string,
    paymentMethodId: string,
    paymentTypeId: string,
    installments: number,
  ): Promise<Invoice | null> => {
    setSaving(true);
    try {
      return await apiClient(
        `/billing/invoices/${invoiceId}/attempts/${attemptId}/mercadopago/charge?organizationId=${organizationId}`,
        {
          method: "POST",
          body: JSON.stringify({ token, paymentMethodId, paymentTypeId, installments }),
        },
      );
    } catch {
      return null;
    } finally {
      setSaving(false);
    }
  };

  return { saving, getInvoice, createPaymentLink, syncInvoice, chargeMercadoPago };
};
