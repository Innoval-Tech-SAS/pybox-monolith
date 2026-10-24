import { useEffect, useState } from "react";
import { useApiClient } from "@/hooks/use-api-client";
import type {
  BillingSummary,
  InvoiceStatusBreakdown,
  MonthlyRevenue,
  RevenueByChannel,
  RevenueByProvider,
} from "@/types/dashboard/billing-dashboard-types";

/** Facturación agregada de toda la plataforma (todas las organizaciones), para el Home de admin global. */
export const useGlobalBillingDashboard = () => {
  const { apiClient } = useApiClient();

  const [summary, setSummary] = useState<BillingSummary | null>(null);
  const [statusBreakdown, setStatusBreakdown] = useState<InvoiceStatusBreakdown | null>(null);
  const [revenueByChannel, setRevenueByChannel] = useState<RevenueByChannel | null>(null);
  const [revenueByProvider, setRevenueByProvider] = useState<RevenueByProvider | null>(null);
  const [monthlyRevenue, setMonthlyRevenue] = useState<MonthlyRevenue | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;

    const load = async () => {
      setLoading(true);
      try {
        const [summaryResult, statusResult, channelResult, providerResult, monthlyResult] = await Promise.all([
          apiClient<BillingSummary>("/billing/admin/dashboard/summary", { method: "GET" }),
          apiClient<InvoiceStatusBreakdown>("/billing/admin/dashboard/invoices-by-status", { method: "GET" }),
          apiClient<RevenueByChannel>("/billing/admin/dashboard/revenue-by-channel", { method: "GET" }),
          apiClient<RevenueByProvider>("/billing/admin/dashboard/revenue-by-provider", { method: "GET" }),
          apiClient<MonthlyRevenue>("/billing/admin/dashboard/monthly-revenue", { method: "GET" }),
        ]);
        if (cancelled) return;
        setSummary(summaryResult);
        setStatusBreakdown(statusResult ?? null);
        setRevenueByChannel(channelResult ?? null);
        setRevenueByProvider(providerResult ?? null);
        setMonthlyRevenue(monthlyResult ?? null);
      } catch {
        if (!cancelled) {
          setSummary(null);
          setStatusBreakdown(null);
          setRevenueByChannel(null);
          setRevenueByProvider(null);
          setMonthlyRevenue(null);
        }
      } finally {
        if (!cancelled) setLoading(false);
      }
    };

    load();
    return () => {
      cancelled = true;
    };
  }, [apiClient]);

  return { summary, statusBreakdown, revenueByChannel, revenueByProvider, monthlyRevenue, loading };
};
