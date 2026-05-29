import { useEffect, useState } from "react";
import { useApiClient } from "@/hooks/use-api-client";
import type { PortfolioDebtor, PortfolioDebtorsResponse } from "@/types/companies/portfolio-debtor-types";

const PAGE_SIZE = 20;

export const usePortfolioDebtors = (portfolioId: string) => {
  const { apiClient } = useApiClient();
  const [debtors, setDebtors] = useState<PortfolioDebtor[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState("");
  const [loading, setLoading] = useState(false);

  const fetchPage = (p: number, s: string) => {
    if (!portfolioId) return;
    setLoading(true);
    const params = new URLSearchParams({
      portfolioId,
      page: String(p),
      pageSize: String(PAGE_SIZE),
    });
    if (s) params.set("documentNumber", s);
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
  };

  useEffect(() => {
    setPage(1);
    fetchPage(1, search);
  }, [portfolioId, search]);

  const goToPage = (p: number) => {
    setPage(p);
    fetchPage(p, search);
  };

  const pages = Math.max(1, Math.ceil(total / PAGE_SIZE));

  return { debtors, total, page, pages, search, setSearch, loading, goToPage };
};
