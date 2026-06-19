import { Pause, Pencil, Play, Trash2 } from "lucide-react";
import {
  Table,
  TableBody,
  TableCell,
  TableHeader,
  TableRow,
} from "@/ui/components/table/table";
import { PaginationWithIcon } from "@/ui/components/table/pagination-with-icon";
import type { CampaignStatus } from "@/types/campaigns/campaign-types";
import type { CampaignsTableProps } from "@/campaigns/types/campaigns-table-props";
import { formatSchedule } from "../utils/campaign-utils";

const STATUS_LABELS: Record<CampaignStatus, string> = {
  "borrador": "Borrador",
  "programada": "Programada",
  "en ejecución": "En ejecución",
  "completada": "Completada",
  "fallida": "Fallida",
  "pausada": "Pausada",
  "cancelada": "Cancelada",
};

const STATUS_COLORS: Record<CampaignStatus, string> = {
  "borrador": "bg-gray-100 text-gray-500 dark:bg-gray-800 dark:text-gray-400",
  "programada": "bg-brand-50 text-brand-700 dark:bg-brand-500/15 dark:text-brand-400",
  "en ejecución": "bg-warning-50 text-warning-700 dark:bg-warning-500/15 dark:text-orange-400",
  "completada": "bg-success-50 text-success-700 dark:bg-success-500/10 dark:text-success-400",
  "fallida": "bg-error-50 text-error-600 dark:bg-error-500/10 dark:text-error-400",
  "pausada": "bg-orange-50 text-orange-700 dark:bg-orange-500/15 dark:text-orange-400",
  "cancelada": "bg-gray-200 text-gray-600 dark:bg-white/5 dark:text-gray-500",
};

export const CampaignsTable: React.FC<CampaignsTableProps> = ({
  items,
  channels,
  isAdmin,
  saving,
  total,
  page,
  pages,
  onActivate,
  onPause,
  onEdit,
  onDelete,
  onPageChange,
}) => {
  const channelLabelById = new Map(channels.map((c) => [c.id, c.label]));

  if (items.length === 0) {
    return (
      <div className="flex flex-1 min-h-0 items-center justify-center">
        <p className="text-sm text-gray-400 dark:text-gray-500">No hay campañas registradas.</p>
      </div>
    );
  }

  return (
    <div className="flex flex-1 min-h-0 flex-col">
      <div className="flex-1 min-h-0 overflow-y-auto rounded-xl border border-gray-200 dark:border-gray-800">
      <Table>
        <TableHeader>
          <TableRow className="border-b border-gray-200 dark:border-gray-800">
            {["Nombre", "Canal", "Estado", "Programación", "Destinatarios", ""].map((h) => (
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
          {items.map((item) => (
            <TableRow key={item.id} className="border-b border-gray-100 last:border-0 dark:border-gray-800">
              <TableCell className="px-4 py-3">
                <p className="text-sm font-medium text-gray-800 dark:text-white/90">{item.name}</p>
                {item.description && (
                  <p className="text-xs text-gray-400 dark:text-gray-500">{item.description}</p>
                )}
              </TableCell>
              <TableCell className="px-4 py-3">
                <span className="inline-flex items-center rounded-full bg-gray-100 px-2.5 py-0.5 text-xs font-medium text-gray-600 dark:bg-gray-800 dark:text-gray-300">
                  {channelLabelById.get(item.channelId) ?? "—"}
                </span>
              </TableCell>
              <TableCell className="px-4 py-3">
                <span className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ${STATUS_COLORS[item.status]}`}>
                  {STATUS_LABELS[item.status]}
                </span>
              </TableCell>
              <TableCell className="px-4 py-3 text-sm text-gray-600 dark:text-gray-400">
                {formatSchedule(item)}
              </TableCell>
              <TableCell className="px-4 py-3 text-sm text-gray-600 dark:text-gray-400">
                {item.totalRecipients}
              </TableCell>
              <TableCell className="px-4 py-3">
                <div className="flex items-center gap-1">
                  {isAdmin && (item.status === "borrador" || item.status === "pausada") && (
                    <button onClick={() => onActivate(item.id)} disabled={saving} title="Activar" className="rounded p-1.5 text-gray-400 hover:bg-success-50 hover:text-success-600 disabled:opacity-50">
                      <Play size={14} />
                    </button>
                  )}
                  {isAdmin && item.status === "programada" && (
                    <button onClick={() => onPause(item.id)} disabled={saving} title="Pausar" className="rounded p-1.5 text-gray-400 hover:bg-orange-50 hover:text-orange-600 disabled:opacity-50">
                      <Pause size={14} />
                    </button>
                  )}
                  {isAdmin && (item.status === "borrador" || item.status === "pausada") && (
                    <button onClick={() => onEdit(item)} title="Editar" className="rounded p-1.5 text-gray-400 hover:bg-gray-100 hover:text-gray-600 dark:hover:bg-gray-800">
                      <Pencil size={14} />
                    </button>
                  )}
                  {isAdmin && (
                    <button onClick={() => onDelete(item)} title="Eliminar" className="rounded p-1.5 text-gray-400 hover:bg-error-50 hover:text-error-500">
                      <Trash2 size={14} />
                    </button>
                  )}
                </div>
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
      </div>

      {pages > 1 && (
        <div className="mt-4 flex flex-col gap-2 border-t border-gray-100 pt-4 dark:border-gray-800 sm:flex-row sm:items-center sm:justify-between">
          <p className="text-sm text-gray-500 dark:text-gray-400">
            Página {page} de {pages} · {total} campaña{total !== 1 ? "s" : ""}
          </p>
          <PaginationWithIcon key={page} totalPages={pages} initialPage={page} onPageChange={onPageChange} />
        </div>
      )}
    </div>
  );
};
