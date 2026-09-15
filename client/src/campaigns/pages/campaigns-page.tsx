import { useState } from "react";
import { useNavigate, useSearchParams } from "react-router";
import { CalendarDays, List, Plus, Send } from "lucide-react";
import { PageMeta } from "@/ui/pages/page-meta";
import { ModuleBase } from "@/ui/components/common/module-base";
import { ConfirmModal } from "@/ui/components/modal/confirm-modal";
import { Button } from "@/ui/components/button/button";
import { getSession } from "@/auth/utils/auth-session-utils";
import { useDeleteWithConfirm } from "@/hooks/use-delete-with-confirm";
import { useCampaigns } from "../hooks/use-campaigns";
import { useChannels } from "../hooks/use-channels";
import { CampaignsTable } from "../components/campaigns-table";
import { CampaignsCalendar } from "../components/campaigns-calendar";
import { useOrgModule } from "@/companies/hooks/use-org-module";
import { useBreadcrumb } from "@/companies/hooks/use-breadcrumb";
import { usePortfolios } from "@/companies/hooks/use-portfolios";
import type { Campaign } from "@/types/campaigns/campaign-types";

type CampaignsView = "table" | "calendar";

export const CampaignsPage: React.FC = () => {
  const [searchParams] = useSearchParams();
  const portfolioId = searchParams.get("portfolio") ?? "";
  const { orgId, buildOrgPath } = useOrgModule();
  const { build } = useBreadcrumb();
  const navigate = useNavigate();

  const { portfolios } = usePortfolios(orgId);
  const portfolioName = portfolios.find((p) => p.id === portfolioId)?.name ?? "Portafolio";

  const {
    items, total, page, pages, loading, saving,
    search, setSearch,
    pageSize, setPageSize,
    sortKey, sortOrder, handleSort,
    remove, activate, pause, goToPage,
  } = useCampaigns(portfolioId);
  const { channels } = useChannels();

  const user = getSession();
  const isAdmin = user?.scope === "GLOBAL" || user?.orgs?.[orgId]?.role === "ADMINISTRADOR";

  const [view, setView] = useState<CampaignsView>("table");

  const handleEdit = (item: Campaign) =>
    navigate(buildOrgPath(`/my-companies/campaigns/${item.id}/edit`, { portfolio: portfolioId }));

  const handleMonitor = (item: Campaign) =>
    navigate(buildOrgPath(`/my-companies/campaigns/${item.id}/monitor`, { portfolio: portfolioId }));

  const handleResults = (item: Campaign) =>
    navigate(buildOrgPath(`/my-companies/campaigns/${item.id}/results`, { portfolio: portfolioId }));

  const { deleting, setDeleting, confirmDelete, deletingInProgress } = useDeleteWithConfirm<Campaign>(remove);

  const [activating, setActivating] = useState<Campaign | null>(null);
  const [activatingInProgress, setActivatingInProgress] = useState(false);
  const confirmActivate = async () => {
    if (!activating) return;
    setActivatingInProgress(true);
    try {
      await activate(activating.id);
      setActivating(null);
    } finally {
      setActivatingInProgress(false);
    }
  };

  return (
    <>
      <PageMeta title="Campañas" description="Gestión de campañas de SMS y correo automáticas" />
      <ModuleBase
        pageTitle="Campañas"
        pageIcon={Send}
        breadcrumbItems={build({
          portfolio: { id: portfolioId, name: portfolioName },
          communications: true,
        })}
      >
        <div className="flex flex-1 min-h-0 flex-col gap-5">
          <div className="flex flex-wrap items-center justify-between gap-3">
            <div className="inline-flex rounded-lg border border-gray-200 bg-gray-50 p-1 dark:border-gray-800 dark:bg-white/5">
              <button
                type="button"
                onClick={() => setView("table")}
                className={`inline-flex items-center gap-1.5 rounded-md px-3 py-1.5 text-sm font-medium ${
                  view === "table"
                    ? "bg-white text-gray-800 shadow-theme-xs dark:bg-gray-800 dark:text-white/90"
                    : "text-gray-500 hover:text-gray-700 dark:text-gray-400"
                }`}
              >
                <List size={16} />
                Tabla
              </button>
              <button
                type="button"
                onClick={() => setView("calendar")}
                className={`inline-flex items-center gap-1.5 rounded-md px-3 py-1.5 text-sm font-medium ${
                  view === "calendar"
                    ? "bg-white text-gray-800 shadow-theme-xs dark:bg-gray-800 dark:text-white/90"
                    : "text-gray-500 hover:text-gray-700 dark:text-gray-400"
                }`}
              >
                <CalendarDays size={16} />
                Calendario
              </button>
            </div>

            {isAdmin && (
              <Button
                type="button"
                size="sm"
                startIcon={<Plus size={16} />}
                onClick={() => navigate(buildOrgPath("/my-companies/campaigns/new", { portfolio: portfolioId }))}
              >
                Nueva campaña
              </Button>
            )}
          </div>

          {view === "table" ? (
            <CampaignsTable
              items={items}
              channels={channels}
              isAdmin={isAdmin}
              saving={saving}
              loading={loading}
              total={total}
              page={page}
              pages={pages}
              search={search}
              pageSize={pageSize}
              sortKey={sortKey}
              sortOrder={sortOrder}
              onSearch={setSearch}
              onPageSizeChange={setPageSize}
              onSort={handleSort}
              onActivate={(id) => setActivating(items.find((c) => c.id === id) ?? null)}
              onPause={pause}
              onEdit={handleEdit}
              onMonitor={handleMonitor}
              onResults={handleResults}
              onDelete={setDeleting}
              onPageChange={goToPage}
            />
          ) : (
            <CampaignsCalendar organizationId={orgId} isAdmin={isAdmin} />
          )}
        </div>
      </ModuleBase>

      <ConfirmModal
        isOpen={!!deleting}
        onClose={() => setDeleting(null)}
        onConfirm={confirmDelete}
        title="Eliminar campaña"
        message={`¿Seguro que deseas eliminar la campaña "${deleting?.name}"? Esta acción no se puede deshacer.`}
        loading={deletingInProgress}
      />

      <ConfirmModal
        isOpen={!!activating}
        onClose={() => setActivating(null)}
        onConfirm={confirmActivate}
        title="Activar campaña"
        message={`¿Seguro que deseas activar la campaña "${activating?.name}"? Empezará a enviar mensajes reales a los destinatarios según su programación.`}
        confirmLabel="Activar"
        loading={activatingInProgress}
      />
    </>
  );
};
