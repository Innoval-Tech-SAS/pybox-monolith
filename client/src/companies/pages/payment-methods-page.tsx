import { useState } from "react";
import { useNavigate } from "react-router";
import { Plus, Pencil, Trash2, CreditCard } from "lucide-react";
import EmptyState from "@/ui/components/common/empty-state";
import { PageMeta } from "@/ui/pages/page-meta";
import { ModuleBase } from "@/ui/components/common/module-base";
import { Loader } from "@/ui/components/loader/loader";
import { Table, TableHeader, TableBody, TableRow, TableCell } from "@/ui/components/table/table";
import { PaginationWithIcon } from "@/ui/components/table/pagination-with-icon";
import { ConfirmModal } from "@/ui/components/modal/confirm-modal";

const PAGE_SIZE = 10;
import { getSession } from "@/auth/utils/auth-session-utils";
import { useDeleteWithConfirm } from "@/hooks/use-delete-with-confirm";
import { Role } from "@/types/auth/role";
import { PAYMENT_METHOD_TYPE_LABELS } from "@/constants/payment-methods/payment-method-labels";
import { usePaymentMethods } from "../hooks/use-payment-methods";
import { useOrgModule } from "../hooks/use-org-module";
import { useBreadcrumb } from "../hooks/use-breadcrumb";
import type { PaymentMethod } from "@/types/payment-methods/payment-method-types";

export const PaymentMethodsPage: React.FC = () => {
  const { orgId, buildOrgPath } = useOrgModule();
  const { build } = useBreadcrumb();
  const navigate = useNavigate();

  const { items, loading, remove } = usePaymentMethods(orgId);
  const [page, setPage] = useState(1);
  const totalPages = Math.max(1, Math.ceil(items.length / PAGE_SIZE));
  const visibleItems = items.slice((page - 1) * PAGE_SIZE, page * PAGE_SIZE);

  const user = getSession();
  const isAdmin = user?.scope === "GLOBAL" || user?.orgs?.[orgId]?.role === Role.ADMIN;

  const { deleting, setDeleting, confirmDelete, deletingInProgress } =
    useDeleteWithConfirm<PaymentMethod>(remove);

  return (
    <>
      <PageMeta title="Métodos de Pago" description="Gestión de métodos de pago de la organización" />
      <ModuleBase
        pageTitle="Métodos de Pago"
        pageIcon={CreditCard}
        breadcrumbItems={build()}
      >
        {loading ? (
          <Loader variant="section" />
        ) : (
          <div className="flex flex-col gap-5">
            {isAdmin && (
              <div className="flex justify-end">
                <button
                  onClick={() => navigate(buildOrgPath("/my-companies/payment-methods/new"))}
                  className="inline-flex items-center gap-2 rounded-lg bg-brand-500 px-4 py-2.5 text-sm font-medium text-white shadow-theme-xs hover:bg-brand-600"
                >
                  <Plus size={16} />
                  Nuevo método
                </button>
              </div>
            )}

            {items.length === 0 ? (
              <EmptyState icon={CreditCard} title="No hay métodos de pago registrados" className="py-12" />
            ) : (
              <div className="overflow-hidden rounded-xl border border-gray-200 dark:border-gray-800">
                <div className="overflow-x-auto">
                  <Table>
                    <TableHeader>
                      <TableRow className="border-b border-gray-200 dark:border-gray-800">
                        {["Nombre", "Tipo", "Banco / Cuenta", "Estado", ...(isAdmin ? [""] : [])].map((h) => (
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
                      {visibleItems.map((item) => (
                        <TableRow
                          key={item.id}
                          className="border-b border-gray-100 last:border-0 dark:border-gray-800"
                        >
                          <TableCell className="px-4 py-3 text-sm font-medium text-gray-800 dark:text-white/90">
                            {item.name}
                          </TableCell>
                          <TableCell className="px-4 py-3 text-sm text-gray-600 dark:text-gray-400">
                            {PAYMENT_METHOD_TYPE_LABELS[item.type] ?? item.type}
                          </TableCell>
                          <TableCell className="px-4 py-3 text-sm text-gray-600 dark:text-gray-400">
                            {item.bankName
                              ? `${item.bankName}${item.accountNumber ? ` · ${item.accountNumber}` : ""}`
                              : "—"}
                          </TableCell>
                          <TableCell className="px-4 py-3">
                            <span
                              className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ${
                                item.isActive
                                  ? "bg-success-50 text-success-700 dark:bg-success-500/10 dark:text-success-400"
                                  : "bg-gray-100 text-gray-500 dark:bg-gray-800 dark:text-gray-400"
                              }`}
                            >
                              {item.isActive ? "Activo" : "Inactivo"}
                            </span>
                          </TableCell>
                          {isAdmin && (
                            <TableCell className="px-4 py-3">
                              <div className="flex items-center gap-2">
                                <button
                                  onClick={() =>
                                    navigate(buildOrgPath(`/my-companies/payment-methods/${item.id}/edit`))
                                  }
                                  className="rounded p-1.5 text-gray-400 hover:bg-gray-100 hover:text-gray-600 dark:hover:bg-gray-800 dark:hover:text-gray-300"
                                >
                                  <Pencil size={14} />
                                </button>
                                <button
                                  onClick={() => setDeleting(item)}
                                  className="rounded p-1.5 text-gray-400 hover:bg-error-50 hover:text-error-500 dark:hover:bg-error-500/10 dark:hover:text-error-400"
                                >
                                  <Trash2 size={14} />
                                </button>
                              </div>
                            </TableCell>
                          )}
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </div>
                <div className="flex flex-col gap-2 border-t border-gray-100 px-4 py-3 dark:border-gray-800 sm:flex-row sm:items-center sm:justify-between">
                  <p className="text-sm text-gray-500 dark:text-gray-400">
                    Mostrando {(page - 1) * PAGE_SIZE + 1}–{Math.min(page * PAGE_SIZE, items.length)} de {items.length}
                  </p>
                  <PaginationWithIcon totalPages={totalPages} initialPage={page} onPageChange={setPage} />
                </div>
              </div>
            )}
          </div>
        )}
      </ModuleBase>

      <ConfirmModal
        isOpen={!!deleting}
        onClose={() => setDeleting(null)}
        onConfirm={confirmDelete}
        title="Eliminar método de pago"
        message={`¿Seguro que deseas eliminar el método de pago "${deleting?.name}"? Esta acción no se puede deshacer.`}
        loading={deletingInProgress}
      />
    </>
  );
};
