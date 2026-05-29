import { useState } from "react";
import { ChevronLeft, ChevronRight, Search } from "lucide-react";
import { Loader } from "@/ui/components/loader/loader";
import { Table, TableBody, TableCell, TableHeader, TableRow } from "@/ui/components/table/table";
import { DebtorDetailsModal } from "./debtor-details-modal";
import type { PortfolioDebtor } from "@/types/companies/portfolio-debtor-types";

interface DebtorsTableProps {
  debtors: PortfolioDebtor[];
  total: number;
  page: number;
  pages: number;
  search: string;
  loading: boolean;
  onSearch: (value: string) => void;
  onPageChange: (page: number) => void;
}

export const DebtorsTable: React.FC<DebtorsTableProps> = ({
  debtors,
  total,
  page,
  pages,
  search,
  loading,
  onSearch,
  onPageChange,
}) => {
  const [selectedDebtor, setSelectedDebtor] = useState<PortfolioDebtor | null>(null);

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

      {/* Table */}
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
            <div className="overflow-x-auto">
              <Table>
                <TableHeader>
                  <TableRow className="border-b border-gray-200 bg-gray-50 dark:border-gray-800 dark:bg-white/[0.03]">
                    {["ID", "Nombre", "Tipo doc.", "Documento"].map((h) => (
                      <TableCell
                        key={h}
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
                    <TableRow
                      key={d.id}
                      className="cursor-pointer transition hover:bg-gray-50 dark:hover:bg-white/[0.03]"
                      onClick={() => setSelectedDebtor(d)}
                    >
                      <TableCell className="px-5 py-4 text-sm text-gray-400 font-mono">
                        {d.id}
                      </TableCell>
                      <TableCell className="px-5 py-4 text-sm font-medium text-gray-800 dark:text-white/90">
                        {d.fullName}
                      </TableCell>
                      <TableCell className="px-5 py-4 text-sm text-gray-600 dark:text-gray-400">
                        {d.documentType}
                      </TableCell>
                      <TableCell className="px-5 py-4 text-sm font-mono text-gray-600 dark:text-gray-400">
                        {d.documentNumber}
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
                onClick={() => setSelectedDebtor(d)}
                className="w-full rounded-2xl border border-gray-200 bg-white p-4 text-left transition hover:bg-gray-50 dark:border-gray-800 dark:bg-gray-900 dark:hover:bg-white/5"
              >
                <p className="font-medium text-gray-800 dark:text-white/90">{d.fullName}</p>
                <p className="mt-1 text-xs text-gray-500">
                  {d.documentType} · {d.documentNumber}
                </p>
              </button>
            ))}
          </div>

          {/* Pagination */}
          {pages > 1 && (
            <div className="mt-4 flex items-center justify-between">
              <p className="text-sm text-gray-500 dark:text-gray-400">
                Página {page} de {pages}
              </p>
              <div className="flex gap-2">
                <button
                  onClick={() => onPageChange(page - 1)}
                  disabled={page <= 1}
                  className="flex h-8 w-8 items-center justify-center rounded-lg border border-gray-200 text-gray-600 transition hover:bg-gray-50 disabled:opacity-40 dark:border-gray-700 dark:text-gray-400"
                >
                  <ChevronLeft size={16} />
                </button>
                <button
                  onClick={() => onPageChange(page + 1)}
                  disabled={page >= pages}
                  className="flex h-8 w-8 items-center justify-center rounded-lg border border-gray-200 text-gray-600 transition hover:bg-gray-50 disabled:opacity-40 dark:border-gray-700 dark:text-gray-400"
                >
                  <ChevronRight size={16} />
                </button>
              </div>
            </div>
          )}
        </>
      )}

      <DebtorDetailsModal
        debtor={selectedDebtor}
        onClose={() => setSelectedDebtor(null)}
      />
    </>
  );
};
