import { useState } from "react";
import { useNavigate, useSearchParams } from "react-router";
import { Plus } from "lucide-react";
import { PageMeta } from "@/ui/pages/page-meta";
import { ModuleBase } from "@/ui/components/common/module-base";
import { Loader } from "@/ui/components/loader/loader";
import { ConfirmModal } from "@/ui/components/modal/confirm-modal";
import { getSession } from "@/auth/utils/auth-session-utils";
import { useMyCompanies } from "@/companies/hooks/use-my-companies";
import { usePortfolios } from "@/companies/hooks/use-portfolios";
import { useTemplates } from "@/templates/hooks/use-templates";
import { useTemplateVariables } from "@/templates/hooks/use-template-variables";
import { TemplatesTable } from "@/templates/components/templates-table";
import { TemplatePreviewModal } from "@/templates/components/template-preview-modal";
import { TemplateSendModal } from "@/templates/components/template-send-modal";
import type { Template } from "@/types/templates/template-types";

export const TemplatesPage: React.FC = () => {
  const [searchParams] = useSearchParams();
  const orgId = searchParams.get("org") ?? "";
  const portfolioId = searchParams.get("portfolio") ?? "";
  const navigate = useNavigate();

  const { orgs } = useMyCompanies();
  const { portfolios } = usePortfolios(orgId);
  const orgName = orgs.find((o) => o.id === orgId)?.name ?? "Empresa";
  const portfolioName = portfolios.find((p) => p.id === portfolioId)?.name ?? "Portafolio";

  const { items, loading, saving, remove, preview, send } = useTemplates(orgId);
  const { variables: variableOptions } = useTemplateVariables(orgId);

  const user = getSession();
  const isAdmin = user?.scope === "GLOBAL" || user?.orgs?.[orgId]?.role === "ADMINISTRADOR";

  const [previewTarget, setPreviewTarget] = useState<Template | null>(null);
  const [sendTarget, setSendTarget] = useState<Template | null>(null);
  const [deleting, setDeleting] = useState<Template | null>(null);

  const handleSend = async (id: string, to: string, subject: string, sub: Record<string, string>) => {
    await send(id, { to, subject: subject || null, sub });
  };

  const confirmDelete = async () => {
    if (!deleting) return;
    await remove(deleting.id);
    setDeleting(null);
  };

  return (
    <>
      <PageMeta title="Plantillas" description="Gestión de plantillas de correo y SMS" />
      <ModuleBase
        pageTitle="Plantillas"
        breadcrumbItems={[
          { label: "Mis Empresas", path: "/my-companies" },
          ...(orgId ? [{ label: orgName, path: `/my-companies?org=${orgId}` }] : []),
          ...(portfolioId
            ? [
                { label: "Mis Portafolios", path: `/my-companies/portfolios?org=${orgId}` },
                { label: portfolioName, path: `/my-companies/portfolios?org=${orgId}&portfolio=${portfolioId}` },
                { label: "Comunicaciones", path: `/my-companies/portfolios/communications?org=${orgId}&portfolio=${portfolioId}` },
              ]
            : []),
        ]}
      >
        {loading ? (
          <div className="py-20"><Loader loaderText="Cargando plantillas..." /></div>
        ) : (
          <div className="flex flex-col gap-5">
            {isAdmin && (
              <div className="flex justify-end">
                <button
                  onClick={() => navigate(`/my-companies/templates/new?org=${orgId}`)}
                  className="inline-flex items-center gap-2 rounded-lg bg-brand-500 px-4 py-2.5 text-sm font-medium text-white shadow-theme-xs hover:bg-brand-600"
                >
                  <Plus size={16} />
                  Nueva plantilla
                </button>
              </div>
            )}

            <TemplatesTable
              items={items}
              isAdmin={isAdmin}
              onPreview={setPreviewTarget}
              onSend={setSendTarget}
              onEdit={(item) => navigate(`/my-companies/templates/${item.id}/edit?org=${orgId}`)}
              onDelete={setDeleting}
            />
          </div>
        )}
      </ModuleBase>

      <TemplatePreviewModal
        isOpen={!!previewTarget}
        template={previewTarget}
        variableOptions={variableOptions}
        onClose={() => setPreviewTarget(null)}
        onPreview={preview}
      />

      <TemplateSendModal
        isOpen={!!sendTarget}
        template={sendTarget}
        saving={saving}
        onClose={() => setSendTarget(null)}
        onSend={handleSend}
      />

      <ConfirmModal
        isOpen={!!deleting}
        onClose={() => setDeleting(null)}
        onConfirm={confirmDelete}
        title="Eliminar plantilla"
        message={`¿Seguro que deseas eliminar la plantilla "${deleting?.name}"? Esta acción no se puede deshacer.`}
        loading={saving}
      />
    </>
  );
};
