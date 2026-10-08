import { useState } from "react";
import { useSearchParams } from "react-router";
import { Filter, Plus } from "lucide-react";
import { PageMeta } from "@/ui/pages/page-meta";
import { ModuleBase } from "@/ui/components/common/module-base";
import { ConfirmModal } from "@/ui/components/modal/confirm-modal";
import { useOrgModule } from "@/companies/hooks/use-org-module";
import { useBreadcrumb } from "@/companies/hooks/use-breadcrumb";
import { usePortfolios } from "@/companies/hooks/use-portfolios";
import { useDeleteWithConfirm } from "@/hooks/use-delete-with-confirm";
import { EntityTable } from "@/query-builder/components/entity-table";
import { EntityForm } from "@/query-builder/components/entity-form";
import { EntityExecuteModal } from "@/query-builder/components/entity-execute-modal";
import { EntityExecutionsHistory } from "@/query-builder/components/entity-executions-history";
import { useEntityList } from "@/query-builder/hooks/use-entity-list";
import { SEGMENT_QUERY_BUILDER_CONFIG as CONFIG } from "@/segments/constants/segment-query-builder-config";
import type { EntityResponse } from "@/query-builder/types/query-builder-types";

type View = "list" | "create" | "edit";

export const SegmentsPage: React.FC = () => {
  const [searchParams] = useSearchParams();
  const portfolioId = searchParams.get("portfolio") ?? "";
  const { orgId } = useOrgModule();
  const { build } = useBreadcrumb();

  const { portfolios } = usePortfolios(orgId);
  const { entities, total, page, pages, loading, refetch, deleteEntity, goToPage } =
    useEntityList(CONFIG.kind, CONFIG.configKey, portfolioId);

  const [view, setView] = useState<View>("list");
  const [editing, setEditing] = useState<EntityResponse | undefined>();
  const [executing, setExecuting] = useState<EntityResponse | null>(null);
  const [history, setHistory] = useState<EntityResponse | null>(null);
  const { deleting, setDeleting, confirmDelete, deletingInProgress } =
    useDeleteWithConfirm<EntityResponse>(deleteEntity);

  const portfolioName = portfolios.find((p) => p.id === portfolioId)?.name ?? "Portafolio";

  const breadcrumbs = build({
    portfolio: { id: portfolioId, name: portfolioName },
    communications: true,
  });

  const handleFormSuccess = () => {
    refetch();
    setView("list");
    setEditing(undefined);
  };

  const handleEdit = (segment: EntityResponse) => {
    setEditing(segment);
    setView("edit");
  };

  const handleDelete = (segment: EntityResponse) => setDeleting(segment);

  return (
    <>
      <PageMeta title="Segmentos" description="Listas dinámicas de deudores" />
      <ModuleBase pageTitle="Segmentos" pageIcon={Filter} breadcrumbItems={breadcrumbs}>
        {view === "list" ? (
          <div className="flex flex-1 min-h-0 flex-col gap-4">
            <div className="flex items-center justify-end">
              <button
                type="button"
                onClick={() => { setEditing(undefined); setView("create"); }}
                className="flex items-center gap-1.5 rounded-xl bg-brand-500 px-4 py-2 text-sm font-semibold text-white transition hover:bg-brand-600"
              >
                <Plus size={16} />
                Nuevo segmento
              </button>
            </div>

            <EntityTable
              config={CONFIG}
              entities={entities}
              loading={loading}
              total={total}
              page={page}
              pages={pages}
              onEdit={handleEdit}
              onExecute={(s) => setExecuting(s)}
              onHistory={(s) => setHistory(s)}
              onDelete={handleDelete}
              onPageChange={goToPage}
            />
          </div>
        ) : (
          <EntityForm
            config={CONFIG}
            scopeId={portfolioId}
            onSuccess={handleFormSuccess}
            onCancel={() => { setView("list"); setEditing(undefined); }}
            existing={view === "edit" ? editing : undefined}
          />
        )}
      </ModuleBase>

      {executing && (
        <EntityExecuteModal
          config={CONFIG}
          isOpen
          onClose={() => setExecuting(null)}
          entity={executing}
          scopeId={portfolioId}
        />
      )}

      {history && (
        <EntityExecutionsHistory
          config={CONFIG}
          isOpen
          onClose={() => setHistory(null)}
          entity={history}
          scopeId={portfolioId}
        />
      )}

      <ConfirmModal
        isOpen={!!deleting}
        onClose={() => setDeleting(null)}
        onConfirm={confirmDelete}
        title="Eliminar segmento"
        message={`¿Seguro que deseas eliminar el segmento "${deleting?.name}"? Esta acción no se puede deshacer.`}
        loading={deletingInProgress}
      />
    </>
  );
};
