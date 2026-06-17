import { Download } from "lucide-react";
import { Table, TableBody, TableCell, TableHeader, TableRow } from "@/ui/components/table/table";
import { resolveSegmentFileUrl } from "@/segments/utils/segment-file-url";
import type { SegmentResultsTableProps } from "@/segments/types/segment-results-table-props";

export const SegmentResultsTable: React.FC<SegmentResultsTableProps> = ({ result }) => {
  if (!result.success || result.rows === 0) {
    return (
      <div className="flex flex-col items-center gap-2 py-12 text-center">
        <span className="text-3xl">📭</span>
        <p className="text-sm text-gray-500 dark:text-gray-400">Sin resultados para este segmento.</p>
      </div>
    );
  }

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
            href={resolveSegmentFileUrl(result.filePath)}
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
              {result.data.map((row, i) => (
                <TableRow key={i} className="hover:bg-gray-50 dark:hover:bg-white/3">
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
    </div>
  );
};
