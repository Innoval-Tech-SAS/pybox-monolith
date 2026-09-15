import { useCallback } from "react";
import { useApiClient } from "@/hooks/use-api-client";
import { useAsyncResource } from "@/hooks/use-async-resource";
import type {
  CurrentInvoiceResponse,
  Invoice,
  ListInvoicesResponse,
  TenantBillingStatus,
} from "@/types/billing/billing-types";

interface BillingData {
  currentInvoice: Invoice | null;
  invoices: Invoice[];
  total: number;
  status: TenantBillingStatus | null;
}

const EMPTY_DATA: BillingData = { currentInvoice: null, invoices: [], total: 0, status: null };

/** Resumen de facturación de una organización: factura vigente, listado y estado de bloqueo. */
export const useBilling = (organizationId: string) => {
  const { apiClient } = useApiClient();

  const fetchBilling = useCallback(() => {
    if (!organizationId) return Promise.resolve(EMPTY_DATA);
    return Promise.all([
      apiClient(`/billing/current-invoice?organizationId=${organizationId}`, { method: "GET" }),
      apiClient(`/billing/invoices?organizationId=${organizationId}&page=1&limit=20`, { method: "GET" }),
      apiClient(`/billing/status?organizationId=${organizationId}`, { method: "GET" }),
    ]).then(
      ([current, list, billingStatus]: [CurrentInvoiceResponse, ListInvoicesResponse, TenantBillingStatus]) => ({
        currentInvoice: current?.invoice ?? null,
        invoices: list?.invoices ?? [],
        total: list?.total ?? 0,
        status: billingStatus ?? null,
      }),
    );
  }, [organizationId, apiClient]);

  const { data, loading, error, refetch } = useAsyncResource<BillingData>(fetchBilling, EMPTY_DATA, [organizationId]);

  return { ...data, loading, error, refetch };
};
