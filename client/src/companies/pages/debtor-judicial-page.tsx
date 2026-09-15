import { useEffect, useState } from "react";
import { useSearchParams } from "react-router";
import { Gavel, Paperclip, Plus } from "lucide-react";
import EmptyState from "@/ui/components/common/empty-state";
import { PageMeta } from "@/ui/pages/page-meta";
import { ModuleBase } from "@/ui/components/common/module-base";
import { Loader } from "@/ui/components/loader/loader";
import { Badge } from "@/ui/components/badge";
import { Table, TableHeader, TableBody, TableRow, TableCell } from "@/ui/components/table/table";
import { useHasPermission } from "@/auth/hooks/use-has-permission";
import { useOrgModule } from "../hooks/use-org-module";
import { useBreadcrumb } from "../hooks/use-breadcrumb";
import { usePortfolios } from "../hooks/use-portfolios";
import { useDebtorCredits } from "../hooks/use-debtor-detail";
import { JudicialNotificationFormModal } from "../components/judicial-notification-form-modal";
import { useCreditJudicialNotifications } from "@/credits/hooks/use-credit-judicial-notifications";
import { useJudicialPriorities } from "@/credits/hooks/use-judicial-priorities";
import { JudicialNotificationDetailModal } from "@/credits/components/judicial-notification-detail-modal";
import { JUDICIAL_PRIORITY_BADGE_COLOR } from "@/constants/credits/judicial-priority";
import { formatPaymentDate } from "@/credits/utils/financial-calendar-utils";
import type { JudicialNotification } from "@/credits/types/judicial-types";

const JUDICIAL_PERMISSION = "portfolio.judicial";

export const DebtorJudicialPage: React.FC = () => {
  const [searchParams, setSearchParams] = useSearchParams();
  const debtorId = searchParams.get("clientId");
  const portfolioId = searchParams.get("portfolio") ?? "";
  const creditIdParam = searchParams.get("creditId");
  const { orgId } = useOrgModule();
  const { debtor } = useBreadcrumb();
  const canManage = useHasPermission(JUDICIAL_PERMISSION, orgId);

  const { credits, loading: loadingCredits } = useDebtorCredits(debtorId, portfolioId);
  const { portfolios } = usePortfolios(orgId);
  const portfolioName = portfolios.find((p) => p.id === portfolioId)?.name ?? "Portafolio";
  const { labels: priorityLabels } = useJudicialPriorities();

  const selectedCreditId = creditIdParam && credits.some((c) => c.id === creditIdParam) ? creditIdParam : credits[0]?.id ?? "";

  useEffect(() => {
    if (!selectedCreditId || selectedCreditId === creditIdParam) return;
    const next = new URLSearchParams(searchParams);
    next.set("creditId", selectedCreditId);
    setSearchParams(next, { replace: true });
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [selectedCreditId]);

  const { items, loading: loadingNotifications, creating, create, updateItem } = useCreditJudicialNotifications(selectedCreditId);

  const [showForm, setShowForm] = useState(false);
  const [selected, setSelected] = useState<JudicialNotification | null>(null);

  const loading = loadingCredits || (!!selectedCreditId && loadingNotifications);

  const selectCredit = (creditId: string) => {
    const next = new URLSearchParams(searchParams);
    next.set("creditId", creditId);
    setSearchParams(next);
  };

  return (
    <>
      <PageMeta title="Notificaciones judiciales" description="Notificaciones judiciales emitidas sobre los créditos del cliente" />
      <ModuleBase
        pageTitle="Judicial"
        pageIcon={Gavel}
        breadcrumbItems={debtor({
          portfolioId,
          portfolioName,
          debtorId,
          includeDetail: true,
        })}
      >
        {loadingCredits ? (
          <div className="py-20">
            <Loader />
          </div>
        ) : credits.length === 0 ? (
          <EmptyState icon={Gavel} title="Este cliente no tiene créditos" className="py-20" />
        ) : (
          <div className="flex flex-col gap-5">
            <div className="flex flex-wrap items-center justify-between gap-3">
              <div className="flex flex-wrap gap-2">
                {credits.map((credit) => (
                  <button
                    key={credit.id}
                    type="button"
                    onClick={() => selectCredit(credit.id)}
                    className={`rounded-lg border px-3 py-1.5 text-xs font-medium transition ${
                      credit.id === selectedCreditId
                        ? "border-brand-500 bg-brand-50 text-brand-600 dark:border-brand-500/50 dark:bg-brand-500/10 dark:text-brand-400"
                        : "border-gray-200 text-gray-600 hover:bg-gray-50 dark:border-gray-700 dark:text-gray-300 dark:hover:bg-white/5"
                    }`}
                  >
                    #{credit.creditNumber}
                  </button>
                ))}
              </div>
              {canManage && selectedCreditId && (
                <button
                  type="button"
                  onClick={() => setShowForm(true)}
                  className="inline-flex items-center gap-2 rounded-lg bg-brand-500 px-4 py-2.5 text-sm font-medium text-white shadow-theme-xs hover:bg-brand-600"
                >
                  <Plus size={16} />
                  Nueva notificación
                </button>
              )}
            </div>

            {loading ? (
              <div className="py-16">
                <Loader />
              </div>
            ) : items.length === 0 ? (
              <EmptyState icon={Gavel} title="Sin notificaciones judiciales para este crédito" className="py-16" />
            ) : (
              <div className="overflow-hidden rounded-xl border border-gray-200 dark:border-gray-800">
                <div className="overflow-x-auto">
                  <Table>
                    <TableHeader>
                      <TableRow className="border-b border-gray-200 dark:border-gray-800">
                        {["Título", "Prioridad", "Fecha", "Leída", "Adjuntos"].map((h) => (
                          <TableCell
                            key={h}
                            isHeader
                            className="px-4 py-3 text-left text-xs font-medium uppercase tracking-wide text-gray-500 dark:text-gray-400"
                          >
                            {h}
                          </TableCell>
                        ))}
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {items.map((item) => {
                        const rowCellClass = "cursor-pointer px-4 py-3";
                        return (
                          <TableRow
                            key={item.id}
                            className="border-b border-gray-100 last:border-0 hover:bg-gray-50 dark:border-gray-800 dark:hover:bg-white/5"
                          >
                            <TableCell
                              onClick={() => setSelected(item)}
                              className={`${rowCellClass} text-sm font-medium text-gray-800 dark:text-white/90`}
                            >
                              {item.title}
                            </TableCell>
                            <TableCell onClick={() => setSelected(item)} className={rowCellClass}>
                              <Badge variant="light" color={JUDICIAL_PRIORITY_BADGE_COLOR[item.priority] ?? "light"} size="sm">
                                {priorityLabels[item.priority] ?? item.priority}
                              </Badge>
                            </TableCell>
                            <TableCell
                              onClick={() => setSelected(item)}
                              className={`${rowCellClass} text-sm text-gray-600 dark:text-gray-400`}
                            >
                              {formatPaymentDate(item.notifiedAt)}
                            </TableCell>
                            <TableCell onClick={() => setSelected(item)} className={rowCellClass}>
                              <Badge variant="light" color={item.isRead ? "success" : "light"} size="sm">
                                {item.isRead ? "Sí" : "No"}
                              </Badge>
                            </TableCell>
                            <TableCell
                              onClick={() => setSelected(item)}
                              className={`${rowCellClass} text-sm text-gray-600 dark:text-gray-400`}
                            >
                              {item.attachments.length > 0 ? (
                                <span className="inline-flex items-center gap-1">
                                  <Paperclip size={12} />
                                  {item.attachments.length}
                                </span>
                              ) : (
                                "—"
                              )}
                            </TableCell>
                          </TableRow>
                        );
                      })}
                    </TableBody>
                  </Table>
                </div>
              </div>
            )}
          </div>
        )}
      </ModuleBase>

      {canManage && selectedCreditId && (
        <JudicialNotificationFormModal
          isOpen={showForm}
          onClose={() => setShowForm(false)}
          creditId={selectedCreditId}
          onSubmit={create}
          submitting={creating}
          onCreated={updateItem}
        />
      )}

      <JudicialNotificationDetailModal
        notification={selected}
        isOpen={!!selected}
        onClose={() => setSelected(null)}
        priorityLabels={priorityLabels}
      />
    </>
  );
};
