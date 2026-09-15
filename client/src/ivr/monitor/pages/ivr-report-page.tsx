import { useEffect, useState } from "react";
import { useParams, useSearchParams } from "react-router";
import { BarChart3, Download } from "lucide-react";
import { PageMeta } from "@/ui/pages/page-meta";
import { ModuleBase } from "@/ui/components/common/module-base";
import { Button } from "@/ui/components/button/button";
import { Loader } from "@/ui/components/loader/loader";
import { useApiClient } from "@/hooks/use-api-client";
import { useOrgModule } from "@/companies/hooks/use-org-module";
import { useBreadcrumb } from "@/companies/hooks/use-breadcrumb";
import { usePortfolios } from "@/companies/hooks/use-portfolios";
import { useIvrReport } from "../hooks/use-ivr-report";
import { OutcomeDistribution } from "../components/outcome-distribution";
import { CallFunnel } from "../components/call-funnel";
import { BreakdownCard } from "../components/breakdown-card";
import { AMD_LABELS } from "../constants/call-status-labels";
import type { Campaign } from "@/types/campaigns/campaign-types";

const formatSeconds = (seconds: number): string => {
  if (!seconds) return "0s";
  const mins = Math.floor(seconds / 60);
  const secs = seconds % 60;
  return mins > 0 ? `${mins}m ${secs}s` : `${secs}s`;
};

export const IvrReportPage: React.FC = () => {
  const { id: campaignId = "" } = useParams();
  const [searchParams] = useSearchParams();
  const portfolioId = searchParams.get("portfolio") ?? "";
  const { orgId } = useOrgModule();
  const { build } = useBreadcrumb();
  const { apiClient } = useApiClient();

  const { portfolios } = usePortfolios(orgId);
  const portfolioName = portfolios.find((p) => p.id === portfolioId)?.name ?? "Portafolio";

  const [campaignName, setCampaignName] = useState("");
  const { report, loading, exporting, exportCsv } = useIvrReport(campaignId);

  useEffect(() => {
    if (!campaignId || !portfolioId) return;
    apiClient(`/campaigns/${campaignId}?portfolioId=${portfolioId}`, { method: "GET" })
      .then((campaign: Campaign) => setCampaignName(campaign?.name ?? ""))
      .catch(() => setCampaignName(""));
  }, [apiClient, campaignId, portfolioId]);

  return (
    <>
      <PageMeta
        title="Resultados de la campaña"
        description="Distribución de resultados de una campaña de llamadas IVR"
      />
      <ModuleBase
        pageTitle={campaignName ? `Resultados · ${campaignName}` : "Resultados de la campaña"}
        pageIcon={BarChart3}
        breadcrumbItems={build({
          portfolio: { id: portfolioId, name: portfolioName },
          communications: true,
        })}
      >
        {loading ? (
          <Loader loaderText="Cargando resultados..." />
        ) : !report ? (
          <p className="text-sm text-gray-500 dark:text-gray-400">
            No se pudo cargar el reporte de esta campaña.
          </p>
        ) : (
          <div className="flex flex-col gap-5">
            <div className="flex flex-wrap items-center justify-between gap-3">
              <div className="flex flex-wrap gap-6">
                <div>
                  <p className="text-xs text-gray-500 dark:text-gray-400">Llamadas</p>
                  <p className="text-xl font-semibold text-gray-800 dark:text-white/90">
                    {report.totalCalls}
                  </p>
                </div>
                <div>
                  <p className="text-xs text-gray-500 dark:text-gray-400">Duración total</p>
                  <p className="text-xl font-semibold text-gray-800 dark:text-white/90">
                    {formatSeconds(report.duration.totalSeconds)}
                  </p>
                </div>
                <div>
                  <p className="text-xs text-gray-500 dark:text-gray-400">Promedio</p>
                  <p className="text-xl font-semibold text-gray-800 dark:text-white/90">
                    {formatSeconds(report.duration.averageSeconds)}
                  </p>
                </div>
              </div>
              <Button
                size="sm"
                variant="outline"
                startIcon={<Download size={15} />}
                onClick={() => exportCsv(`llamadas_${campaignName || campaignId}`)}
                disabled={exporting || report.totalCalls === 0}
              >
                {exporting ? "Exportando..." : "Exportar CSV"}
              </Button>
            </div>

            <div className="grid grid-cols-1 gap-5 lg:grid-cols-2">
              <OutcomeDistribution
                outcomes={report.outcomes}
                typifiedCalls={report.typifiedCalls}
                totalCalls={report.totalCalls}
              />
              <CallFunnel funnel={report.funnel} />
            </div>

            <div className="grid grid-cols-1 gap-5 lg:grid-cols-3">
              <BreakdownCard
                title="Detección AMD"
                rows={report.byAmd}
                formatValue={(value) =>
                  value ? (AMD_LABELS[value] ?? value) : "Sin detección"
                }
              />
              <BreakdownCard
                title="Nodo final del flujo"
                rows={report.byEndNode}
                formatValue={(value) => value ?? "No entró al flujo"}
              />
              <BreakdownCard
                title="Intento de marcación"
                rows={report.byAttempt}
                formatValue={(value) => (value ? `Intento ${value}` : "—")}
              />
            </div>
          </div>
        )}
      </ModuleBase>
    </>
  );
};
