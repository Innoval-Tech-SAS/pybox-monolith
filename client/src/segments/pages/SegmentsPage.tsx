import { useState } from "react";
import { useSearchParams } from "react-router";
import { Plus } from "lucide-react";
import { PageMeta } from "@/ui/pages/page-meta";
import { ModuleBase } from "@/ui/components/common/module-base";
import { ConfirmModal } from "@/ui/components/modal/confirm-modal";
import { useOrgModule } from "@/companies/hooks/use-org-module";
import { usePortfolios } from "@/companies/hooks/use-portfolios";
import { SegmentsTable } from "@/segments/components/segments-table";
import { SegmentForm } from "@/segments/components/segment-form/segment-form";
import { SegmentExecuteModal } from "@/segments/components/segment-execute-modal";
import { SegmentExecutionsHistory } from "@/segments/components/segment-executions-history";
import { useSegments } from "@/segments/hooks/use-segments";
import type { SegmentResponse } from "@/segments/types/segment.types";

type View = "list" | "create" | "edit";

export const SegmentsPage: React.FC = () => {
  const [searchParams] = useSearchParams();
  const portfolioId = searchParams.get("portfolio") ?? "";
  const { orgId, orgName, buildOrgPath } = useOrgModule();

  const { portfolios } = usePortfolios(orgId);
  const { segments, total, page, pages, loading, refetch, deleteSegment, goToPage } = useSegments(orgId);

  const [view, setView] = useState<View>("list");
  const [editing, setEditing] = useState<SegmentResponse | undefined>();
  const [executing, setExecuting] = useState<SegmentResponse | null>(null);
  const [history, setHistory] = useState<SegmentResponse | null>(null);
  const [deleting, setDeleting] = useState<SegmentResponse | null>(null);
  const [deletingInProgress, setDeletingInProgress] = useState(false);

  const portfolioName = portfolios.find((p) => p.id === portfolioId)?.name ?? "Portafolio";

  const breadcrumbs = [
    { label: "Mis Empresas", path: "/my-companies" },
    { label: orgName || "Empresa", path: buildOrgPath("/my-companies") },
    { label: "Mis Portafolios", path: buildOrgPath("/my-companies/portfolios") },
    { label: portfolioName, path: buildOrgPath("/my-companies/portfolios", { portfolio: portfolioId }) },
    { label: "Comunicaciones", path: buildOrgPath("/my-companies/portfolios/communications", { portfolio: portfolioId }) },
  ];

  const handleFormSuccess = () => {
    refetch();
    setView("list");
    setEditing(undefined);
  };

  const handleEdit = (segment: SegmentResponse) => {
    setEditing(segment);
    setView("edit");
  };

  const handleDelete = (segment: SegmentResponse) => setDeleting(segment);

  const confirmDelete = async () => {
    if (!deleting) return;
    setDeletingInProgress(true);
    try {
      await deleteSegment(deleting.id);
      setDeleting(null);
    } finally {
      setDeletingInProgress(false);
    }
  };

  return (
    <>
      <PageMeta title="Segmentos" description="Listas dinámicas de deudores" />
      <ModuleBase pageTitle="Segmentos" breadcrumbItems={breadcrumbs}>
        {view === "list" ? (
          <div className="flex flex-1 min-h-0 flex-col gap-4">
            <div className="flex items-center justify-between">
              <p className="text-sm text-gray-500 dark:text-gray-400">
                {total} segmento{total !== 1 ? "s" : ""}
              </p>
              <button
                type="button"
                onClick={() => { setEditing(undefined); setView("create"); }}
                className="flex items-center gap-1.5 rounded-xl bg-brand-500 px-4 py-2 text-sm font-semibold text-white transition hover:bg-brand-600"
              >
                <Plus size={16} />
                Nuevo segmento
              </button>
            </div>

            <SegmentsTable
              segments={segments}
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
          <SegmentForm
            orgId={orgId}
            onSuccess={handleFormSuccess}
            onCancel={() => { setView("list"); setEditing(undefined); }}
            existing={view === "edit" ? editing : undefined}
          />
        )}
      </ModuleBase>

      {executing && (
        <SegmentExecuteModal
          isOpen
          onClose={() => setExecuting(null)}
          segment={executing}
          orgId={orgId}
        />
      )}

      {history && (
        <SegmentExecutionsHistory
          isOpen
          onClose={() => setHistory(null)}
          segment={history}
          orgId={orgId}
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
