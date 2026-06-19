import { Edit2, Play, Trash2, History } from "lucide-react";
import { Loader } from "@/ui/components/loader/loader";
import { Table, TableBody, TableCell, TableHeader, TableRow } from "@/ui/components/table/table";
import { PaginationWithIcon } from "@/ui/components/table/pagination-with-icon";
import type { ReportsTableProps, ActionBtnProps } from "@/reports/types/reports-table-props";
import { ALL_TABLES } from "@/reports/constants/report.constants";

const getMainTableLabel = (reportConfig: Record<string, unknown>): string => {
  const tables = reportConfig.tables as Array<{ name: string }> | undefined;
  const name = tables?.[0]?.name ?? "";
  return ALL_TABLES.find((t) => t.name === name)?.label ?? name;
};

export const ReportsTable: React.FC<ReportsTableProps> = ({
  reports,
  loading,
  total,
  page,
  pages,
  onEdit,
  onExecute,
  onHistory,
  onDelete,
  onPageChange,
}) => {
  if (loading) {
    return (
      <div className="flex flex-1 min-h-0 items-center justify-center">
        <Loader />
      </div>
    );
  }

  if (reports.length === 0) {
    return (
      <div className="flex flex-1 min-h-0 flex-col items-center justify-center gap-3 text-center">
        <span className="text-4xl">📋</span>
        <p className="text-sm text-gray-500 dark:text-gray-400">
          No hay reportes. Crea el primero.
        </p>
      </div>
    );
  }

  return (
    <div className="flex flex-1 min-h-0 flex-col">
      {/* Desktop */}
      <div className="hidden flex-1 min-h-0 flex-col overflow-hidden rounded-2xl border border-gray-200 dark:border-gray-800 sm:flex">
        <div className="flex-1 min-h-0 overflow-y-auto custom-scrollbar">
          <Table>
            <TableHeader>
              <TableRow className="border-b border-gray-200 bg-gray-50 dark:border-gray-800 dark:bg-white/3">
                {["ID", "Nombre", "Tabla principal", "Descripción", ""].map((h, i) => (
                  <TableCell
                    key={i}
                    isHeader
                    className="px-5 py-3.5 text-left text-xs font-semibold uppercase tracking-wider text-gray-500 dark:text-gray-400"
                  >
                    {h}
                  </TableCell>
                ))}
              </TableRow>
            </TableHeader>
            <TableBody className="divide-y divide-gray-100 dark:divide-gray-800">
              {reports.map((r) => (
                <TableRow key={r.id} className="transition hover:bg-gray-50 dark:hover:bg-white/3">
                  <TableCell className="px-5 py-4 text-sm font-mono text-gray-400">
                    {r.id}
                  </TableCell>
                  <TableCell className="px-5 py-4 text-sm font-medium text-gray-800 dark:text-white/90">
                    {r.name}
                  </TableCell>
                  <TableCell className="px-5 py-4 text-sm text-gray-600 dark:text-gray-400">
                    {getMainTableLabel(r.reportConfig)}
                  </TableCell>
                  <TableCell className="px-5 py-4 text-sm text-gray-500 dark:text-gray-400 max-w-xs truncate">
                    {r.description ?? "—"}
                  </TableCell>
                  <TableCell className="px-5 py-4">
                    <div className="flex items-center gap-1">
                      <ActionBtn title="Ejecutar" onClick={() => onExecute(r)} icon={<Play size={16} />} />
                      <ActionBtn title="Historial" onClick={() => onHistory(r)} icon={<History size={16} />} />
                      <ActionBtn title="Editar" onClick={() => onEdit(r)} icon={<Edit2 size={16} />} />
                      <ActionBtn title="Eliminar" onClick={() => onDelete(r)} icon={<Trash2 size={16} />} danger />
                    </div>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </div>
      </div>

      {/* Mobile */}
      <div className="flex flex-1 min-h-0 flex-col gap-3 overflow-y-auto sm:hidden">
        {reports.map((r) => (
          <div
            key={r.id}
            className="rounded-2xl border border-gray-200 bg-white p-4 dark:border-gray-800 dark:bg-gray-900"
          >
            <div className="flex items-start justify-between gap-2">
              <div>
                <p className="font-medium text-gray-800 dark:text-white/90">{r.name}</p>
                <p className="mt-0.5 text-xs text-gray-400">
                  {getMainTableLabel(r.reportConfig)}
                </p>
                {r.description && (
                  <p className="mt-1 text-xs text-gray-500 dark:text-gray-400 line-clamp-2">
                    {r.description}
                  </p>
                )}
              </div>
              <div className="flex items-center gap-1 shrink-0">
                <ActionBtn title="Ejecutar" onClick={() => onExecute(r)} icon={<Play size={15} />} />
                <ActionBtn title="Historial" onClick={() => onHistory(r)} icon={<History size={15} />} />
                <ActionBtn title="Editar" onClick={() => onEdit(r)} icon={<Edit2 size={15} />} />
                <ActionBtn title="Eliminar" onClick={() => onDelete(r)} icon={<Trash2 size={15} />} danger />
              </div>
            </div>
          </div>
        ))}
      </div>

      {pages > 1 && (
        <div className="mt-4 flex flex-col gap-2 border-t border-gray-100 pt-4 dark:border-gray-800 sm:flex-row sm:items-center sm:justify-between">
          <p className="text-sm text-gray-500 dark:text-gray-400">
            Página {page} de {pages} · {total} reporte{total !== 1 ? "s" : ""}
          </p>
          <PaginationWithIcon key={page} totalPages={pages} initialPage={page} onPageChange={onPageChange} />
        </div>
      )}
    </div>
  );
};

const ActionBtn: React.FC<ActionBtnProps> = ({ title, onClick, icon, danger }) => (
  <button
    type="button"
    title={title}
    onClick={onClick}
    className={`rounded-lg p-1.5 transition-all ${
      danger
        ? "text-gray-400 hover:bg-red-50 hover:text-red-500 dark:text-gray-500 dark:hover:bg-red-500/10 dark:hover:text-red-400"
        : "text-gray-400 hover:bg-brand-50 hover:text-brand-600 dark:text-gray-500 dark:hover:bg-brand-500/10 dark:hover:text-brand-400"
    }`}
  >
    {icon}
  </button>
);
