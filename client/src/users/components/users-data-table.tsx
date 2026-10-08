import { useMemo, useState } from "react";
import { useNavigate } from "react-router";
import { Eye, Pencil, RotateCcw, Settings, Trash2, Users } from "lucide-react";
import EmptyState from "@/ui/components/common/empty-state";
import { Table, TableBody, TableCell, TableHeader, TableRow } from "@/ui/components/table/table";
import { PaginationWithIcon } from "@/ui/components/table/pagination-with-icon";
import { Badge } from "@/ui/components/badge";
import { Switch } from "@/ui/components/switch";
import { SortIcon } from "./sort-icon";
import { IconBtn } from "./icon-btn";
import { ROLE_DISPLAY } from "../constants/user-role-display";
import { formatShortDate as formatDate } from "@/profile/utils/format-date";
import { Loader } from "@/ui/components/loader/loader";
import type { SortKey, SortOrder, UsersDataTableProps } from "@/types/props/users-data-table-props";

export const UsersDataTable: React.FC<UsersDataTableProps> = ({
  users,
  loading,
  orgId,
  onToggleStatus,
  onDelete,
  onRestore,
}) => {
  const navigate = useNavigate();
  const [currentPage, setCurrentPage] = useState(1);
  const [itemsPerPage, setItemsPerPage] = useState(10);
  const [sortKey, setSortKey] = useState<SortKey>("fullName");
  const [sortOrder, setSortOrder] = useState<SortOrder>("asc");
  const [searchTerm, setSearchTerm] = useState("");

  const handleSort = (key: SortKey) => {
    setSortKey(key);
    setSortOrder(sortKey === key && sortOrder === "asc" ? "desc" : "asc");
  };

  const filteredAndSorted = useMemo(() =>
    users
      .filter((u) =>
        u.fullName.toLowerCase().includes(searchTerm.toLowerCase()) ||
        u.email.toLowerCase().includes(searchTerm.toLowerCase()) ||
        u.roles.some((r) => r.role.toLowerCase().includes(searchTerm.toLowerCase()))
      )
      .sort((a, b) => {
        const va = a[sortKey] ?? "";
        const vb = b[sortKey] ?? "";
        return sortOrder === "asc"
          ? String(va).localeCompare(String(vb))
          : String(vb).localeCompare(String(va));
      }),
    [users, searchTerm, sortKey, sortOrder]
  );

  const totalItems = filteredAndSorted.length;
  const totalPages = Math.max(1, Math.ceil(totalItems / itemsPerPage));
  const startIndex = (currentPage - 1) * itemsPerPage;
  const currentData = filteredAndSorted.slice(startIndex, startIndex + itemsPerPage);

  return (
    <div className="flex flex-1 min-h-0 flex-col overflow-hidden rounded-xl bg-white dark:bg-white/3">

      {/* Toolbar */}
      <div className="shrink-0 flex flex-col gap-2 px-4 py-4 border border-b-0 border-gray-100 dark:border-white/5 rounded-t-xl sm:flex-row sm:items-center sm:justify-between">
        <div className="flex items-center gap-3">
          <span className="text-gray-500 dark:text-gray-400">Mostrar</span>
          <div className="relative z-20">
            <select
              className="w-full py-2 pl-3 pr-8 text-sm text-gray-800 bg-transparent border border-gray-300 rounded-lg appearance-none h-9 shadow-theme-xs focus:border-brand-300 focus:outline-hidden focus:ring-3 focus:ring-brand-500/10 dark:border-gray-700 dark:bg-gray-900 dark:text-white/90"
              value={itemsPerPage}
              onChange={(e) => { setItemsPerPage(Number(e.target.value)); setCurrentPage(1); }}
            >
              {[5, 10, 25].map((v) => <option key={v} value={v}>{v}</option>)}
            </select>
            <span className="absolute z-30 text-gray-500 -translate-y-1/2 right-2 top-1/2">
              <svg className="stroke-current" width="16" height="16" viewBox="0 0 16 16" fill="none">
                <path d="M3.8335 5.9165L8.00016 10.0832L12.1668 5.9165" strokeWidth="1.2" strokeLinecap="round" strokeLinejoin="round" />
              </svg>
            </span>
          </div>
          <span className="text-gray-500 dark:text-gray-400">entradas</span>
        </div>
        <div className="relative">
          <span className="absolute text-gray-500 -translate-y-1/2 pointer-events-none left-4 top-1/2">
            <svg className="fill-current" width="20" height="20" viewBox="0 0 20 20" fill="none">
              <path fillRule="evenodd" clipRule="evenodd" d="M3.04199 9.37363C3.04199 5.87693 5.87735 3.04199 9.37533 3.04199C12.8733 3.04199 15.7087 5.87693 15.7087 9.37363C15.7087 12.8703 12.8733 15.7053 9.37533 15.7053C5.87735 15.7053 3.04199 12.8703 3.04199 9.37363ZM9.37533 1.54199C5.04926 1.54199 1.54199 5.04817 1.54199 9.37363C1.54199 13.6991 5.04926 17.2053 9.37533 17.2053C11.2676 17.2053 13.0032 16.5344 14.3572 15.4176L17.1773 18.238C17.4702 18.5309 17.945 18.5309 18.2379 18.238C18.5308 17.9451 18.5309 17.4703 18.238 17.1773L15.4182 14.3573C16.5367 13.0033 17.2087 11.2669 17.2087 9.37363C17.2087 5.04817 13.7014 1.54199 9.37533 1.54199Z" />
            </svg>
          </span>
          <input
            type="text"
            value={searchTerm}
            onChange={(e) => { setSearchTerm(e.target.value); setCurrentPage(1); }}
            placeholder="Buscar..."
            className="h-11 w-full rounded-lg border border-gray-300 bg-transparent py-2.5 pl-11 pr-4 text-sm text-gray-800 shadow-theme-xs placeholder:text-gray-400 focus:border-brand-300 focus:outline-hidden focus:ring-3 focus:ring-brand-500/10 dark:border-gray-700 dark:bg-gray-900 dark:text-white/90 xl:w-75"
          />
        </div>
      </div>

      {/* Desktop table */}
      <div className="hidden max-w-full flex-1 min-h-0 overflow-auto custom-scrollbar sm:block">
        <Table>
          <TableHeader>
            <TableRow>
              <TableCell isHeader className="px-4 py-3 border border-gray-100 dark:border-white/5">
                <button
                  type="button"
                  onClick={() => handleSort("fullName")}
                  className="flex w-full items-center justify-between"
                >
                  <p className="font-medium text-gray-700 text-theme-xs dark:text-gray-400">Usuario</p>
                  <SortIcon active={sortKey === "fullName"} order={sortOrder} />
                </button>
              </TableCell>
              <TableCell isHeader className="px-4 py-3 border border-gray-100 dark:border-white/5 text-center">
                <p className="font-medium text-gray-700 text-theme-xs dark:text-gray-400">Entidad</p>
              </TableCell>
              <TableCell isHeader className="px-4 py-3 border border-gray-100 dark:border-white/5">
                <button
                  type="button"
                  onClick={() => handleSort("createdAt")}
                  className="flex w-full items-center justify-between"
                >
                  <p className="font-medium text-gray-700 text-theme-xs dark:text-gray-400">Registro</p>
                  <SortIcon active={sortKey === "createdAt"} order={sortOrder} />
                </button>
              </TableCell>
              <TableCell isHeader className="px-4 py-3 border border-gray-100 dark:border-white/5">
                <p className="font-medium text-gray-700 text-theme-xs dark:text-gray-400">Teléfono</p>
              </TableCell>
              <TableCell isHeader className="px-4 py-3 border border-gray-100 dark:border-white/5 text-center">
                <p className="font-medium text-gray-700 text-theme-xs dark:text-gray-400">Rol</p>
              </TableCell>
              <TableCell isHeader className="px-4 py-3 border border-gray-100 dark:border-white/5 text-center">
                <p className="font-medium text-gray-700 text-theme-xs dark:text-gray-400">Estado</p>
              </TableCell>
              <TableCell isHeader className="px-4 py-3 border border-gray-100 dark:border-white/5 text-center">
                <p className="font-medium text-gray-700 text-theme-xs dark:text-gray-400">Acciones</p>
              </TableCell>
            </TableRow>
          </TableHeader>
          <TableBody>
            {loading ? (
              <TableRow>
                <TableCell className="px-4 py-8 text-center" colSpan={7}>
                  <Loader size="sm" loaderText="Cargando usuarios..." />
                </TableCell>
              </TableRow>
            ) : currentData.length === 0 ? (
              <TableRow>
                <TableCell className="px-4 py-8 text-center" colSpan={7}>
                  <EmptyState icon={Users} title="No hay usuarios" />
                </TableCell>
              </TableRow>
            ) : (
              currentData.map((user) => {
                const isUserOrg = user.roles.some((r) => r.role === "USUARIO" && r.scope === "ORGANIZACION");
                const settingsPath = orgId
                  ? `/my-users/${user.id}/settings?org=${orgId}`
                  : `/my-users/${user.id}/settings`;
                return (
                  <TableRow key={user.id}>
                    {/* Usuario */}
                    <TableCell className="px-4 py-4 border border-gray-100 dark:border-white/5 whitespace-nowrap">
                      <p className="font-medium text-gray-800 text-theme-sm dark:text-white/90">{user.fullName}</p>
                    </TableCell>
                    {/* Entidad */}
                    <TableCell className="px-4 py-4 font-normal text-gray-600 dark:text-gray-400 border border-gray-100 dark:border-white/5 text-theme-sm whitespace-nowrap text-center">
                      {user.roles[0]?.orgName ?? "—"}
                    </TableCell>
                    {/* Registro */}
                    <TableCell className="px-4 py-4 font-normal text-gray-500 dark:text-gray-400 border border-gray-100 dark:border-white/5 text-theme-sm whitespace-nowrap">
                      {formatDate(user.createdAt)}
                    </TableCell>
                    {/* Teléfono */}
                    <TableCell className="px-4 py-4 font-normal text-gray-500 dark:text-gray-400 border border-gray-100 dark:border-white/5 text-theme-sm whitespace-nowrap">
                      {user.phoneNumber ?? "—"}
                    </TableCell>
                    {/* Rol */}
                    <TableCell className="px-4 py-4 border border-gray-100 dark:border-white/5 whitespace-nowrap text-center">
                      {user.roles.length > 0 ? (
                        <Badge size="sm" color="primary" variant="light">
                          {ROLE_DISPLAY[user.roles[0].role] ?? user.roles[0].role}
                        </Badge>
                      ) : (
                        <Badge size="sm" color="light" variant="light">Sin rol</Badge>
                      )}
                    </TableCell>
                    {/* Estado */}
                    <TableCell className="px-4 py-4 border border-gray-100 dark:border-white/5 text-center">
                      <div className="flex justify-center">
                      <Switch
                        checked={user.isActive}
                        onChange={(checked) => onToggleStatus(user.id, checked)}
                        ariaLabel={`Estado de ${user.fullName}: ${user.isActive ? "activo" : "inactivo"}`}
                      />
                      </div>
                    </TableCell>
                    {/* Acciones */}
                    <TableCell className="px-4 py-4 border border-gray-100 dark:border-white/5">
                      <div className="flex items-center justify-center gap-0.5">
                        {user.deletedAt ? (
                          onRestore && (
                            <IconBtn title="Restaurar" variant="primary" onClick={() => onRestore(user)}>
                              <RotateCcw size={18} />
                            </IconBtn>
                          )
                        ) : (
                          <>
                            <IconBtn title="Ver perfil" variant="default" onClick={() => navigate(`/my-users/${user.id}`)}>
                              <Eye size={18} />
                            </IconBtn>
                            <IconBtn title="Editar" variant="warning" onClick={() => navigate(`/my-users/${user.id}/edit`)}>
                              <Pencil size={18} />
                            </IconBtn>
                            {isUserOrg && (
                              <IconBtn title="Configuración" variant="primary" onClick={() => navigate(settingsPath)}>
                                <Settings size={18} />
                              </IconBtn>
                            )}
                            <IconBtn
                              title="Eliminar"
                              variant="error"
                              onClick={() => onDelete(user)}
                            >
                              <Trash2 size={18} />
                            </IconBtn>
                          </>
                        )}
                      </div>
                    </TableCell>
                  </TableRow>
                );
              })
            )}
          </TableBody>
        </Table>
      </div>

      {/* Mobile cards */}
      <div className="flex flex-1 min-h-0 flex-col gap-3 overflow-y-auto p-4 sm:hidden">
        {loading ? (
          <div className="py-10"><Loader size="sm" loaderText="Cargando usuarios..." /></div>
        ) : currentData.length === 0 ? (
          <EmptyState icon={Users} title="No hay usuarios" className="py-10" />
        ) : (
          currentData.map((user) => {
            const isUserOrg = user.roles.some((r) => r.role === "USUARIO" && r.scope === "ORGANIZACION");
            const settingsPath = orgId
              ? `/my-users/${user.id}/settings?org=${orgId}`
              : `/my-users/${user.id}/settings`;
            return (
              <div
                key={user.id}
                className="w-full rounded-2xl border border-gray-200 bg-white p-4 dark:border-gray-800 dark:bg-gray-900"
              >
                <div className="flex items-start justify-between gap-2">
                  <div className="min-w-0">
                    <p className="font-medium text-gray-800 dark:text-white/90">{user.fullName}</p>
                    <p className="mt-0.5 truncate text-xs text-gray-400">{user.roles[0]?.orgName ?? "—"}</p>
                  </div>
                  {user.roles.length > 0 ? (
                    <Badge size="sm" color="primary" variant="light">
                      {ROLE_DISPLAY[user.roles[0].role] ?? user.roles[0].role}
                    </Badge>
                  ) : (
                    <Badge size="sm" color="light" variant="light">Sin rol</Badge>
                  )}
                </div>

                <p className="mt-2 text-xs text-gray-400">
                  {formatDate(user.createdAt)} · {user.phoneNumber ?? "—"}
                </p>

                <div className="mt-3 flex items-center justify-between gap-2 border-t border-gray-100 pt-3 dark:border-gray-800">
                  <Switch
                    checked={user.isActive}
                    onChange={(checked) => onToggleStatus(user.id, checked)}
                    label={user.isActive ? "Activo" : "Inactivo"}
                  />
                  <div className="flex items-center gap-0.5">
                    {user.deletedAt ? (
                      onRestore && (
                        <IconBtn title="Restaurar" variant="primary" onClick={() => onRestore(user)}>
                          <RotateCcw size={18} />
                        </IconBtn>
                      )
                    ) : (
                      <>
                        <IconBtn title="Ver perfil" variant="default" onClick={() => navigate(`/my-users/${user.id}`)}>
                          <Eye size={18} />
                        </IconBtn>
                        <IconBtn title="Editar" variant="warning" onClick={() => navigate(`/my-users/${user.id}/edit`)}>
                          <Pencil size={18} />
                        </IconBtn>
                        {isUserOrg && (
                          <IconBtn title="Configuración" variant="primary" onClick={() => navigate(settingsPath)}>
                            <Settings size={18} />
                          </IconBtn>
                        )}
                        <IconBtn title="Eliminar" variant="error" onClick={() => onDelete(user)}>
                          <Trash2 size={18} />
                        </IconBtn>
                      </>
                    )}
                  </div>
                </div>
              </div>
            );
          })
        )}
      </div>

      {/* Footer */}
      <div className="shrink-0 border border-t-0 rounded-b-xl border-gray-100 py-4 pl-4.5 pr-4 dark:border-white/5">
        <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
          <p className="pb-3 text-sm font-medium text-center text-gray-500 border-b border-gray-100 dark:border-gray-800 dark:text-gray-400 sm:border-b-0 sm:pb-0 sm:text-left">
            {totalItems === 0
              ? "Sin resultados"
              : `Mostrando ${startIndex + 1}–${Math.min(startIndex + itemsPerPage, totalItems)} de ${totalItems}`}
          </p>
          <PaginationWithIcon totalPages={totalPages} initialPage={currentPage} onPageChange={setCurrentPage} />
        </div>
      </div>

    </div>
  );
};
