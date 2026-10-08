import { useCallback } from "react";
import { useApiClient } from "@/hooks/use-api-client";
import type { AdminInvoice } from "@/types/billing/billing-types";

/** Consulta puntual de una factura de cualquier organizacion (solo admin global, solo lectura). */
export const useAdminInvoiceActions = () => {
  const { apiClient } = useApiClient();

  const getInvoice = useCallback(
    async (invoiceId: string): Promise<AdminInvoice | null> => {
      try {
        return await apiClient(`/billing/admin/invoices/${invoiceId}`, { method: "GET" });
      } catch {
        return null;
      }
    },
    [apiClient],
  );

  return { getInvoice };
};
