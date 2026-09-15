import { useState } from "react";
import { useNavigate, useSearchParams } from "react-router";
import { Mail, Plus } from "lucide-react";
import { PageMeta } from "@/ui/pages/page-meta";
import { ModuleBase } from "@/ui/components/common/module-base";
import { ConfirmModal } from "@/ui/components/modal/confirm-modal";
import { getSession } from "@/auth/utils/auth-session-utils";
import { useDeleteWithConfirm } from "@/hooks/use-delete-with-confirm";
import { useOrgModule } from "@/companies/hooks/use-org-module";
import { useBreadcrumb } from "@/companies/hooks/use-breadcrumb";
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
  const { orgId, buildOrgPath } = useOrgModule();
  const { build } = useBreadcrumb();

  const { portfolios } = usePortfolios(orgId);
  const portfolioName = portfolios.find((p) => p.id === portfolioId)?.name ?? "Portafolio";

  const {
    items, total, page, pages, loading, saving,
    search, setSearch,
    pageSize, setPageSize,
    sortKey, sortOrder, handleSort,
    remove, preview, send, goToPage,
  } = useTemplates(portfolioId);
  const { variables: variableOptions } = useTemplateVariables(orgId);

  const user = getSession();
  const isAdmin = user?.scope === "GLOBAL" || user?.orgs?.[orgId]?.role === "ADMINISTRADOR";

  const [previewTarget, setPreviewTarget] = useState<Template | null>(null);
  const [sendTarget, setSendTarget] = useState<Template | null>(null);
  const { deleting, setDeleting, confirmDelete, deletingInProgress } = useDeleteWithConfirm<Template>(remove);

  const handleSend = async (id: string, to: string, subject: string, sub: Record<string, string>) => {
    const result = await send(id, { to, subject: subject || null, sub });
    return result !== null;
  };

  return (
    <>
      <PageMeta title="Plantillas" description="Gestión de plantillas de correo y SMS" />
      <ModuleBase
        pageTitle="Plantillas"
        pageIcon={Mail}
        breadcrumbItems={build({
          portfolio: { id: portfolioId, name: portfolioName },
          communications: true,
        })}
      >
        <div className="flex flex-1 min-h-0 flex-col gap-5">
          {isAdmin && (
            <div className="flex justify-end">
              <button
                onClick={() => navigate(buildOrgPath("/my-companies/templates/new", { portfolio: portfolioId }))}
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
            onPreview={setPreviewTarget}
            onSend={setSendTarget}
            onEdit={(item) => navigate(buildOrgPath(`/my-companies/templates/${item.id}/edit`, { portfolio: portfolioId }))}
            onDelete={setDeleting}
            onPageChange={goToPage}
          />
        </div>
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
        loading={deletingInProgress}
      />
    </>
  );
};
