import { useCallback, useEffect, useState } from "react";
import { useApiClient } from "@/hooks/use-api-client";
import type { AdminInvoice, AdminListInvoicesResponse } from "@/types/billing/billing-types";

export const useAdminInvoices = () => {
  const { apiClient } = useApiClient();
  const [invoices, setInvoices] = useState<AdminInvoice[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);

  const fetchInvoices = useCallback(
    (page = 1, limit = 20) => {
      setLoading(true);
      apiClient(`/billing/admin/invoices?page=${page}&limit=${limit}`, { method: "GET" })
        .then((data: AdminListInvoicesResponse) => {
          setInvoices(data?.invoices ?? []);
          setTotal(data?.total ?? 0);
        })
        .catch(() => {})
        .finally(() => setLoading(false));
    },
    [apiClient],
  );

  useEffect(() => {
    fetchInvoices();
  }, [fetchInvoices]);

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

  return { invoices, total, loading, fetchPage: fetchInvoices, getInvoice };
};
