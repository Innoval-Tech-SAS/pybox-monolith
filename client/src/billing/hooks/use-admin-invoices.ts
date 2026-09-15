import { useCallback, useEffect, useState } from "react";
import { useApiClient } from "@/hooks/use-api-client";
import type { AdminListInvoicesResponse, AdminInvoice } from "@/types/billing/billing-types";
import { ADMIN_INVOICE_LIST_PAGE_SIZE } from "../constants/pagination";

/** Listado de facturas de todas las organizaciones (solo admin global). */
export const useAdminInvoices = () => {
  const { apiClient } = useApiClient();
  const [invoices, setInvoices] = useState<AdminInvoice[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);

  const fetchInvoices = useCallback(
    (page = 1, limit = ADMIN_INVOICE_LIST_PAGE_SIZE) => {
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

  return { invoices, total, loading, fetchPage: fetchInvoices };
};
