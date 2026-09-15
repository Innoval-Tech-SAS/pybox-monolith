import { useState } from "react";
import { Download, SearchX } from "lucide-react";
import EmptyState from "@/ui/components/common/empty-state";
import { Table, TableBody, TableCell, TableHeader, TableRow } from "@/ui/components/table/table";
import { PaginationWithIcon } from "@/ui/components/table/pagination-with-icon";
import { resolveEntityFileUrl } from "@/query-builder/utils/resolve-entity-file-url";
import type { EntityResultsTableProps } from "@/query-builder/types/entity-results-table-props";

const ROWS_PER_PAGE = 50;

export const EntityResultsTable: React.FC<EntityResultsTableProps> = ({ result, config }) => {
  const [currentPage, setCurrentPage] = useState(1);

  if (!result.success || result.rows === 0) {
    return (
      <div className="py-12">
        <EmptyState icon={SearchX} title={`Sin resultados para este ${config.copy.entityNoun}`} />
      </div>
    );
  }

  const totalPages = Math.max(1, Math.ceil(result.rows / ROWS_PER_PAGE));
  const startIndex = (currentPage - 1) * ROWS_PER_PAGE;
  const visibleRows = result.data.slice(startIndex, startIndex + ROWS_PER_PAGE);

  return (
    <div className="flex min-h-0 flex-1 flex-col gap-3">
      <div className="flex shrink-0 items-center justify-between">
        <p className="text-sm text-gray-500 dark:text-gray-400">
          <span className="font-semibold text-gray-800 dark:text-white">{result.rows}</span> fila
          {result.rows !== 1 ? "s" : ""} ·{" "}
          <span className="font-semibold text-gray-800 dark:text-white">
            {result.columns.length}
          </span>{" "}
          columna{result.columns.length !== 1 ? "s" : ""}
        </p>
        {result.mode === "audit" && result.fileName && result.filePath && (
          <a
            href={resolveEntityFileUrl(result.filePath)}
            download={result.fileName}
            className="flex items-center gap-1.5 text-xs font-medium text-emerald-600 hover:underline dark:text-emerald-400"
          >
            <Download size={13} />
            Descargar {result.fileName}
          </a>
        )}
      </div>

      <div className="min-h-0 flex-1 overflow-hidden rounded-2xl border border-gray-200 dark:border-gray-800">
        <div className="custom-scrollbar h-full overflow-auto">
          <Table>
            <TableHeader>
              <TableRow className="border-b border-gray-200 bg-gray-50 dark:border-gray-800 dark:bg-white/3 sticky top-0">
                {result.columns.map((col) => (
                  <TableCell
                    key={col}
                    isHeader
                    className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wider text-gray-500 dark:text-gray-400 whitespace-nowrap"
                  >
                    {col}
                  </TableCell>
                ))}
              </TableRow>
            </TableHeader>
            <TableBody className="divide-y divide-gray-100 dark:divide-gray-800">
              {visibleRows.map((row, i) => (
                <TableRow key={startIndex + i} className="hover:bg-gray-50 dark:hover:bg-white/3">
                  {result.columns.map((col) => (
                    <TableCell
                      key={col}
                      className="px-4 py-3 text-sm text-gray-700 dark:text-gray-300 whitespace-nowrap"
                    >
                      {row[col] == null ? (
                        <span className="text-gray-300 dark:text-gray-600 italic">nulo</span>
                      ) : (
                        String(row[col])
                      )}
                    </TableCell>
                  ))}
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </div>
      </div>

      {totalPages > 1 && (
        <div className="flex shrink-0 flex-col gap-2 border-t border-gray-100 pt-3 dark:border-gray-800 sm:flex-row sm:items-center sm:justify-between">
          <p className="text-sm text-gray-500 dark:text-gray-400">
            Mostrando {startIndex + 1}–{Math.min(startIndex + ROWS_PER_PAGE, result.rows)} de {result.rows}
          </p>
          <PaginationWithIcon totalPages={totalPages} initialPage={currentPage} onPageChange={setCurrentPage} />
        </div>
      )}
    </div>
  );
};
