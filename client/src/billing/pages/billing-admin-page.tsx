import { useNavigate } from "react-router";
import { PageMeta } from "@/ui/pages/page-meta";
import { ModuleBase } from "@/ui/components/common/module-base";
import { Loader } from "@/ui/components/loader/loader";
import { Table, TableHeader, TableBody, TableRow, TableCell } from "@/ui/components/table/table";
import { PaginationWithIcon } from "@/ui/components/table/pagination-with-icon";
import { InvoiceStatusBadge } from "@/billing/components/invoice-status-badge";
import { formatCop, formatPeriod } from "@/billing/utils/format-currency";
import { useAdminInvoices } from "../hooks/use-admin-invoices";

const PAGE_SIZE = 20;

export const BillingAdminPage: React.FC = () => {
  const navigate = useNavigate();
  const { invoices, total, loading, fetchPage } = useAdminInvoices();
  const totalPages = Math.max(1, Math.ceil(total / PAGE_SIZE));

  return (
    <>
      <PageMeta title="Facturación" description="Facturación de todas las organizaciones" />
      <ModuleBase pageTitle="Facturación" breadcrumbItems={[{ label: "Inicio", path: "/home" }]}>
        {loading ? (
          <div className="py-20">
            <Loader />
          </div>
        ) : invoices.length === 0 ? (
          <p className="py-12 text-center text-sm text-gray-400 dark:text-gray-500">
            No hay facturas registradas todavía.
          </p>
        ) : (
          <div className="flex flex-col gap-5">
            <div className="overflow-x-auto rounded-xl border border-gray-200 dark:border-gray-800">
              <Table>
                <TableHeader>
                  <TableRow className="border-b border-gray-200 dark:border-gray-800">
                    {["Organización", "Periodo", "Total", "Estado", ""].map((h) => (
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
                        {inv.organizationName}
                      </TableCell>
                      <TableCell className="px-4 py-3 text-sm text-gray-600 dark:text-gray-400">
                        {formatPeriod(inv.periodYear, inv.periodMonth)}
                      </TableCell>
                      <TableCell className="px-4 py-3 text-sm text-gray-600 dark:text-gray-400">
                        {formatCop(inv.totalAmount)}
                      </TableCell>
                      <TableCell className="px-4 py-3">
                        <InvoiceStatusBadge status={inv.status} />
                      </TableCell>
                      <TableCell className="px-4 py-3">
                        <button
                          onClick={() => navigate(`/billing/${inv.id}`)}
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
            {totalPages > 1 && (
              <PaginationWithIcon totalPages={totalPages} onPageChange={(page) => fetchPage(page, PAGE_SIZE)} />
            )}
          </div>
        )}
      </ModuleBase>
    </>
  );
};
