import { Building2, Receipt, TrendingDown } from "lucide-react";
import { Card, CardTitle } from "@/ui/components/card";
import { Loader } from "@/ui/components/loader/loader";
import EmptyState from "@/ui/components/common/empty-state";
import { RadialGaugeChart } from "@/ui/components/charts/radial-gauge-chart";
import { DonutChart } from "@/ui/components/charts/donut-chart";
import { MonthlyBarChart } from "@/ui/components/charts/monthly-bar-chart";
import { StatCard } from "@/ui/components/charts/stat-card";
import { DollarLineIcon } from "@/ui/icons";
import { CHART_DONUT_COLORS } from "@/ui/constants/chart-colors";
import { formatUsd } from "@/billing/utils/format-currency";
import { INVOICE_STATUS_CHART_COLORS, INVOICE_STATUS_LABELS } from "@/billing/constants/invoice-status-labels";
import { PAYMENT_PROVIDER_LABELS } from "@/billing/constants/payment-provider-labels";
import type { InvoiceStatus, PaymentProviderName } from "@/types/billing/billing-types";
import { formatMonthlyPeriod } from "../utils/dashboard-format-utils";
import { useGlobalBillingDashboard } from "../hooks/use-global-billing-dashboard";

export const GlobalBillingDashboardCharts: React.FC = () => {
  const { summary, statusBreakdown, revenueByChannel, revenueByProvider, monthlyRevenue, loading } =
    useGlobalBillingDashboard();

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <Loader />
      </div>
    );
  }

  if (!summary) return null;

  const statusItems = statusBreakdown?.items ?? [];
  const statusSeries = statusItems.map((i) => Number(i.totalAmount));
  const statusLabels = statusItems.map((i) => INVOICE_STATUS_LABELS[i.status as InvoiceStatus] ?? i.status);
  const statusColors = statusItems.map((i) => INVOICE_STATUS_CHART_COLORS[i.status as InvoiceStatus] ?? "#98a2b3");

  const channelItems = revenueByChannel?.items ?? [];
  const providerItems = revenueByProvider?.items ?? [];
  const monthlyPoints = monthlyRevenue?.points ?? [];

  return (
    <div className="flex flex-col gap-4">
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
        <StatCard
          icon={<DollarLineIcon className="size-5" />}
          label="Facturación del mes (USD)"
          value={formatUsd(summary.currentMonthRevenue)}
          accent
        />
        <StatCard
          icon={<TrendingDown className="size-5" />}
          label="Cartera vencida (USD)"
          value={formatUsd(summary.overdueAmount)}
        />
        <StatCard
          icon={<Building2 className="size-5" />}
          label="Organizaciones facturadas"
          value={summary.billedOrganizationsCount}
        />
      </div>

      <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
        <Card>
          <CardTitle>Tasa de cobro del mes</CardTitle>
          <RadialGaugeChart value={summary.collectionRate} label="Tasa de cobro" />
          <p className="text-center text-sm text-gray-500 dark:text-gray-400">
            % del monto facturado en el periodo actual que ya está pagado
          </p>
        </Card>

        <Card>
          <CardTitle>Facturas del mes por estado</CardTitle>
          {statusSeries.length > 0 ? (
            <DonutChart series={statusSeries} labels={statusLabels} colors={statusColors} />
          ) : (
            <EmptyState icon={Receipt} title="Sin facturas en el periodo actual" className="py-12" />
          )}
        </Card>
      </div>

      <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
        <Card>
          <CardTitle>Ingreso por canal (USD, últimos 12 meses)</CardTitle>
          {channelItems.length > 0 ? (
            <DonutChart
              series={channelItems.map((i) => Number(i.totalAmount))}
              labels={channelItems.map((i) => i.channelName)}
              colors={CHART_DONUT_COLORS}
            />
          ) : (
            <EmptyState icon={Receipt} title="Sin consumo facturado" className="py-12" />
          )}
        </Card>

        <Card>
          <CardTitle>Ingreso por pasarela (USD, últimos 12 meses)</CardTitle>
          {providerItems.length > 0 ? (
            <DonutChart
              series={providerItems.map((i) => Number(i.totalAmount))}
              labels={providerItems.map(
                (i) => PAYMENT_PROVIDER_LABELS[i.provider as PaymentProviderName] ?? i.provider,
              )}
              colors={CHART_DONUT_COLORS}
            />
          ) : (
            <EmptyState icon={Receipt} title="Sin pagos cobrados" className="py-12" />
          )}
        </Card>
      </div>

      <Card>
        <CardTitle>Facturación mensual global (USD)</CardTitle>
        {monthlyPoints.length > 0 ? (
          <MonthlyBarChart
            categories={monthlyPoints.map((p) => formatMonthlyPeriod(p.period))}
            data={monthlyPoints.map((p) => Number(p.totalAmount))}
            seriesName="Facturación"
            height={320}
            tooltipFormatter={(val) => formatUsd(val)}
          />
        ) : (
          <EmptyState icon={Receipt} title="Sin facturación registrada" className="py-12" />
        )}
      </Card>
    </div>
  );
};
