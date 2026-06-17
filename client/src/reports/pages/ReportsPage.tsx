import { useState } from "react";
import { useSearchParams } from "react-router";
import { Plus } from "lucide-react";
import { PageMeta } from "@/ui/pages/page-meta";
import { ModuleBase } from "@/ui/components/common/module-base";
import { ConfirmModal } from "@/ui/components/modal/confirm-modal";
import { useMyCompanies } from "@/companies/hooks/use-my-companies";
import { ReportsTable } from "@/reports/components/reports-table";
import { ReportForm } from "@/reports/components/report-form/report-form";
import { ReportExecuteModal } from "@/reports/components/report-execute-modal";
import { ReportExecutionsHistory } from "@/reports/components/report-executions-history";
import { useReports } from "@/reports/hooks/use-reports";
import type { ReportResponse } from "@/reports/types/report.types";

type View = "list" | "create" | "edit";

export const ReportsPage: React.FC = () => {
  const [searchParams] = useSearchParams();
  const orgId = searchParams.get("org") ?? "";

  const { orgs } = useMyCompanies();
  const { reports, loading, refetch, deleteReport } = useReports(orgId);

  const [view, setView] = useState<View>("list");
  const [editing, setEditing] = useState<ReportResponse | undefined>();
  const [executing, setExecuting] = useState<ReportResponse | null>(null);
  const [history, setHistory] = useState<ReportResponse | null>(null);
  const [deleting, setDeleting] = useState<ReportResponse | null>(null);
  const [deletingInProgress, setDeletingInProgress] = useState(false);

  const orgName = orgs.find((o) => o.id === orgId)?.name ?? "Empresa";

  const breadcrumbs = [
    { label: "Mis Empresas", path: "/my-companies" },
    { label: orgName, path: `/my-companies?org=${orgId}` },
    { label: "Reportes", path: `/my-companies/reports?org=${orgId}` },
  ];

  const handleFormSuccess = () => {
    refetch();
    setView("list");
    setEditing(undefined);
  };

  const handleEdit = (report: ReportResponse) => {
    setEditing(report);
    setView("edit");
  };

  const handleDelete = (report: ReportResponse) => setDeleting(report);

  const confirmDelete = async () => {
    if (!deleting) return;
    setDeletingInProgress(true);
    try {
      await deleteReport(deleting.id);
      setDeleting(null);
    } finally {
      setDeletingInProgress(false);
    }
  };

  return (
    <>
      <PageMeta title="Reportes" description="Genera y consulta reportes de gestión" />
      <ModuleBase pageTitle="Reportes" breadcrumbItems={breadcrumbs}>
        {view === "list" ? (
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <p className="text-sm text-gray-500 dark:text-gray-400">
                {reports.length} reporte{reports.length !== 1 ? "s" : ""}
              </p>
              <button
                type="button"
                onClick={() => { setEditing(undefined); setView("create"); }}
                className="flex items-center gap-1.5 rounded-xl bg-brand-500 px-4 py-2 text-sm font-semibold text-white transition hover:bg-brand-600"
              >
                <Plus size={16} />
                Nuevo reporte
              </button>
            </div>

            <ReportsTable
              reports={reports}
              loading={loading}
              onEdit={handleEdit}
              onExecute={(r) => setExecuting(r)}
              onHistory={(r) => setHistory(r)}
              onDelete={handleDelete}
            />
          </div>
        ) : (
          <ReportForm
            orgId={orgId}
            onSuccess={handleFormSuccess}
            onCancel={() => { setView("list"); setEditing(undefined); }}
            existing={view === "edit" ? editing : undefined}
          />
        )}
      </ModuleBase>

      {executing && (
        <ReportExecuteModal
          isOpen
          onClose={() => setExecuting(null)}
          report={executing}
          orgId={orgId}
        />
      )}

      {history && (
        <ReportExecutionsHistory
          isOpen
          onClose={() => setHistory(null)}
          report={history}
          orgId={orgId}
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
