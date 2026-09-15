import { Download, FileStack } from "lucide-react";
import EmptyState from "@/ui/components/common/empty-state";
import { ModuleBase } from "@/ui/components/common/module-base";
import { API_URL } from "@/hooks/use-api-client";
import { useMyStatements } from "@/credits/hooks/use-my-statements";
import { IdentityVerificationNotice } from "@/credits/components/identity-verification-notice";

const dateLabel = (iso: string) =>
  new Intl.DateTimeFormat("es-CO", { day: "numeric", month: "long", year: "numeric" }).format(new Date(iso));

export const MyStatementsPage: React.FC = () => {
  const { statements, loading, error, identityPending, refetch } = useMyStatements();

  return (
    <ModuleBase pageTitle="Mis Extractos" pageIcon={FileStack} showBack>
      {loading && <p className="text-sm text-gray-500 dark:text-gray-400">Cargando tus extractos...</p>}

      {!loading && identityPending && <IdentityVerificationNotice />}

      {!loading && !identityPending && error && (
        <div className="flex flex-col items-start gap-3">
          <p className="text-sm text-red-600 dark:text-red-400">{error}</p>
          <button
            onClick={refetch}
            className="rounded-lg border border-gray-300 bg-white px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50 dark:border-gray-700 dark:bg-gray-800 dark:text-gray-300"
          >
            Reintentar
          </button>
        </div>
      )}

      {!loading && !identityPending && !error && statements.length === 0 && (
        <EmptyState icon={FileStack} title="Aún no tienes extractos generados" className="py-20" />
      )}

      {!loading && !identityPending && !error && statements.length > 0 && (
        <div className="space-y-3">
          {statements.map((statement) => (
            <a
              key={statement.id}
              href={`${API_URL}/statements/my-statements/${statement.id}/content`}
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center gap-3 rounded-xl border border-gray-200 p-4 transition hover:border-brand-300 hover:shadow-sm dark:border-gray-800 dark:bg-white/3 dark:hover:border-brand-700"
            >
              <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-error-50 text-error-600 dark:bg-error-500/10 dark:text-error-400">
                <FileStack size={18} />
              </div>
              <div className="min-w-0 flex-1">
                <p className="truncate text-sm font-medium text-gray-700 dark:text-gray-300">
                  {statement.creditNumber ? `Crédito #${statement.creditNumber}` : "Extracto consolidado"}
                </p>
                <p className="mt-1 text-xs text-gray-400">
                  {statement.organizationName} · {dateLabel(statement.cutoffDate)}
                </p>
              </div>
              <Download size={14} className="shrink-0 text-gray-300 dark:text-gray-600" />
            </a>
          ))}
        </div>
      )}
    </ModuleBase>
  );
};
