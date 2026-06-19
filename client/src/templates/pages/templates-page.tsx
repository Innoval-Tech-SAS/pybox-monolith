import { useState } from "react";
import { useNavigate, useSearchParams } from "react-router";
import { Plus } from "lucide-react";
import { PageMeta } from "@/ui/pages/page-meta";
import { ModuleBase } from "@/ui/components/common/module-base";
import { Loader } from "@/ui/components/loader/loader";
import { ConfirmModal } from "@/ui/components/modal/confirm-modal";
import { getSession } from "@/auth/utils/auth-session-utils";
import { useOrgModule } from "@/companies/hooks/use-org-module";
import { usePortfolios } from "@/companies/hooks/use-portfolios";
import { useTemplates } from "@/templates/hooks/use-templates";
import { useTemplateVariables } from "@/templates/hooks/use-template-variables";
import { TemplatesTable } from "@/templates/components/templates-table";
import { TemplatePreviewModal } from "@/templates/components/template-preview-modal";
import { TemplateSendModal } from "@/templates/components/template-send-modal";
import type { Template } from "@/types/templates/template-types";

export const TemplatesPage: React.FC = () => {
  const [searchParams] = useSearchParams();
  const portfolioId = searchParams.get("portfolio") ?? "";
  const navigate = useNavigate();
  const { orgId, orgName, buildOrgPath } = useOrgModule();

  const { portfolios } = usePortfolios(orgId);
  const portfolioName = portfolios.find((p) => p.id === portfolioId)?.name ?? "Portafolio";

  const { items, total, page, pages, loading, saving, remove, preview, send, goToPage } = useTemplates(orgId);
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
          ...(orgId ? [{ label: orgName || "Empresa", path: buildOrgPath("/my-companies") }] : []),
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
          <div className="py-20"><Loader loaderText="Cargando plantillas..." /></div>
        ) : (
          <div className="flex flex-1 min-h-0 flex-col gap-5">
            {isAdmin && (
              <div className="flex justify-end">
                <button
                  onClick={() => navigate(buildOrgPath("/my-companies/templates/new"))}
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
              total={total}
              page={page}
              pages={pages}
              onPreview={setPreviewTarget}
              onSend={setSendTarget}
              onEdit={(item) => navigate(buildOrgPath(`/my-companies/templates/${item.id}/edit`))}
              onDelete={setDeleting}
              onPageChange={goToPage}
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
