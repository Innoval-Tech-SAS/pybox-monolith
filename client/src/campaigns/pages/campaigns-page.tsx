import { useState } from "react";
import { useNavigate, useSearchParams } from "react-router";
import { Plus } from "lucide-react";
import { PageMeta } from "@/ui/pages/page-meta";
import { ModuleBase } from "@/ui/components/common/module-base";
import { Loader } from "@/ui/components/loader/loader";
import { ConfirmModal } from "@/ui/components/modal/confirm-modal";
import { getSession } from "@/auth/utils/auth-session-utils";
import { useCampaigns } from "../hooks/use-campaigns";
import { useChannels } from "../hooks/use-channels";
import { CampaignsTable } from "../components/campaigns-table";
import { useOrgModule } from "@/companies/hooks/use-org-module";
import { usePortfolios } from "@/companies/hooks/use-portfolios";
import type { Campaign } from "@/types/campaigns/campaign-types";

export const CampaignsPage: React.FC = () => {
  const [searchParams] = useSearchParams();
  const portfolioId = searchParams.get("portfolio") ?? "";
  const { orgId, orgName, buildOrgPath } = useOrgModule();
  const navigate = useNavigate();

  const { portfolios } = usePortfolios(orgId);
  const portfolioName = portfolios.find((p) => p.id === portfolioId)?.name ?? "Portafolio";

  const { items, total, page, pages, loading, saving, remove, activate, pause, goToPage } = useCampaigns(orgId);
  const { channels } = useChannels();

  const user = getSession();
  const isAdmin = user?.scope === "GLOBAL" || user?.orgs?.[orgId]?.role === "ADMINISTRADOR";

  const handleEdit = (item: Campaign) =>
    navigate(buildOrgPath(`/my-companies/campaigns/${item.id}/edit`, { portfolio: portfolioId }));

  const [deleting, setDeleting] = useState<Campaign | null>(null);

  const confirmDelete = async () => {
    if (!deleting) return;
    await remove(deleting.id);
    setDeleting(null);
  };

  return (
    <>
      <PageMeta title="Campañas" description="Gestión de campañas de SMS y correo automáticas" />
      <ModuleBase
        pageTitle="Campañas"
        breadcrumbItems={[
          { label: "Mis Empresas", path: "/my-companies" },
          { label: orgName || "Empresa", path: buildOrgPath("/my-companies") },
          ...(portfolioId
            ? [
                { label: "Mis Portafolios", path: buildOrgPath("/my-companies/portfolios") },
                { label: portfolioName, path: buildOrgPath("/my-companies/portfolios", { portfolio: portfolioId }) },
                { label: "Comunicaciones", path: buildOrgPath("/my-companies/portfolios/communications", { portfolio: portfolioId }) },
              ]
            : []),
        ]}
      >
        {loading ? (
          <div className="py-20"><Loader loaderText="Cargando campañas..." /></div>
        ) : (
          <div className="flex flex-1 min-h-0 flex-col gap-5">
            {isAdmin && (
              <div className="flex justify-end">
                <button
                  onClick={() => navigate(buildOrgPath("/my-companies/campaigns/new", { portfolio: portfolioId }))}
                  className="inline-flex items-center gap-2 rounded-lg bg-brand-500 px-4 py-2.5 text-sm font-medium text-white shadow-theme-xs hover:bg-brand-600"
                >
                  <Plus size={16} />
                  Nueva campaña
                </button>
              </div>
            )}

            <CampaignsTable
              items={items}
              channels={channels}
              isAdmin={isAdmin}
              saving={saving}
              total={total}
              page={page}
              pages={pages}
              onActivate={activate}
              onPause={pause}
              onEdit={handleEdit}
              onDelete={setDeleting}
              onPageChange={goToPage}
            />
          </div>
        )}
      </ModuleBase>

      <ConfirmModal
        isOpen={!!deleting}
        onClose={() => setDeleting(null)}
        onConfirm={confirmDelete}
        title="Eliminar campaña"
        message={`¿Seguro que deseas eliminar la campaña "${deleting?.name}"? Esta acción no se puede deshacer.`}
        loading={saving}
      />
    </>
  );
};
