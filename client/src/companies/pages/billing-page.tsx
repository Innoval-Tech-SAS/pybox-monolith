import { useState } from "react";
import { useNavigate } from "react-router";
import { Receipt } from "lucide-react";
import { PageMeta } from "@/ui/pages/page-meta";
import EmptyState from "@/ui/components/common/empty-state";
import { ModuleBase } from "@/ui/components/common/module-base";
import { Loader } from "@/ui/components/loader/loader";
import { Table, TableHeader, TableBody, TableRow, TableCell } from "@/ui/components/table/table";
import { PaginationWithIcon } from "@/ui/components/table/pagination-with-icon";
import { Alert } from "@/ui/components/alert/alert";
import { InvoiceStatusBadge } from "@/billing/components/invoice-status-badge";
import { formatCop, formatPeriod } from "@/billing/utils/format-currency";
import { useBilling } from "../hooks/use-billing";
import { useOrgModule } from "../hooks/use-org-module";
import { useBreadcrumb } from "../hooks/use-breadcrumb";
import { LOCK_ALERT_VARIANT } from "../constants/billing-lock-alert-variant";

const PAGE_SIZE = 10;

export const BillingPage: React.FC = () => {
  const { orgId, buildOrgPath } = useOrgModule();
  const { build } = useBreadcrumb();
  const navigate = useNavigate();

  const { currentInvoice, invoices, status, loading } = useBilling(orgId);
  const [page, setPage] = useState(1);
  const totalPages = Math.max(1, Math.ceil(invoices.length / PAGE_SIZE));
  const visibleInvoices = invoices.slice((page - 1) * PAGE_SIZE, page * PAGE_SIZE);

  return (
    <>
      <PageMeta title="Facturación" description="Facturación y pagos de la organización" />
      <ModuleBase
        pageTitle="Facturación"
        pageIcon={Receipt}
        breadcrumbItems={build()}
      >
        {loading ? (
          <div className="py-20">
            <Loader />
          </div>
        ) : (
          <div className="flex flex-col gap-5">
            {status && status.lockStatus !== "NINGUNO" && (
              <Alert
                variant={LOCK_ALERT_VARIANT[status.lockStatus] ?? "info"}
                title={
                  status.lockStatus === "BLOQUEADO"
                    ? "Cuenta bloqueada"
                    : status.lockStatus === "PAGO_REQUERIDO"
                      ? "Pago requerido"
                      : "Aviso de facturación"
                }
                message={status.message ?? "Hay una factura que requiere tu atención."}
              />
            )}

            {currentInvoice && (
              <div className="rounded-xl border border-gray-200 p-5 dark:border-gray-800">
                <div className="flex flex-wrap items-center justify-between gap-3">
                  <div>
                    <p className="text-xs uppercase tracking-wide text-gray-400">Factura vigente</p>
                    <p className="text-lg font-semibold text-gray-800 dark:text-white/90">
                      {formatPeriod(currentInvoice.periodYear, currentInvoice.periodMonth)}
                    </p>
                    <p className="text-2xl font-bold text-gray-800 dark:text-white/90">
                      {formatCop(currentInvoice.totalAmount)}
                    </p>
                  </div>
                  <div className="flex items-center gap-3">
                    <InvoiceStatusBadge status={currentInvoice.status} />
                    <button
                      onClick={() => navigate(buildOrgPath("/my-companies/billing", { invoice: currentInvoice.id }))}
                      className="inline-flex items-center gap-2 rounded-lg bg-brand-500 px-4 py-2.5 text-sm font-medium text-white shadow-theme-xs hover:bg-brand-600"
                    >
                      Ver detalle
                    </button>
                  </div>
                </div>
              </div>
            )}

            {invoices.length === 0 ? (
              <EmptyState icon={Receipt} title="No hay facturas registradas todavía" className="py-12" />
            ) : (
              <div className="overflow-hidden rounded-xl border border-gray-200 dark:border-gray-800">
                <div className="overflow-x-auto">
                  <Table>
                    <TableHeader>
                      <TableRow className="border-b border-gray-200 dark:border-gray-800">
                        {["Periodo", "Total", "Estado", "Vencimiento", ""].map((h) => (
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
                      {visibleInvoices.map((inv) => (
                        <TableRow key={inv.id} className="border-b border-gray-100 last:border-0 dark:border-gray-800">
                          <TableCell className="px-4 py-3 text-sm font-medium text-gray-800 dark:text-white/90">
                            {formatPeriod(inv.periodYear, inv.periodMonth)}
                          </TableCell>
                          <TableCell className="px-4 py-3 text-sm text-gray-600 dark:text-gray-400">
                            {formatCop(inv.totalAmount)}
                          </TableCell>
                          <TableCell className="px-4 py-3">
                            <InvoiceStatusBadge status={inv.status} />
                          </TableCell>
                          <TableCell className="px-4 py-3 text-sm text-gray-600 dark:text-gray-400">
                            {inv.dueAt ? new Date(inv.dueAt).toLocaleDateString("es-CO") : "—"}
                          </TableCell>
                          <TableCell className="px-4 py-3">
                            <button
                              onClick={() => navigate(buildOrgPath("/my-companies/billing", { invoice: inv.id }))}
                              className="text-sm font-medium text-brand-500 hover:text-brand-600"
                            >
                              Ver detalle
                            </button>
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </div>
                <div className="flex flex-col gap-2 border-t border-gray-100 px-4 py-3 dark:border-gray-800 sm:flex-row sm:items-center sm:justify-between">
                  <p className="text-sm text-gray-500 dark:text-gray-400">
                    Mostrando {(page - 1) * PAGE_SIZE + 1}–{Math.min(page * PAGE_SIZE, invoices.length)} de {invoices.length}
                  </p>
                  <PaginationWithIcon totalPages={totalPages} initialPage={page} onPageChange={setPage} />
                </div>
              </div>
            )}
          </div>
        )}
      </ModuleBase>
    </>
  );
};
