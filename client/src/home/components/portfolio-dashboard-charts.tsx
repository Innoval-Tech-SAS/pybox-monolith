import { CreditCard, FileText, KeyRound, Megaphone, Send, TrendingDown } from "lucide-react";
import { Card, CardTitle } from "@/ui/components/card";
import { Loader } from "@/ui/components/loader/loader";
import EmptyState from "@/ui/components/common/empty-state";
import { RadialGaugeChart } from "@/ui/components/charts/radial-gauge-chart";
import { DonutChart } from "@/ui/components/charts/donut-chart";
import { MonthlyBarChart } from "@/ui/components/charts/monthly-bar-chart";
import { StatCard } from "@/ui/components/charts/stat-card";
import { DollarLineIcon, GroupIcon, UserCircleIcon } from "@/ui/icons";
import { CHART_DONUT_COLORS } from "@/ui/constants/chart-colors";
import type { PortfolioDashboardChartsProps } from "@/types/props/portfolio-dashboard-charts-props";
import { formatMonthlyPeriod } from "../utils/dashboard-format-utils";
import { usePortfolioDashboard } from "../hooks/use-portfolio-dashboard";
import { CONTACT_STATUS_COLORS, CONTACT_STATUS_LABELS } from "../constants/contact-status-display";

export const PortfolioDashboardCharts: React.FC<PortfolioDashboardChartsProps> = ({ portfolioId }) => {
  const {
    stats,
    statusCounts,
    campaigns,
    selectedCampaignId,
    setSelectedCampaignId,
    monthlySends,
    loading,
    loadingMonthlySends,
  } = usePortfolioDashboard(portfolioId);

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <Loader />
      </div>
    );
  }

  if (!stats) return null;

  const debtorsLoadedPercentage = stats.clientesUnicos > 0 ? Math.round((stats.titulares / stats.clientesUnicos) * 100) : 0;

  const statusItems = statusCounts?.items ?? [];
  const statusSeries = statusItems.map((i) => i.count);
  const statusLabels = statusItems.map((i) => CONTACT_STATUS_LABELS[i.status] ?? i.status);
  const statusColors = statusItems.map((i) => CONTACT_STATUS_COLORS[i.status] ?? "#98a2b3");

  return (
    <div className="flex flex-col gap-4">
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <StatCard icon={<UserCircleIcon className="size-5" />} label="Titulares" value={stats.titulares} accent />
        <StatCard icon={<GroupIcon className="size-5" />} label="Codeudores" value={stats.codeudores} />
        <StatCard icon={<DollarLineIcon className="size-5" />} label="Créditos cargados" value={stats.creditosCargados} />
        <StatCard icon={<FileText className="size-5" />} label="Documentos únicos" value={stats.documentosUnicos} />
        <StatCard icon={<KeyRound className="size-5" />} label="Usuarios con acceso" value={stats.usuariosConAcceso} />
        <StatCard
          icon={<TrendingDown className="size-5" />}
          label="Total en mora"
          value={stats.totalMora.toLocaleString("es-CO", { maximumFractionDigits: 0 })}
        />
      </div>

      <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
        <Card>
          <CardTitle>% Cédulas cargadas</CardTitle>
          <RadialGaugeChart value={debtorsLoadedPercentage} label="Cédulas cargadas" />
          <p className="text-center text-sm text-gray-500 dark:text-gray-400">
            {stats.titulares} titulares sobre {stats.clientesUnicos} deudores totales
          </p>
        </Card>

        <Card>
          <CardTitle>Titulares y codeudores</CardTitle>
          {stats.titulares + stats.codeudores > 0 ? (
            <DonutChart
              series={[stats.titulares, stats.codeudores]}
              labels={["Titulares", "Codeudores"]}
              colors={CHART_DONUT_COLORS}
            />
          ) : (
            <EmptyState icon={CreditCard} title="Sin créditos cargados en este portafolio" className="py-12" />
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
          <EmptyState icon={Megaphone} title="Sin campañas en este portafolio" className="py-12" />
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
