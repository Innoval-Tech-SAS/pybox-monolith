import { useNavigate } from "react-router";
import { Plus } from "lucide-react";
import { PageMeta } from "@/ui/pages/page-meta";
import { ModuleBase } from "@/ui/components/common/module-base";
import { Loader } from "@/ui/components/loader/loader";
import { getSession } from "@/auth/utils/auth-session-utils";
import { useCampaigns } from "../hooks/use-campaigns";
import { useChannels } from "../hooks/use-channels";
import { CampaignsTable } from "../components/campaigns-table";
import { useOrgModule } from "@/companies/hooks/use-org-module";
import type { Campaign } from "@/types/campaigns/campaign-types";

export const CampaignsPage: React.FC = () => {
  const { orgId, buildOrgPath } = useOrgModule();
  const navigate = useNavigate();

  const { items, loading, saving, remove, activate, pause } = useCampaigns(orgId);
  const { channels } = useChannels();

  const user = getSession();
  const isAdmin = user?.scope === "GLOBAL" || user?.orgs?.[orgId]?.role === "ADMINISTRADOR";

  const handleEdit = (item: Campaign) => navigate(buildOrgPath(`/my-companies/campaigns/${item.id}/edit`));

  return (
    <>
      <PageMeta title="Campañas" description="Gestión de campañas de SMS y correo automáticas" />
      <ModuleBase
        pageTitle="Campañas"
        breadcrumbItems={[
          { label: "Mis Empresas", path: "/my-companies" },
          ...(orgId ? [{ label: "Empresa", path: buildOrgPath("/my-companies") }] : []),
        ]}
      >
        {loading ? (
          <div className="py-20"><Loader loaderText="Cargando campañas..." /></div>
        ) : (
          <div className="flex flex-col gap-5">
            {isAdmin && (
              <div className="flex justify-end">
                <button
                  onClick={() => navigate(buildOrgPath("/my-companies/campaigns/new"))}
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
              onActivate={activate}
              onPause={pause}
              onEdit={handleEdit}
              onDelete={remove}
            />
          </div>
        )}
      </ModuleBase>
    </>
  );
};
