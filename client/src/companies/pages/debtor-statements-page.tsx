import { useState } from "react";
import { useSearchParams } from "react-router";
import { Download, FileStack } from "lucide-react";
import EmptyState from "@/ui/components/common/empty-state";
import { PageMeta } from "@/ui/pages/page-meta";
import { ModuleBase } from "@/ui/components/common/module-base";
import { Loader } from "@/ui/components/loader/loader";
import { Button } from "@/ui/components/button/button";
import { API_URL } from "@/hooks/use-api-client";
import { useOrgModule } from "../hooks/use-org-module";
import { useBreadcrumb } from "../hooks/use-breadcrumb";
import { usePortfolios } from "../hooks/use-portfolios";
import { useDebtorCredits } from "../hooks/use-debtor-detail";
import { useDebtorStatements } from "../hooks/use-debtor-statements";
import { useGenerateStatement } from "../hooks/use-generate-statement";

const dateLabel = (iso: string) =>
  new Intl.DateTimeFormat("es-CO", { day: "numeric", month: "long", year: "numeric", hour: "numeric", minute: "2-digit" }).format(
    new Date(iso),
  );

export const DebtorStatementsPage: React.FC = () => {
  const [searchParams] = useSearchParams();
  const debtorId = searchParams.get("clientId");
  const portfolioId = searchParams.get("portfolio") ?? "";
  const { orgId } = useOrgModule();
  const { debtor } = useBreadcrumb();
  const { portfolios } = usePortfolios(orgId);
  const portfolioName = portfolios.find((p) => p.id === portfolioId)?.name ?? "Portafolio";

  const { credits } = useDebtorCredits(debtorId, portfolioId);
  const { items, loading, error, refetch } = useDebtorStatements(debtorId, portfolioId);
  const { generate, generating, error: generateError } = useGenerateStatement(debtorId, portfolioId);
  const [selectedCreditId, setSelectedCreditId] = useState("");

  const handleGenerate = async () => {
    const created = await generate(selectedCreditId || undefined);
    if (created) refetch();
  };

  return (
    <>
      <PageMeta title="Extractos del cliente" description="Estados de cuenta generados para el cliente" />
      <ModuleBase
        pageTitle="Extractos"
        pageIcon={FileStack}
        breadcrumbItems={debtor({ portfolioId, portfolioName, debtorId, includeDetail: true })}
      >
        <div className="mb-5 flex flex-wrap items-center gap-3 rounded-xl border border-gray-100 bg-gray-50 p-4 dark:border-gray-800 dark:bg-white/5">
          <select
            value={selectedCreditId}
            onChange={(e) => setSelectedCreditId(e.target.value)}
            className="rounded-lg border border-gray-300 bg-white px-3 py-2 text-sm text-gray-700 dark:border-gray-700 dark:bg-gray-800 dark:text-gray-300"
          >
            <option value="">Consolidado (todos los créditos activos)</option>
            {credits.map((c) => (
              <option key={c.id} value={c.id}>
                Crédito #{c.creditNumber}
              </option>
            ))}
          </select>
          <Button type="button" size="sm" loading={generating} onClick={handleGenerate}>
            Generar extracto
          </Button>
          {generateError && <p className="w-full text-sm text-error-600 dark:text-error-400">{generateError}</p>}
        </div>

        {loading ? (
          <div className="py-20">
            <Loader />
          </div>
        ) : error ? (
          <div className="rounded-xl border border-error-200 bg-error-50 p-5 text-sm text-error-600 dark:border-error-500/20 dark:bg-error-500/10 dark:text-error-400">
            {error}
          </div>
        ) : items.length === 0 ? (
          <EmptyState icon={FileStack} title="Este cliente aún no tiene extractos generados" className="py-20" />
        ) : (
          <div className="space-y-3">
            {items.map((statement) => (
              <a
                key={statement.id}
                href={`${API_URL}/debtors/${debtorId}/statements/${statement.id}/content?portfolioId=${portfolioId}`}
                target="_blank"
                rel="noopener noreferrer"
                className="flex items-center gap-3 rounded-xl border border-gray-100 p-4 transition hover:border-brand-200 hover:bg-brand-50/40 dark:border-gray-800 dark:hover:border-brand-500/30 dark:hover:bg-brand-500/5"
              >
                <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-error-50 text-error-600 dark:bg-error-500/10 dark:text-error-400">
                  <FileStack size={18} />
                </div>
                <div className="min-w-0 flex-1">
                  <p className="truncate text-sm font-medium text-gray-700 dark:text-gray-300">
                    {statement.creditNumber ? `Crédito #${statement.creditNumber}` : "Extracto consolidado"}
                  </p>
                  <p className="mt-1 text-xs text-gray-400">{dateLabel(statement.cutoffDate)}</p>
                </div>
                <Download size={14} className="shrink-0 text-gray-300 dark:text-gray-600" />
              </a>
            ))}
          </div>
        )}
      </ModuleBase>
    </>
  );
};
