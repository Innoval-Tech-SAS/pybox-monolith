import { useEffect, useState } from "react";
import { useApiClient } from "@/hooks/use-api-client";
import type { DebtorProfile, PortfolioDebtor, PortfolioDebtorsResponse } from "@/types/companies/portfolio-debtor-types";

const PAGE_SIZE = 20;

export const usePortfolioDebtors = (portfolioId: string) => {
  const { apiClient } = useApiClient();
  const [debtors, setDebtors] = useState<PortfolioDebtor[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState("");
  const [loading, setLoading] = useState(false);

  const fetch = (p: number, s: string) => {
    if (!portfolioId) return;
    setLoading(true);
    const params = new URLSearchParams({
      portfolioId,
      page: String(p),
      limit: String(PAGE_SIZE),
    });
    if (s) params.set("search", s);
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
    fetch(1, search);
  }, [portfolioId, search]);

  const goToPage = (p: number) => {
    setPage(p);
    fetch(p, search);
  };

  const pages = Math.max(1, Math.ceil(total / PAGE_SIZE));

  return { debtors, total, page, pages, search, setSearch, loading, goToPage };
};

export const useDebtorProfile = (debtorId: number | null) => {
  const { apiClient } = useApiClient();
  const [profile, setProfile] = useState<DebtorProfile | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!debtorId) { setProfile(null); return; }
    setLoading(true);
    apiClient(`/debtors/${debtorId}/profile`)
      .then((data: DebtorProfile) => setProfile(data))
      .catch(() => setProfile(null))
      .finally(() => setLoading(false));
  }, [debtorId]);

  return { profile, loading };
};
