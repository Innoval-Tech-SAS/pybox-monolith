import { useState } from "react";
import { BarChart2, Plus } from "lucide-react";
import { PageMeta } from "@/ui/pages/page-meta";
import { ModuleBase } from "@/ui/components/common/module-base";
import { ConfirmModal } from "@/ui/components/modal/confirm-modal";
import { useOrgModule } from "@/companies/hooks/use-org-module";
import { useBreadcrumb } from "@/companies/hooks/use-breadcrumb";
import { useDeleteWithConfirm } from "@/hooks/use-delete-with-confirm";
import { EntityTable } from "@/query-builder/components/entity-table";
import { EntityForm } from "@/query-builder/components/entity-form";
import { EntityExecuteModal } from "@/query-builder/components/entity-execute-modal";
import { EntityExecutionsHistory } from "@/query-builder/components/entity-executions-history";
import { REPORT_QUERY_BUILDER_CONFIG as CONFIG } from "@/reports/constants/report-query-builder-config";
import { useReports } from "@/reports/hooks/use-reports";
import type { EntityResponse } from "@/query-builder/types/query-builder-types";

type View = "list" | "create" | "edit";

export const ReportsPage: React.FC = () => {
  const { orgId } = useOrgModule();
  const { build } = useBreadcrumb();

  const { entities, total, page, pages, loading, refetch, deleteEntity, goToPage } =
    useReports(orgId);

  const [view, setView] = useState<View>("list");
  const [editing, setEditing] = useState<EntityResponse | undefined>();
  const [executing, setExecuting] = useState<EntityResponse | null>(null);
  const [history, setHistory] = useState<EntityResponse | null>(null);
  const { deleting, setDeleting, confirmDelete, deletingInProgress } =
    useDeleteWithConfirm<EntityResponse>(deleteEntity);

  const breadcrumbs = build();

  const handleFormSuccess = () => {
    refetch();
    setView("list");
    setEditing(undefined);
  };

  const handleEdit = (report: EntityResponse) => {
    setEditing(report);
    setView("edit");
  };

  const handleDelete = (report: EntityResponse) => setDeleting(report);

  return (
    <>
      <PageMeta title="Reportes" description="Genera y consulta reportes de gestión" />
      <ModuleBase pageTitle="Reportes" pageIcon={BarChart2} breadcrumbItems={breadcrumbs}>
        {view === "list" ? (
          <div className="flex flex-1 min-h-0 flex-col gap-4">
            <div className="flex items-center justify-end">
              <button
                type="button"
                onClick={() => { setEditing(undefined); setView("create"); }}
                className="flex items-center gap-1.5 rounded-xl bg-brand-500 px-4 py-2 text-sm font-semibold text-white transition hover:bg-brand-600"
              >
                <Plus size={16} />
                Nuevo reporte
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
              onExecute={(r) => setExecuting(r)}
              onHistory={(r) => setHistory(r)}
              onDelete={handleDelete}
              onPageChange={goToPage}
            />
          </div>
        ) : (
          <EntityForm
            config={CONFIG}
            scopeId={orgId}
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
          scopeId={orgId}
        />
      )}

      {history && (
        <EntityExecutionsHistory
          config={CONFIG}
          isOpen
          onClose={() => setHistory(null)}
          entity={history}
          scopeId={orgId}
        />
      )}

      <ConfirmModal
        isOpen={!!deleting}
        onClose={() => setDeleting(null)}
        onConfirm={confirmDelete}
        title="Eliminar reporte"
        message={`¿Seguro que deseas eliminar el reporte "${deleting?.name}"? Esta acción no se puede deshacer.`}
        loading={deletingInProgress}
      />
    </>
  );
};
