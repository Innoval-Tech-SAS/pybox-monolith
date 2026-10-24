import { useState } from "react";
import { Table, TableHeader, TableBody, TableRow, TableCell } from "@/ui/components/table/table";
import { PaginationWithIcon } from "@/ui/components/table/pagination-with-icon";
import { INVOICE_LIST_PAGE_SIZE } from "../constants/pagination";
import type { InvoicePaymentAttemptsTableProps } from "../types/props/invoice-payment-attempts-table-props";

const COLUMNS = ["#", "Referencia", "Estado", "Fecha"];

export const InvoicePaymentAttemptsTable: React.FC<InvoicePaymentAttemptsTableProps> = ({ attempts }) => {
  const [page, setPage] = useState(1);

  if (attempts.length === 0) return null;

  const totalPages = Math.max(1, Math.ceil(attempts.length / INVOICE_LIST_PAGE_SIZE));
  const visibleAttempts = attempts.slice((page - 1) * INVOICE_LIST_PAGE_SIZE, page * INVOICE_LIST_PAGE_SIZE);

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
            {visibleAttempts.map((attempt) => (
              <TableRow key={attempt.id} className="border-b border-gray-100 last:border-0 dark:border-gray-800">
                <TableCell className="px-4 py-3 text-sm text-gray-600 dark:text-gray-400">
                  {attempt.attemptNumber}
                </TableCell>
                <TableCell className="px-4 py-3 text-sm text-gray-600 dark:text-gray-400">
                  {attempt.providerReference ?? "—"}
                </TableCell>
                <TableCell className="px-4 py-3 text-sm text-gray-600 dark:text-gray-400">
                  {attempt.status}
                </TableCell>
                <TableCell className="px-4 py-3 text-sm text-gray-600 dark:text-gray-400">
                  {new Date(attempt.createdAt).toLocaleString("es-CO")}
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </div>
      <div className="flex flex-col gap-2 border-t border-gray-100 px-4 py-3 dark:border-gray-800 sm:flex-row sm:items-center sm:justify-between">
        <p className="text-sm text-gray-500 dark:text-gray-400">
          Mostrando {(page - 1) * INVOICE_LIST_PAGE_SIZE + 1}–{Math.min(page * INVOICE_LIST_PAGE_SIZE, attempts.length)} de{" "}
          {attempts.length}
        </p>
        <PaginationWithIcon totalPages={totalPages} initialPage={page} onPageChange={setPage} />
      </div>
    </div>
  );
};
