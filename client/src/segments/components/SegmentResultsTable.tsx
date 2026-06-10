import { Table, TableBody, TableCell, TableHeader, TableRow } from "@/ui/components/table/table";
import type { SegmentExecuteResponse } from "@/segments/types/segment.types";

interface SegmentResultsTableProps {
  result: SegmentExecuteResponse;
}

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
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <p className="text-sm text-gray-500 dark:text-gray-400">
          <span className="font-semibold text-gray-800 dark:text-white">{result.rows}</span> fila
          {result.rows !== 1 ? "s" : ""} ·{" "}
          <span className="font-semibold text-gray-800 dark:text-white">
            {result.columns.length}
          </span>{" "}
          columna{result.columns.length !== 1 ? "s" : ""}
        </p>
        {result.mode === "audit" && result.fileName && (
          <span className="text-xs text-emerald-600 dark:text-emerald-400 font-medium">
            CSV generado: {result.fileName}
          </span>
        )}
      </div>

      <div className="overflow-hidden rounded-2xl border border-gray-200 dark:border-gray-800">
        <div className="overflow-x-auto custom-scrollbar max-h-96">
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
