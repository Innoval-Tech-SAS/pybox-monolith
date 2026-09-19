import { FolderOpen, Megaphone, Send, TrendingDown } from "lucide-react";
import { Card, CardTitle } from "@/ui/components/card";
import { Loader } from "@/ui/components/loader/loader";
import EmptyState from "@/ui/components/common/empty-state";
import { RadialGaugeChart } from "@/ui/components/charts/radial-gauge-chart";
import { DonutChart } from "@/ui/components/charts/donut-chart";
import { MonthlyBarChart } from "@/ui/components/charts/monthly-bar-chart";
import { StatCard } from "@/ui/components/charts/stat-card";
import { DollarLineIcon, FolderIcon, GroupIcon } from "@/ui/icons";
import { CHART_DONUT_COLORS } from "@/ui/constants/chart-colors";
import type { OrganizationDashboardChartsProps } from "@/types/props/organization-dashboard-charts-props";
import { formatMonthlyPeriod } from "../utils/dashboard-format-utils";
import { useOrganizationDashboard } from "../hooks/use-organization-dashboard";
import { CONTACT_STATUS_COLORS, CONTACT_STATUS_LABELS } from "../constants/contact-status-display";

export const OrganizationDashboardCharts: React.FC<OrganizationDashboardChartsProps> = ({
  organizationId,
}) => {
  const {
    stats,
    statusCounts,
    campaigns,
    selectedCampaignId,
    setSelectedCampaignId,
    monthlySends,
    loading,
    loadingMonthlySends,
  } = useOrganizationDashboard(organizationId);

  const statusItems = statusCounts?.items ?? [];
  const statusSeries = statusItems.map((i) => i.count);
  const statusLabels = statusItems.map((i) => CONTACT_STATUS_LABELS[i.status] ?? i.status);
  const statusColors = statusItems.map((i) => CONTACT_STATUS_COLORS[i.status] ?? "#98a2b3");

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <Loader />
      </div>
    );
  }

  if (!stats) return null;

  return (
    <div className="flex flex-col gap-4">
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <StatCard
          icon={<GroupIcon className="size-5" />}
          label="Cédulas cargadas"
          value={stats.debtorsCount}
          accent
        />
        <StatCard icon={<FolderIcon className="size-5" />} label="Portafolios" value={stats.portfoliosCount} />
        <StatCard icon={<DollarLineIcon className="size-5" />} label="Créditos" value={stats.creditsCount} />
        <StatCard
          icon={<TrendingDown className="size-5" />}
          label="Total en mora"
          value={stats.totalOverdueAmount.toLocaleString("es-CO", { maximumFractionDigits: 0 })}
        />
      </div>

      <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
        <Card>
          <CardTitle>% Cédulas cargadas</CardTitle>
          <RadialGaugeChart value={stats.debtorsLoadedPercentage} label="Cédulas cargadas" />
          <p className="text-center text-sm text-gray-500 dark:text-gray-400">
            {stats.debtorsCount} titulares sobre {stats.uniqueDebtorsCount} deudores totales
          </p>
        </Card>

        <Card>
          <CardTitle>Portafolios activos</CardTitle>
          {stats.portfoliosCount > 0 ? (
            <DonutChart
              series={[stats.portfoliosActiveCount, stats.portfoliosInactiveCount]}
              labels={["Activos", "Inactivos"]}
              colors={CHART_DONUT_COLORS}
            />
          ) : (
            <EmptyState icon={FolderOpen} title="Sin portafolios cargados" className="py-12" />
          )}
        </Card>
      </div>

      <Card>
        <CardTitle>Estados de envíos</CardTitle>
        {statusSeries.length > 0 ? (
          <DonutChart series={statusSeries} labels={statusLabels} colors={statusColors} />
        ) : (
          <EmptyState icon={Send} title="Sin envíos registrados" className="py-12" />
        )}
      </Card>

      <Card>
        <div className="mb-4 flex items-center justify-between gap-3">
          <CardTitle>Envíos mensuales</CardTitle>
          {campaigns.length > 0 && (
            <select
              value={selectedCampaignId}
              onChange={(e) => setSelectedCampaignId(e.target.value)}
              className="rounded-lg border border-gray-300 bg-white px-2.5 py-1.5 text-xs text-gray-700 dark:border-gray-700 dark:bg-gray-800 dark:text-gray-300"
            >
              {campaigns.map((c) => (
                <option key={c.id} value={c.id}>
                  {c.name}
                </option>
              ))}
            </select>
          )}
        </div>
        {campaigns.length === 0 ? (
          <EmptyState icon={Megaphone} title="Sin campañas en esta organización" className="py-12" />
        ) : loadingMonthlySends || !monthlySends ? (
          <div className="flex items-center justify-center py-12">
            <Loader />
          </div>
        ) : (
          <MonthlyBarChart
            categories={monthlySends.points.map((p) => formatMonthlyPeriod(p.period))}
            data={monthlySends.points.map((p) => p.count)}
            seriesName={monthlySends.campaignName}
            height={320}
          />
        )}
      </Card>
    </div>
  );
};
