import { useEffect, useState, useCallback } from "react";
import { useApiClient } from "@/hooks/use-api-client";
import type { PortfolioDebtor, PortfolioDebtorsResponse } from "@/types/companies/portfolio-debtor-types";

export type DebtorSortKey = "fullName" | "documentNumber";

export const usePortfolioDebtors = (portfolioId: string) => {
  const { apiClient } = useApiClient();
  const [debtors, setDebtors] = useState<PortfolioDebtor[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState("");
  const [pageSize, setPageSize] = useState(20);
  const [sortKey, setSortKey] = useState<DebtorSortKey>("fullName");
  const [sortOrder, setSortOrder] = useState<"asc" | "desc">("asc");
  const [loading, setLoading] = useState(false);

  const fetchPage = useCallback((p: number) => {
    if (!portfolioId) return;
    setLoading(true);
    const params = new URLSearchParams({
      portfolioId,
      page: String(p),
      pageSize: String(pageSize),
    });
    if (search) params.set("q", search);
    params.set("sort", sortKey);
    params.set("sort_order", sortOrder);
    apiClient(`/debtors/?${params}`)
      .then((data: PortfolioDebtorsResponse) => {
        setDebtors(data.items ?? []);
        setTotal(data.total ?? 0);
      })
      .catch(() => {
        setDebtors([]);
        setTotal(0);
      })
      .finally(() => setLoading(false));
  }, [portfolioId, apiClient, search, pageSize, sortKey, sortOrder]);

  useEffect(() => {
    setPage(1);
    fetchPage(1);
  }, [fetchPage]);

  const goToPage = (p: number) => {
    setPage(p);
    fetchPage(p);
  };

  const handleSort = (key: DebtorSortKey) => {
    if (key === sortKey) {
      setSortOrder((prev) => (prev === "asc" ? "desc" : "asc"));
    } else {
      setSortKey(key);
      setSortOrder("asc");
    }
  };

  const pages = Math.max(1, Math.ceil(total / pageSize));

  return { debtors, total, page, pages, search, setSearch, pageSize, setPageSize, sortKey, sortOrder, handleSort, loading, goToPage };
};
