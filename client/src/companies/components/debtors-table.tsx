import { Eye, Search } from "lucide-react";
import { useNavigate } from "react-router";
import { PaginationWithIcon } from "@/ui/components/table/pagination-with-icon";
import { Loader } from "@/ui/components/loader/loader";
import { Badge } from "@/ui/components/badge";
import { Table, TableBody, TableCell, TableHeader, TableRow } from "@/ui/components/table/table";
import { DEBTOR_TYPE_COLOR } from "@/constants/companies/debtors-table";
import type { DebtorsTableProps } from "@/types/props/debtors-table-props";

export const DebtorsTable: React.FC<DebtorsTableProps> = ({
  orgId,
  portfolioId,
  debtors,
  total,
  page,
  pages,
  search,
  loading,
  onSearch,
  onPageChange,
}) => {
  const navigate = useNavigate();

  const goToDebtor = (debtorId: number) => {
    navigate(`/my-companies/portfolios/debtors/${debtorId}?org=${orgId}&portfolio=${portfolioId}`);
  };

  return (
    <>
      {/* Search */}
      <div className="mb-4 flex items-center gap-3">
        <div className="relative flex-1 max-w-sm">
          <span className="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 text-gray-400">
            <Search size={16} />
          </span>
          <input
            type="text"
            placeholder="Buscar por número de documento…"
            value={search}
            onChange={(e) => onSearch(e.target.value)}
            className="w-full rounded-lg border border-gray-300 bg-white py-2.5 pl-9 pr-4 text-sm text-gray-700 outline-none transition focus:border-brand-500 focus:ring-1 focus:ring-brand-500 dark:border-gray-700 dark:bg-gray-900 dark:text-gray-300 dark:placeholder-gray-500"
          />
        </div>
        <span className="text-sm text-gray-500 dark:text-gray-400 shrink-0">
          {total} cliente{total !== 1 ? "s" : ""}
        </span>
      </div>

      {loading ? (
        <div className="py-20">
          <Loader />
        </div>
      ) : debtors.length === 0 ? (
        <div className="flex flex-col items-center gap-3 py-20 text-center">
          <span className="text-4xl">📂</span>
          <p className="text-sm text-gray-500 dark:text-gray-400">
            {search ? "Sin resultados para esa búsqueda." : "No hay clientes en este portafolio."}
          </p>
        </div>
      ) : (
        <>
          {/* Desktop table */}
          <div className="hidden overflow-hidden rounded-2xl border border-gray-200 dark:border-gray-800 sm:block">
            <div className="overflow-x-auto custom-scrollbar">
              <Table>
                <TableHeader>
                  <TableRow className="border-b border-gray-200 bg-gray-50 dark:border-gray-800 dark:bg-white/3">
                    {["ID", "Nombre", "Tipo", "Tipo doc.", "Documento", ""].map((h, i) => (
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
                  {debtors.map((d) => (
                    <TableRow key={d.id} className="transition hover:bg-gray-50 dark:hover:bg-white/3">
                      <TableCell className="px-5 py-4 text-sm font-mono text-gray-400">
                        {d.id}
                      </TableCell>
                      <TableCell className="px-5 py-4 text-sm font-medium text-gray-800 dark:text-white/90">
                        {d.fullName}
                      </TableCell>
                      <TableCell className="px-5 py-4">
                        <Badge variant="light" color={DEBTOR_TYPE_COLOR[d.debtorType] ?? "light"} size="sm">
                          {d.debtorType}
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
                  ))}
                </TableBody>
              </Table>
            </div>
          </div>

          {/* Mobile cards */}
          <div className="flex flex-col gap-3 sm:hidden">
            {debtors.map((d) => (
              <button
                key={d.id}
                onClick={() => goToDebtor(d.id)}
                className="w-full rounded-2xl border border-gray-200 bg-white p-4 text-left transition hover:bg-gray-50 dark:border-gray-800 dark:bg-gray-900 dark:hover:bg-white/5"
              >
                <div className="flex items-start justify-between gap-2">
                  <p className="font-medium text-gray-800 dark:text-white/90">{d.fullName}</p>
                  <Badge variant="light" color={DEBTOR_TYPE_COLOR[d.debtorType] ?? "light"} size="sm">
                    {d.debtorType}
                  </Badge>
                </div>
                <p className="mt-1 text-xs text-gray-400">
                  {d.documentType} · {d.documentNumber}
                </p>
              </button>
            ))}
          </div>

          {/* Pagination */}
          {pages > 1 && (
            <div className="mt-4 flex flex-col gap-2 border-t border-gray-100 pt-4 dark:border-gray-800 sm:flex-row sm:items-center sm:justify-between">
              <p className="text-sm text-gray-500 dark:text-gray-400">
                Página {page} de {pages} · {total} cliente{total !== 1 ? "s" : ""}
              </p>
              <PaginationWithIcon
                key={search}
                totalPages={pages}
                initialPage={page}
                onPageChange={onPageChange}
              />
            </div>
          )}
        </>
      )}
    </>
  );
};
