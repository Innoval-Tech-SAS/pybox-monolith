import { Eye, Search, Users } from "lucide-react";
import EmptyState from "@/ui/components/common/empty-state";
import { useNavigate } from "react-router";
import { PaginationWithIcon } from "@/ui/components/table/pagination-with-icon";
import { SortIcon } from "@/ui/components/table/sort-icon";
import { Loader } from "@/ui/components/loader/loader";
import { Badge } from "@/ui/components/badge";
import { Table, TableBody, TableCell, TableHeader, TableRow } from "@/ui/components/table/table";
import { DEBTOR_TYPE_COLOR, DEBTOR_TYPE_LABEL } from "@/constants/companies/debtors-table";
import { useOrgModule } from "../hooks/use-org-module";
import type { DebtorsTableProps } from "@/types/props/debtors-table-props";
import type { DebtorSortKey } from "@/companies/hooks/use-portfolio-debtors";

const PAGE_SIZE_OPTIONS = [10, 20, 50];

export const DebtorsTable: React.FC<DebtorsTableProps> = ({
  portfolioId,
  debtors,
  total,
  page,
  pages,
  search,
  pageSize,
  sortKey,
  sortOrder,
  loading,
  onSearch,
  onPageSizeChange,
  onSort,
  onPageChange,
}) => {
  const navigate = useNavigate();
  const { buildOrgPath } = useOrgModule();

  const goToDebtor = (debtorId: string) => {
    navigate(buildOrgPath("/my-companies/portfolios/debtors", { portfolio: portfolioId, clientId: debtorId }));
  };

  const startIndex = (page - 1) * pageSize + 1;
  const endIndex = Math.min(page * pageSize, total);

  const SortableHeader = ({ label, sortable, className = "" }: { label: string; sortable?: DebtorSortKey; className?: string }) => (
    <TableCell
      isHeader
      className={`px-5 py-3.5 text-left text-xs font-semibold uppercase tracking-wider text-gray-500 dark:text-gray-400 ${className}`}
    >
      {sortable ? (
        <button
          type="button"
          onClick={() => onSort(sortable)}
          className="flex cursor-pointer select-none items-center gap-1.5"
        >
          {label}
          <SortIcon active={sortKey === sortable} order={sortOrder} />
        </button>
      ) : (
        <div className="flex items-center gap-1.5">{label}</div>
      )}
    </TableCell>
  );

  return (
    <div className="flex flex-1 min-h-0 flex-col overflow-hidden rounded-xl border border-gray-200 bg-white dark:border-white/5 dark:bg-white/3">
      {/* Toolbar */}
      <div className="shrink-0 flex flex-col gap-2 px-4 py-3 border-b border-gray-100 dark:border-white/5 sm:flex-row sm:items-center sm:justify-between">
        <div className="flex items-center gap-3">
          <span className="text-sm text-gray-500 dark:text-gray-400">Mostrar</span>
          <div className="relative">
            <select
              className="py-1.5 pl-3 pr-7 text-sm text-gray-800 bg-transparent border border-gray-300 rounded-lg appearance-none shadow-theme-xs focus:border-brand-300 focus:outline-hidden focus:ring-3 focus:ring-brand-500/10 dark:border-gray-700 dark:bg-gray-900 dark:text-white/90"
              value={pageSize}
              onChange={(e) => onPageSizeChange(Number(e.target.value))}
            >
              {PAGE_SIZE_OPTIONS.map((v) => <option key={v} value={v}>{v}</option>)}
            </select>
            <span className="absolute right-2 top-1/2 -translate-y-1/2 pointer-events-none text-gray-500">
              <svg className="stroke-current" width="12" height="12" viewBox="0 0 16 16" fill="none">
                <path d="M3.8335 5.9165L8.00016 10.0832L12.1668 5.9165" strokeWidth="1.2" strokeLinecap="round" strokeLinejoin="round" />
              </svg>
            </span>
          </div>
          <span className="text-sm text-gray-500 dark:text-gray-400">entradas</span>
        </div>
        <div className="relative">
          <span className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400 pointer-events-none">
            <Search size={15} />
          </span>
          <input
            type="text"
            placeholder="Buscar por nombre o documento…"
            value={search}
            onChange={(e) => onSearch(e.target.value)}
            className="h-9 w-full rounded-lg border border-gray-300 bg-transparent py-2 pl-9 pr-4 text-sm text-gray-800 shadow-theme-xs placeholder:text-gray-400 focus:border-brand-300 focus:outline-hidden focus:ring-3 focus:ring-brand-500/10 dark:border-gray-700 dark:bg-gray-900 dark:text-white/90 sm:w-72"
          />
        </div>
      </div>

      {/* Desktop table */}
      <div className="hidden flex-1 min-h-0 overflow-y-auto overflow-x-auto custom-scrollbar sm:block">
        <Table>
          <TableHeader>
            <TableRow className="border-b border-gray-200 bg-gray-50 dark:border-gray-800 dark:bg-white/3">
              <SortableHeader label="ID" />
              <SortableHeader label="Nombre" sortable="fullName" />
              <SortableHeader label="Tipo" />
              <SortableHeader label="Tipo doc." />
              <SortableHeader label="Documento" sortable="documentNumber" />
              <SortableHeader label="" />
            </TableRow>
          </TableHeader>
          <TableBody className="divide-y divide-gray-100 dark:divide-gray-800">
            {loading ? (
              <TableRow>
                <TableCell className="px-5 py-10 text-center" colSpan={6}>
                  <Loader size="sm" loaderText="Cargando..." />
                </TableCell>
              </TableRow>
            ) : debtors.length === 0 ? (
              <TableRow>
                <TableCell className="px-5 py-10 text-center" colSpan={6}>
                  <EmptyState
                    icon={Users}
                    title={search ? "Sin resultados para esa búsqueda" : "No hay clientes en este portafolio"}
                  />
                </TableCell>
              </TableRow>
            ) : (
              debtors.map((d) => (
                <TableRow key={d.id} className="transition hover:bg-gray-50 dark:hover:bg-white/3">
                  <TableCell className="px-5 py-4 text-sm font-mono text-gray-400">
                    {d.id}
                  </TableCell>
                  <TableCell className="px-5 py-4 text-sm font-medium text-gray-800 dark:text-white/90">
                    {d.fullName}
                  </TableCell>
                  <TableCell className="px-5 py-4">
                    <Badge variant="light" color={DEBTOR_TYPE_COLOR[d.debtorType] ?? "light"} size="sm">
                      {DEBTOR_TYPE_LABEL[d.debtorType] ?? d.debtorType}
                    </Badge>
                  </TableCell>
                  <TableCell className="px-5 py-4 text-sm text-gray-600 dark:text-gray-400">
                    {d.documentType}
                  </TableCell>
                  <TableCell className="px-5 py-4 text-sm font-mono text-gray-600 dark:text-gray-400">
                    {d.documentNumber}
                  </TableCell>
                  <TableCell className="px-5 py-4">
                    <button
                      type="button"
                      title="Ver detalle"
                      onClick={() => goToDebtor(d.id)}
                      className="rounded-lg p-1.5 text-gray-400 transition-all hover:bg-brand-50 hover:text-brand-600 dark:text-gray-500 dark:hover:bg-brand-500/10 dark:hover:text-brand-400"
                    >
                      <Eye size={18} />
                    </button>
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
        ) : debtors.length === 0 ? (
          <EmptyState
            icon={Users}
            title={search ? "Sin resultados para esa búsqueda" : "No hay clientes en este portafolio"}
            className="py-10"
          />
        ) : (
          debtors.map((d) => (
            <button
              key={d.id}
              type="button"
              onClick={() => goToDebtor(d.id)}
              className="w-full rounded-2xl border border-gray-200 bg-white p-4 text-left transition hover:bg-gray-50 dark:border-gray-800 dark:bg-gray-900 dark:hover:bg-white/5"
            >
              <div className="flex items-start justify-between gap-2">
                <p className="font-medium text-gray-800 dark:text-white/90">{d.fullName}</p>
                <Badge variant="light" color={DEBTOR_TYPE_COLOR[d.debtorType] ?? "light"} size="sm">
                  {DEBTOR_TYPE_LABEL[d.debtorType] ?? d.debtorType}
                </Badge>
              </div>
              <p className="mt-1 text-xs text-gray-400">
                {d.documentType} · {d.documentNumber}
              </p>
            </button>
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
