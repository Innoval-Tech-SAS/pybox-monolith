import { useState } from "react";
import { FileText } from "lucide-react";
import EmptyState from "@/ui/components/common/empty-state";
import { Table, TableHeader, TableBody, TableRow, TableCell } from "@/ui/components/table/table";
import { PaginationWithIcon } from "@/ui/components/table/pagination-with-icon";
import { formatUsd } from "../utils/format-currency";
import { INVOICE_LIST_PAGE_SIZE } from "../constants/pagination";
import type { InvoiceItemsTableProps } from "../types/props/invoice-items-table-props";

const COLUMNS = ["Campaña", "Canal", "Cantidad", "Subtotal"];

export const InvoiceItemsTable: React.FC<InvoiceItemsTableProps> = ({ items }) => {
  const [page, setPage] = useState(1);

  if (items.length === 0) {
    return <EmptyState icon={FileText} title="Sin consumo registrado en este periodo" className="py-6" />;
  }

  const totalPages = Math.max(1, Math.ceil(items.length / INVOICE_LIST_PAGE_SIZE));
  const visibleItems = items.slice((page - 1) * INVOICE_LIST_PAGE_SIZE, page * INVOICE_LIST_PAGE_SIZE);

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
            {visibleItems.map((item) => (
              <TableRow key={item.id} className="border-b border-gray-100 last:border-0 dark:border-gray-800">
                <TableCell className="px-4 py-3 text-sm font-medium text-gray-800 dark:text-white/90">
                  {item.campaignName}
                </TableCell>
                <TableCell className="px-4 py-3 text-sm text-gray-600 dark:text-gray-400">
                  {item.channelName}
                </TableCell>
                <TableCell className="px-4 py-3 text-sm text-gray-600 dark:text-gray-400">{item.quantity}</TableCell>
                <TableCell className="px-4 py-3 text-sm text-gray-600 dark:text-gray-400">
                  {formatUsd(item.subtotalBase)}
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </div>
      <div className="flex flex-col gap-2 border-t border-gray-100 px-4 py-3 dark:border-gray-800 sm:flex-row sm:items-center sm:justify-between">
        <p className="text-sm text-gray-500 dark:text-gray-400">
          Mostrando {(page - 1) * INVOICE_LIST_PAGE_SIZE + 1}–{Math.min(page * INVOICE_LIST_PAGE_SIZE, items.length)} de{" "}
          {items.length}
        </p>
        <PaginationWithIcon totalPages={totalPages} initialPage={page} onPageChange={setPage} />
      </div>
    </div>
  );
};
