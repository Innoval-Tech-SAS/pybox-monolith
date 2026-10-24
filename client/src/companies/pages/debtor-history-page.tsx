import { useState } from "react";
import { useSearchParams } from "react-router";
import { History, Send } from "lucide-react";
import EmptyState from "@/ui/components/common/empty-state";
import { PageMeta } from "@/ui/pages/page-meta";
import { ModuleBase } from "@/ui/components/common/module-base";
import { Loader } from "@/ui/components/loader/loader";
import { Badge } from "@/ui/components/badge";
import { PaginationWithIcon } from "@/ui/components/table/pagination-with-icon";
import { useOrgModule } from "../hooks/use-org-module";
import { useBreadcrumb } from "../hooks/use-breadcrumb";
import { usePortfolios } from "../hooks/use-portfolios";
import { useDebtorSendingsHistory } from "../hooks/use-debtor-sendings-history";
import { CONTACT_STATUS_COLOR } from "@/constants/companies/contact-status";
import { formatDebtorDateTime as formatDateTime } from "../utils/format-debtor-datetime";

export const DebtorHistoryPage: React.FC = () => {
  const [searchParams] = useSearchParams();
  const debtorId = searchParams.get("clientId");
  const portfolioId = searchParams.get("portfolio") ?? "";
  const { orgId } = useOrgModule();
  const { debtor } = useBreadcrumb();
  const { portfolios } = usePortfolios(orgId);
  const portfolioName = portfolios.find((p) => p.id === portfolioId)?.name ?? "Portafolio";

  const [activeChannelId, setActiveChannelId] = useState<string | null>(null);
  const [page, setPage] = useState(1);

  const { groups, loading, error } = useDebtorSendingsHistory(debtorId, portfolioId, page);
  const activeGroup = groups.find((g) => g.channelId === activeChannelId) ?? groups[0] ?? null;

  return (
    <>
      <PageMeta title="Historial de envíos" description="Historial de envíos del cliente" />
      <ModuleBase
        pageTitle="Historial de envíos"
        pageIcon={History}
        breadcrumbItems={debtor({ portfolioId, portfolioName, debtorId, includeDetail: true })}
      >
        {loading ? (
          <div className="py-20">
            <Loader />
          </div>
        ) : error ? (
          <div className="rounded-xl border border-error-200 bg-error-50 p-5 text-sm text-error-600 dark:border-error-500/20 dark:bg-error-500/10 dark:text-error-400">
            {error}
          </div>
        ) : groups.length === 0 ? (
          <EmptyState icon={Send} title="No hay envíos registrados para este cliente" className="py-20" />
        ) : (
          <div className="space-y-5">
            {/* Channel tabs */}
            <div className="flex flex-wrap gap-2">
              {groups.map((g) => (
                <button
                  key={g.channelId ?? "none"}
                  type="button"
                  onClick={() => {
                    setActiveChannelId(g.channelId);
                    setPage(1);
                  }}
                  className={`rounded-lg px-3 py-1.5 text-xs font-medium transition ${
                    (activeGroup?.channelId ?? null) === g.channelId
                      ? "bg-brand-50 text-brand-600 dark:bg-brand-500/15 dark:text-brand-400"
                      : "bg-gray-100 text-gray-600 hover:bg-gray-200 dark:bg-white/5 dark:text-gray-400 dark:hover:bg-white/10"
                  }`}
                >
                  {g.channelName} · {g.total}
                </button>
              ))}
            </div>

            {/* Messages list */}
            {activeGroup && (
              <div className="space-y-3">
                {activeGroup.items.length === 0 ? (
                  <p className="text-sm text-gray-400">Sin envíos en este canal.</p>
                ) : (
                  activeGroup.items.map((item) => (
                    <div key={item.id} className="rounded-xl border border-gray-100 p-4 dark:border-gray-800">
                      <div className="flex flex-wrap items-center justify-between gap-2">
                        <p className="text-sm font-medium text-gray-700 dark:text-gray-300">{item.recipient}</p>
                        <span className="text-xs text-gray-400">{formatDateTime(item.sentAt ?? item.createdAt)}</span>
                      </div>
                      <p className="mt-2 whitespace-pre-wrap text-sm text-gray-600 dark:text-gray-400">{item.content}</p>
                      <div className="mt-2 flex flex-wrap items-center gap-2">
                        <Badge variant="light" color={CONTACT_STATUS_COLOR[item.status] ?? "light"} size="sm">
                          {item.status}
                        </Badge>
                        {item.error && (
                          <span className="text-xs text-error-600 dark:text-error-400">{item.error}</span>
                        )}
                      </div>
                    </div>
                  ))
                )}

                {activeGroup.totalPages > 1 && (
                  <div className="border-t border-gray-100 pt-4 dark:border-gray-800">
                    <PaginationWithIcon
                      key={activeGroup.channelId ?? "none"}
                      totalPages={activeGroup.totalPages}
                      initialPage={activeGroup.page}
                      onPageChange={setPage}
                    />
                  </div>
                )}
              </div>
            )}
          </div>
        )}
      </ModuleBase>
    </>
  );
};
