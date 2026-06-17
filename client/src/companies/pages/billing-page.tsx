import { useSearchParams, useNavigate } from "react-router";
import { PageMeta } from "@/ui/pages/page-meta";
import { ModuleBase } from "@/ui/components/common/module-base";
import { Loader } from "@/ui/components/loader/loader";
import { Table, TableHeader, TableBody, TableRow, TableCell } from "@/ui/components/table/table";
import { Alert } from "@/ui/components/alert/alert";
import { InvoiceStatusBadge } from "@/billing/components/invoice-status-badge";
import { formatCop, formatPeriod } from "@/billing/utils/format-currency";
import { useBilling } from "../hooks/use-billing";

const LOCK_ALERT_VARIANT: Record<string, "info" | "warning" | "error"> = {
  WARNING: "info",
  PAYMENT_REQUIRED: "warning",
  BLOCKED: "error",
};

export const BillingPage: React.FC = () => {
  const [searchParams] = useSearchParams();
  const orgId = searchParams.get("org") ?? "";
  const navigate = useNavigate();

  const { currentInvoice, invoices, status, loading } = useBilling(orgId);

  return (
    <>
      <PageMeta title="Facturación" description="Facturación y pagos de la organización" />
      <ModuleBase
        pageTitle="Facturación"
        breadcrumbItems={[
          { label: "Mis Empresas", path: "/my-companies" },
          ...(orgId ? [{ label: "Empresa", path: `/my-companies?org=${orgId}` }] : []),
        ]}
      >
        {loading ? (
          <div className="py-20">
            <Loader />
          </div>
        ) : (
          <div className="flex flex-col gap-5">
            {status && status.lockStatus !== "NONE" && (
              <Alert
                variant={LOCK_ALERT_VARIANT[status.lockStatus] ?? "info"}
                title={
                  status.lockStatus === "BLOCKED"
                    ? "Cuenta bloqueada"
                    : status.lockStatus === "PAYMENT_REQUIRED"
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
                      onClick={() => navigate(`/my-companies/billing/${currentInvoice.id}?org=${orgId}`)}
                      className="inline-flex items-center gap-2 rounded-lg bg-brand-500 px-4 py-2.5 text-sm font-medium text-white shadow-theme-xs hover:bg-brand-600"
                    >
                      Ver detalle
                    </button>
                  </div>
                </div>
              </div>
            )}

            {invoices.length === 0 ? (
              <p className="py-12 text-center text-sm text-gray-400 dark:text-gray-500">
                No hay facturas registradas todavía.
              </p>
            ) : (
              <div className="overflow-x-auto rounded-xl border border-gray-200 dark:border-gray-800">
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
                    {invoices.map((inv) => (
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
                            onClick={() => navigate(`/my-companies/billing/${inv.id}?org=${orgId}`)}
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
            )}
          </div>
        )}
      </ModuleBase>
    </>
  );
};
