import { useState } from "react";
import { useNavigate, useSearchParams } from "react-router";
import { Mail, Plus } from "lucide-react";
import { PageMeta } from "@/ui/pages/page-meta";
import { ModuleBase } from "@/ui/components/common/module-base";
import { ConfirmModal } from "@/ui/components/modal/confirm-modal";
import { Button } from "@/ui/components/button/button";
import { getSession } from "@/auth/utils/auth-session-utils";
import { useDeleteWithConfirm } from "@/hooks/use-delete-with-confirm";
import { useOrgModule } from "@/companies/hooks/use-org-module";
import { useBreadcrumb } from "@/companies/hooks/use-breadcrumb";
import { usePortfolios } from "@/companies/hooks/use-portfolios";
import { useTemplates } from "@/templates/hooks/use-templates";
import { useTemplateVariables } from "@/templates/hooks/use-template-variables";
import { useWhatsAppTemplates } from "@/templates/hooks/use-whatsapp-templates";
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
    remove, preview, send, goToPage, refetch,
  } = useTemplates(portfolioId);
  const { variables: variableOptions } = useTemplateVariables(orgId);
  const {
    dataByTemplateId: whatsappData,
    refreshingId,
    refreshStatus: refreshWhatsAppStatus,
    remove: removeWhatsApp,
  } = useWhatsAppTemplates(portfolioId);

  const user = getSession();
  const isAdmin = user?.scope === "GLOBAL" || user?.orgs?.[orgId]?.role === "ADMINISTRADOR";

  const [previewTarget, setPreviewTarget] = useState<Template | null>(null);
  const [sendTarget, setSendTarget] = useState<Template | null>(null);

  // Las plantillas de WhatsApp se borran por su propio flujo: elimina también en Meta.
  const removeTemplate = async (id: string) => {
    if (items.find((t) => t.id === id)?.channel !== "WHATSAPP") return remove(id);
    const removed = await removeWhatsApp(id);
    if (removed) goToPage(items.length === 1 && page > 1 ? page - 1 : page);
    return removed;
  };
  const { deleting, setDeleting, confirmDelete, deletingInProgress } = useDeleteWithConfirm<Template>(removeTemplate);

  const handleRefreshStatus = async (template: Template) => {
    const updated = await refreshWhatsAppStatus(template.id);
    if (updated) refetch();
  };

  const handleSend = async (id: string, to: string, subject: string, sub: Record<string, string>) => {
    const result = await send(id, { to, subject: subject || null, sub });
    return result !== null;
  };

  return (
    <>
      <PageMeta title="Plantillas" description="Gestión de plantillas de correo, SMS y WhatsApp" />
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
              <Button
                type="button"
                size="sm"
                startIcon={<Plus size={16} />}
                onClick={() => navigate(buildOrgPath("/my-companies/templates/new", { portfolio: portfolioId }))}
              >
                Nueva plantilla
              </Button>
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
            whatsappData={whatsappData}
            refreshingId={refreshingId}
            onSearch={setSearch}
            onPageSizeChange={setPageSize}
            onSort={handleSort}
            onPreview={setPreviewTarget}
            onSend={setSendTarget}
            onEdit={(item) => navigate(buildOrgPath(`/my-companies/templates/${item.id}/edit`, { portfolio: portfolioId }))}
            onDelete={setDeleting}
            onRefreshStatus={handleRefreshStatus}
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
        message={
          deleting?.channel === "WHATSAPP"
            ? `¿Seguro que deseas eliminar la plantilla "${deleting.name}"? También se eliminará en Meta y no se puede deshacer.`
            : `¿Seguro que deseas eliminar la plantilla "${deleting?.name}"? Esta acción no se puede deshacer.`
        }
        loading={deletingInProgress}
      />
    </>
  );
};
