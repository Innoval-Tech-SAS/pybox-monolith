import { useCallback } from "react";
import { useApiClient } from "@/hooks/use-api-client";
import { useAsyncResource } from "@/hooks/use-async-resource";
import type { CurrentInvoiceResponse, ListInvoicesResponse, TenantBillingStatus } from "@/types/billing/billing-types";
import type { BillingSummary } from "../types/billing-summary-types";
import { BILLING_SUMMARY_INVOICE_FETCH_LIMIT } from "../constants/pagination";

const EMPTY_DATA: BillingSummary = { currentInvoice: null, invoices: [], total: 0, status: null };

/** Resumen de facturación de una organización: factura vigente, listado y estado de bloqueo. */
export const useBilling = (organizationId: string) => {
  const { apiClient } = useApiClient();

  const fetchBilling = useCallback(() => {
    if (!organizationId) return Promise.resolve(EMPTY_DATA);
    return Promise.all([
      apiClient(`/billing/current-invoice?organizationId=${organizationId}`, { method: "GET" }),
      apiClient(`/billing/invoices?organizationId=${organizationId}&page=1&limit=${BILLING_SUMMARY_INVOICE_FETCH_LIMIT}`, {
        method: "GET",
      }),
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

  const { data, loading, error, refetch } = useAsyncResource<BillingSummary>(fetchBilling, EMPTY_DATA, [organizationId]);

  return { ...data, loading, error, refetch };
};
