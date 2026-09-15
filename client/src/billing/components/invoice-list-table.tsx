import { useState } from "react";
import { Receipt } from "lucide-react";
import EmptyState from "@/ui/components/common/empty-state";
import { Table, TableHeader, TableBody, TableRow, TableCell } from "@/ui/components/table/table";
import { PaginationWithIcon } from "@/ui/components/table/pagination-with-icon";
import { InvoiceStatusBadge } from "./invoice-status-badge";
import { formatCop, formatPeriod } from "../utils/format-currency";
import { INVOICE_LIST_PAGE_SIZE } from "../constants/pagination";
import type { InvoiceListTableProps } from "../types/props/invoice-list-table-props";

const COLUMNS = ["Periodo", "Total", "Estado", "Vencimiento", ""];

export const InvoiceListTable: React.FC<InvoiceListTableProps> = ({ invoices, onViewDetail }) => {
  const [page, setPage] = useState(1);

  if (invoices.length === 0) {
    return <EmptyState icon={Receipt} title="No hay facturas registradas todavía" className="py-12" />;
  }

  const totalPages = Math.max(1, Math.ceil(invoices.length / INVOICE_LIST_PAGE_SIZE));
  const visibleInvoices = invoices.slice((page - 1) * INVOICE_LIST_PAGE_SIZE, page * INVOICE_LIST_PAGE_SIZE);

  return (
    <div className="overflow-hidden rounded-xl border border-gray-200 dark:border-gray-800">
      <div className="overflow-x-auto">
        <Table>
          <TableHeader>
            <TableRow className="border-b border-gray-200 dark:border-gray-800">
              {COLUMNS.map((h) => (
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
                    type="button"
                    onClick={() => onViewDetail(inv.id)}
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
          Mostrando {(page - 1) * INVOICE_LIST_PAGE_SIZE + 1}–{Math.min(page * INVOICE_LIST_PAGE_SIZE, invoices.length)} de{" "}
          {invoices.length}
        </p>
        <PaginationWithIcon totalPages={totalPages} initialPage={page} onPageChange={setPage} />
      </div>
    </div>
  );
};
