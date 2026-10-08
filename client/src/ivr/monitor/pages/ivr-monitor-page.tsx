import { useEffect, useState } from "react";
import { useParams, useSearchParams } from "react-router";
import { Activity } from "lucide-react";
import { PageMeta } from "@/ui/pages/page-meta";
import { ModuleBase } from "@/ui/components/common/module-base";
import { useOrgModule } from "@/companies/hooks/use-org-module";
import { useBreadcrumb } from "@/companies/hooks/use-breadcrumb";
import { usePortfolios } from "@/companies/hooks/use-portfolios";
import { useCallMonitor, type CallEntry } from "../hooks/use-call-monitor";
import { useIvrExecution } from "../hooks/use-ivr-execution";
import { useCampaignName } from "../hooks/use-campaign-name";
import { CallStatsCards } from "../components/call-stats-cards";
import { ActiveCallsTable } from "../components/active-calls-table";
import { CallDetailModal } from "../components/call-detail-modal";
import { ConnectionIndicator } from "../components/connection-indicator";
import { CampaignControlBar } from "../components/campaign-control-bar";

/**
 * Monitor en vivo de una campaña IVR. Carga el estado con
 * `/ivr/monitor/snapshot` y lo mantiene al día por SSE (`/ivr/monitor/stream`),
 * que a su vez se alimenta de los webhooks de Helena.
 */
export const IvrMonitorPage: React.FC = () => {
  const { id: campaignId = "" } = useParams();
  const [searchParams] = useSearchParams();
  const portfolioId = searchParams.get("portfolio") ?? "";
  const { orgId } = useOrgModule();
  const { build } = useBreadcrumb();

  const { portfolios } = usePortfolios(orgId);
  const portfolioName = portfolios.find((p) => p.id === portfolioId)?.name ?? "Portafolio";
  const campaignName = useCampaignName(campaignId, portfolioId);

  const [selected, setSelected] = useState<CallEntry | null>(null);

  const { calls, stats, campaignStatus, loading, connected, error, tick, refresh } =
    useCallMonitor(campaignId);
  const execution = useIvrExecution(campaignId);

  // El estado del bulk puede cambiar por fuera de esta pestaña (otro usuario,
  // o la consola de Helena); el stream ya lo refleja en `campaignStatus`, así
  // que se aprovecha para refrescar la fila de control sin pedirlo aparte.
  useEffect(() => {
    if (campaignStatus) execution.refresh();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [campaignStatus]);

  return (
    <>
      <PageMeta
        title="Monitor de llamadas"
        description="Seguimiento en tiempo real de una campaña de llamadas IVR"
      />
      <ModuleBase
        pageTitle={campaignName ? `Monitor · ${campaignName}` : "Monitor de llamadas"}
        pageIcon={Activity}
        breadcrumbItems={build({
          portfolio: { id: portfolioId, name: portfolioName },
          communications: true,
        })}
      >
        <div className="flex flex-1 min-h-0 flex-col gap-5">
          <div className="flex flex-wrap items-center justify-between gap-3">
            <h2 className="text-base font-semibold text-gray-800 dark:text-white/90">
              Llamadas en vivo
            </h2>
            <ConnectionIndicator connected={connected} onRefresh={refresh} />
          </div>

          <CampaignControlBar
            execution={execution.execution}
            loading={execution.loading}
            acting={execution.acting}
            onPause={execution.pause}
            onResume={execution.resume}
            onCancel={execution.cancel}
          />

          {error && (
            <div className="rounded-lg border border-error-200 bg-error-50 px-4 py-3 text-sm text-error-600 dark:border-error-500/30 dark:bg-error-500/10 dark:text-error-400">
              {error}
            </div>
          )}

          <CallStatsCards stats={stats} />

          <ActiveCallsTable
            calls={calls}
            loading={loading}
            tick={tick}
            onSelect={setSelected}
          />
        </div>
      </ModuleBase>

      <CallDetailModal call={selected} onClose={() => setSelected(null)} />
    </>
  );
};
