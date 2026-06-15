import { useState } from "react";
import { useSearchParams } from "react-router";
import { Plus } from "lucide-react";
import { PageMeta } from "@/ui/pages/page-meta";
import { ModuleBase } from "@/ui/components/common/module-base";
import { useMyCompanies } from "@/companies/hooks/use-my-companies";
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
  const orgId = searchParams.get("org") ?? "";
  const portfolioId = searchParams.get("portfolio") ?? "";

  const { orgs } = useMyCompanies();
  const { portfolios } = usePortfolios(orgId);
  const { segments, loading, refetch, deleteSegment } = useSegments(orgId);

  const [view, setView] = useState<View>("list");
  const [editing, setEditing] = useState<SegmentResponse | undefined>();
  const [executing, setExecuting] = useState<SegmentResponse | null>(null);
  const [history, setHistory] = useState<SegmentResponse | null>(null);

  const orgName = orgs.find((o) => o.id === orgId)?.name ?? "Empresa";
  const portfolioName = portfolios.find((p) => p.id === portfolioId)?.name ?? "Portafolio";

  const breadcrumbs = [
    { label: "Mis Empresas", path: "/my-companies" },
    { label: orgName, path: `/my-companies?org=${orgId}` },
    { label: "Mis Portafolios", path: `/my-companies/portfolios?org=${orgId}` },
    { label: portfolioName, path: `/my-companies/portfolios?org=${orgId}&portfolio=${portfolioId}` },
    { label: "Segmentos" },
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

  const handleDelete = async (segment: SegmentResponse) => {
    if (!confirm(`¿Eliminar el segmento "${segment.name}"?`)) return;
    await deleteSegment(segment.id);
  };

  return (
    <>
      <PageMeta title="Segmentos" description="Listas dinámicas de deudores" />
      <ModuleBase pageTitle="Segmentos" breadcrumbItems={breadcrumbs}>
        {view === "list" ? (
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <p className="text-sm text-gray-500 dark:text-gray-400">
                {segments.length} segmento{segments.length !== 1 ? "s" : ""}
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
              onEdit={handleEdit}
              onExecute={(s) => setExecuting(s)}
              onHistory={(s) => setHistory(s)}
              onDelete={handleDelete}
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
    </>
  );
};
