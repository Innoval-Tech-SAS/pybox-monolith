import { Eye, Mail, Pencil, Trash2, FileText, Search, RefreshCw } from "lucide-react";
import EmptyState from "@/ui/components/common/empty-state";
import { Loader } from "@/ui/components/loader/loader";
import { Badge } from "@/ui/components/badge";
import { ChannelBadge } from "@/ui/components/channel-badge";
import {
  Table,
  TableBody,
  TableCell,
  TableHeader,
  TableRow,
} from "@/ui/components/table/table";
import { PaginationWithIcon } from "@/ui/components/table/pagination-with-icon";
import { SortIcon } from "@/ui/components/table/sort-icon";
import { Select } from "@/ui/components/inputs/select";
import type { TemplatesTableProps } from "@/templates/types/templates-table-props";
import type { TemplateSortKey } from "@/templates/hooks/use-templates";
import { TEMPLATE_STATUS_LABELS as STATUS_LABELS, TEMPLATE_STATUS_COLORS as STATUS_COLORS } from "../constants/template-status-labels";
import { PAGE_SIZE_OPTIONS } from "@/campaigns/constants/table-pagination";
import {
  WHATSAPP_META_STATUS_COLORS,
  WHATSAPP_META_STATUS_LABELS,
} from "@/templates/constants/whatsapp-template-options";

export const TemplatesTable: React.FC<TemplatesTableProps> = ({
  items,
  isAdmin,
  loading,
  total,
  page,
  pages,
  search,
  pageSize,
  sortKey,
  sortOrder,
  whatsappData,
  refreshingId,
  onSearch,
  onPageSizeChange,
  onSort,
  onPreview,
  onSend,
  onEdit,
  onDelete,
  onRefreshStatus,
  onPageChange,
}) => {
  const startIndex = (page - 1) * pageSize + 1;
  const endIndex = Math.min(page * pageSize, total);

  const SortableHeader = ({ label, sortable }: { label: string; sortable?: TemplateSortKey }) => (
    <TableCell
      isHeader
      className="px-4 py-3 text-left text-xs font-medium uppercase tracking-wide text-gray-500 dark:text-gray-400"
    >
      {sortable ? (
        <button
          type="button"
          onClick={() => onSort(sortable)}
          className="flex items-center gap-1.5 select-none"
        >
          {label}
          <SortIcon active={sortKey === sortable} order={sortOrder} />
        </button>
      ) : (
        <div className="flex items-center gap-1.5">{label}</div>
      )}
    </TableCell>
  );

  // El estado de una plantilla de WhatsApp es el que reporta Meta; hasta que se cargue
  // (o si falta la fila de datos) se cae al estado local como el resto de canales.
  const renderStatus = (item: TemplatesTableProps["items"][number]) => {
    const meta = item.channel === "WHATSAPP" ? whatsappData[item.id] : undefined;
    if (meta) {
      return (
        <Badge size="sm" color={WHATSAPP_META_STATUS_COLORS[meta.metaStatus] ?? "light"}>
          {WHATSAPP_META_STATUS_LABELS[meta.metaStatus] ?? meta.metaStatus}
        </Badge>
      );
    }
    return <Badge size="sm" color={STATUS_COLORS[item.status]}>{STATUS_LABELS[item.status]}</Badge>;
  };

  const rowActions = (item: TemplatesTableProps["items"][number]) => {
    const isWhatsApp = item.channel === "WHATSAPP";
    return (
      <div className="flex items-center gap-1">
        {!isWhatsApp && (
          <button type="button" onClick={() => onPreview(item)} title="Vista previa" aria-label="Vista previa" className="rounded p-1.5 text-gray-400 hover:bg-gray-100 hover:text-brand-500 dark:hover:bg-gray-800">
            <Eye size={14} />
          </button>
        )}
        {isWhatsApp && (
          <button
            type="button"
            onClick={() => onRefreshStatus(item)}
            disabled={refreshingId === item.id}
            title="Refrescar estado en Meta"
            aria-label="Refrescar estado en Meta"
            className="rounded p-1.5 text-gray-400 hover:bg-gray-100 hover:text-brand-500 disabled:opacity-50 dark:hover:bg-gray-800"
          >
            <RefreshCw size={14} className={refreshingId === item.id ? "animate-spin" : ""} />
          </button>
        )}
        {item.channel === "EMAIL" && item.status === "ACTIVA" && (
          <button type="button" onClick={() => onSend(item)} title="Enviar" aria-label="Enviar" className="rounded p-1.5 text-gray-400 hover:bg-gray-100 hover:text-brand-500 dark:hover:bg-gray-800">
            <Mail size={14} />
          </button>
        )}
        {isAdmin && (
          <>
            {!isWhatsApp && (
              <button type="button" onClick={() => onEdit(item)} title="Editar" aria-label="Editar" className="rounded p-1.5 text-gray-400 hover:bg-gray-100 hover:text-gray-600 dark:hover:bg-gray-800">
                <Pencil size={14} />
              </button>
            )}
            <button type="button" onClick={() => onDelete(item)} title="Eliminar" aria-label="Eliminar" className="rounded p-1.5 text-gray-400 hover:bg-error-50 hover:text-error-500">
              <Trash2 size={14} />
            </button>
          </>
        )}
      </div>
    );
  };

  return (
    <div className="flex flex-1 min-h-0 flex-col overflow-hidden rounded-xl border border-gray-200 bg-white dark:border-white/5 dark:bg-white/3">
      {/* Toolbar */}
      <div className="shrink-0 flex flex-col gap-2 px-4 py-3 border-b border-gray-100 dark:border-white/5 sm:flex-row sm:items-center sm:justify-between">
        <div className="flex items-center gap-3">
          <span className="text-sm text-gray-500 dark:text-gray-400">Mostrar</span>
          <div className="w-20">
            <Select
              value={String(pageSize)}
              onChange={(v) => onPageSizeChange(Number(v))}
              options={PAGE_SIZE_OPTIONS.map((v) => ({ value: String(v), label: String(v) }))}
            />
          </div>
          <span className="text-sm text-gray-500 dark:text-gray-400">entradas</span>
        </div>
        <div className="relative">
          <span className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400 pointer-events-none">
            <Search size={15} />
          </span>
          <input
            type="text"
            value={search}
            onChange={(e) => onSearch(e.target.value)}
            placeholder="Buscar plantillas..."
            className="h-9 w-full rounded-lg border border-gray-300 bg-transparent py-2 pl-9 pr-4 text-sm text-gray-800 shadow-theme-xs placeholder:text-gray-400 focus:border-brand-300 focus:outline-hidden focus:ring-3 focus:ring-brand-500/10 dark:border-gray-700 dark:bg-gray-900 dark:text-white/90 sm:w-64"
          />
        </div>
      </div>

      {/* Desktop table */}
      <div className="hidden flex-1 min-h-0 overflow-auto custom-scrollbar sm:block">
        <Table>
          <TableHeader>
            <TableRow className="border-b border-gray-200 dark:border-gray-800">
              <SortableHeader label="Nombre" sortable="name" />
              <SortableHeader label="Canal" />
              <SortableHeader label="Estado" sortable="status" />
              <SortableHeader label="Asunto" />
              <SortableHeader label="" />
            </TableRow>
          </TableHeader>
          <TableBody>
            {loading ? (
              <TableRow>
                <TableCell className="px-4 py-10 text-center" colSpan={5}>
                  <Loader size="sm" loaderText="Cargando..." />
                </TableCell>
              </TableRow>
            ) : items.length === 0 ? (
              <TableRow>
                <TableCell className="px-4 py-10 text-center" colSpan={5}>
                  <EmptyState icon={FileText} title={search ? "Sin resultados para esa búsqueda" : "No hay plantillas registradas"} />
                </TableCell>
              </TableRow>
            ) : (
              items.map((item) => (
                <TableRow key={item.id} className="border-b border-gray-100 last:border-0 dark:border-gray-800 hover:bg-gray-50 dark:hover:bg-white/3">
                  <TableCell className="px-4 py-3 text-sm font-medium text-gray-800 dark:text-white/90">
                    {item.name}
                  </TableCell>
                  <TableCell className="px-4 py-3">
                    <ChannelBadge label={item.channel} />
                  </TableCell>
                  <TableCell className="px-4 py-3">
                    {renderStatus(item)}
                  </TableCell>
                  <TableCell className="px-4 py-3 text-sm text-gray-600 dark:text-gray-400">
                    {item.subject ?? "—"}
                  </TableCell>
                  <TableCell className="px-4 py-3">
                    {rowActions(item)}
                  </TableCell>
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </div>

      {/* Mobile cards */}
      <div className="flex flex-1 min-h-0 flex-col gap-3 overflow-y-auto p-4 sm:hidden">
        {loading ? (
          <div className="py-10"><Loader size="sm" /></div>
        ) : items.length === 0 ? (
          <EmptyState
            icon={FileText}
            title={search ? "Sin resultados para esa búsqueda" : "No hay plantillas registradas"}
            className="py-10"
          />
        ) : (
          items.map((item) => (
            <div
              key={item.id}
              className="w-full rounded-2xl border border-gray-200 bg-white p-4 dark:border-gray-800 dark:bg-gray-900"
            >
              <div className="flex items-start justify-between gap-2">
                <p className="min-w-0 truncate font-medium text-gray-800 dark:text-white/90">{item.name}</p>
                <div className="shrink-0">
                  {renderStatus(item)}
                </div>
              </div>
              <div className="mt-2 flex flex-wrap items-center gap-x-3 gap-y-1 text-xs text-gray-500 dark:text-gray-400">
                <ChannelBadge label={item.channel} />
                <span>{item.subject ?? "Sin asunto"}</span>
              </div>
              <div className="mt-3 flex justify-end border-t border-gray-100 pt-2 dark:border-gray-800">
                {rowActions(item)}
              </div>
            </div>
          ))
        )}
      </div>

      {/* Footer */}
      <div className="shrink-0 border-t border-gray-100 py-3 px-4 dark:border-white/5">
        <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
          <p className="text-sm text-gray-500 dark:text-gray-400">
            {total === 0
              ? "Sin resultados"
              : `Mostrando ${startIndex}–${endIndex} de ${total}`}
          </p>
          <PaginationWithIcon key={`${search}-${pageSize}`} totalPages={pages} initialPage={page} onPageChange={onPageChange} />
        </div>
      </div>
    </div>
  );
};
