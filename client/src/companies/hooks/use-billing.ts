import { useCallback, useEffect, useState } from "react";
import { useApiClient } from "@/hooks/use-api-client";
import type {
  CurrentInvoiceResponse,
  Invoice,
  ListInvoicesResponse,
  TenantBillingStatus,
} from "@/types/billing/billing-types";

/** Resumen de facturación de una organización: factura vigente, listado y estado de bloqueo. */
export const useBilling = (organizationId: string) => {
  const { apiClient } = useApiClient();
  const [currentInvoice, setCurrentInvoice] = useState<Invoice | null>(null);
  const [invoices, setInvoices] = useState<Invoice[]>([]);
  const [total, setTotal] = useState(0);
  const [status, setStatus] = useState<TenantBillingStatus | null>(null);
  const [loading, setLoading] = useState(true);

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

  return {
    currentInvoice,
    invoices,
    total,
    status,
    loading,
    fetchPage: fetchAll,
    refetch: fetchAll,
  };
};
