import { useCallback, useEffect, useState } from "react";
import { useApiClient } from "@/hooks/use-api-client";
import type {
  CurrentInvoiceResponse,
  Invoice,
  ListInvoicesResponse,
  PaymentLinkData,
  TenantBillingStatus,
} from "@/types/billing/billing-types";

export const useBilling = (organizationId: string) => {
  const { apiClient } = useApiClient();
  const [currentInvoice, setCurrentInvoice] = useState<Invoice | null>(null);
  const [invoices, setInvoices] = useState<Invoice[]>([]);
  const [total, setTotal] = useState(0);
  const [status, setStatus] = useState<TenantBillingStatus | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);

  const fetchAll = useCallback(
    (page = 1, limit = 20) => {
      if (!organizationId) return;
      setLoading(true);
      Promise.all([
        apiClient(`/billing/current-invoice?organizationId=${organizationId}`, { method: "GET" }),
        apiClient(`/billing/invoices?organizationId=${organizationId}&page=${page}&limit=${limit}`, {
          method: "GET",
        }),
        apiClient(`/billing/status?organizationId=${organizationId}`, { method: "GET" }),
      ])
        .then(
          ([current, list, billingStatus]: [
            CurrentInvoiceResponse,
            ListInvoicesResponse,
            TenantBillingStatus,
          ]) => {
            setCurrentInvoice(current?.invoice ?? null);
            setInvoices(list?.invoices ?? []);
            setTotal(list?.total ?? 0);
            setStatus(billingStatus ?? null);
          },
        )
        .catch(() => {})
        .finally(() => setLoading(false));
    },
    [organizationId, apiClient],
  );

  useEffect(() => {
    fetchAll();
  }, [fetchAll]);

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

  return {
    currentInvoice,
    invoices,
    total,
    status,
    loading,
    saving,
    fetchPage: fetchAll,
    refetch: fetchAll,
    getInvoice,
    createPaymentLink,
    syncInvoice,
  };
};
