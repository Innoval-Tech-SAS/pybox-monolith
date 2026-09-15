import { Table, TableHeader, TableBody, TableRow, TableCell } from "@/ui/components/table/table";
import { InvoiceStatusBadge } from "./invoice-status-badge";
import { formatCop, formatPeriod } from "../utils/format-currency";
import type { AdminInvoiceListTableProps } from "../types/props/admin-invoice-list-table-props";

const COLUMNS = ["Organización", "Periodo", "Total", "Estado", ""];

export const AdminInvoiceListTable: React.FC<AdminInvoiceListTableProps> = ({ invoices, onViewDetail }) => (
  <div className="overflow-x-auto rounded-xl border border-gray-200 dark:border-gray-800">
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
);
