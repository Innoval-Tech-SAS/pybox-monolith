import { useMemo, useState } from "react";
import { useNavigate } from "react-router";
import { Table, TableBody, TableCell, TableHeader, TableRow } from "@/ui/components/table";
import { PaginationWithIcon } from "@/ui/components/table/pagination-with-icon";
import { Badge } from "@/ui/components/badge";
import { Switch } from "@/ui/components/switch";
import type { SortKey, SortOrder, UsersDataTableProps } from "@/types/props/users-data-table-props";

const SortIcon = ({ active, order }: { active: boolean; order: SortOrder }) => (
  <button className="flex flex-col gap-0.5">
    <svg className={active && order === "asc" ? "text-brand-500" : "text-gray-300 dark:text-gray-700"} width="8" height="5" viewBox="0 0 8 5" fill="none">
      <path d="M4.40962 0.585167C4.21057 0.300808 3.78943 0.300807 3.59038 0.585166L1.05071 4.21327C0.81874 4.54466 1.05582 5 1.46033 5H6.53967C6.94418 5 7.18126 4.54466 6.94929 4.21327L4.40962 0.585167Z" fill="currentColor" />
    </svg>
    <svg className={active && order === "desc" ? "text-brand-500" : "text-gray-300 dark:text-gray-700"} width="8" height="5" viewBox="0 0 8 5" fill="none">
      <path d="M4.40962 4.41483C4.21057 4.69919 3.78943 4.69919 3.59038 4.41483L1.05071 0.786732C0.81874 0.455343 1.05582 0 1.46033 0H6.53967C6.94418 0 7.18126 0.455342 6.94929 0.786731L4.40962 4.41483Z" fill="currentColor" />
    </svg>
  </button>
);

// Inline action icon buttons
type IconBtnVariant = "default" | "warning" | "primary" | "success" | "error";

const ICON_BTN_VARIANTS: Record<IconBtnVariant, string> = {
  default: "text-gray-400 hover:bg-gray-100 hover:text-gray-700 dark:text-gray-500 dark:hover:bg-white/8 dark:hover:text-gray-300",
  warning: "text-gray-400 hover:bg-warning-50 hover:text-warning-600 dark:text-gray-500 dark:hover:bg-warning-500/10 dark:hover:text-warning-400",
  primary: "text-gray-400 hover:bg-brand-50 hover:text-brand-600 dark:text-gray-500 dark:hover:bg-brand-500/10 dark:hover:text-brand-400",
  success: "text-gray-400 hover:bg-success-50 hover:text-success-600 dark:text-gray-500 dark:hover:bg-success-500/10 dark:hover:text-success-400",
  error:   "text-gray-400 hover:bg-error-50 hover:text-error-600 dark:text-gray-500 dark:hover:bg-error-500/10 dark:hover:text-error-400",
};

const IconBtn = ({ onClick, title, variant = "default", children }: { onClick: () => void; title: string; variant?: IconBtnVariant; children: React.ReactNode }) => (
  <button
    type="button"
    title={title}
    onClick={onClick}
    className={`rounded-lg p-1.5 transition-all ${ICON_BTN_VARIANTS[variant]}`}
  >
    {children}
  </button>
);

const EyeIcon = () => (
  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
    <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/>
    <circle cx="12" cy="12" r="3"/>
  </svg>
);

const PencilIcon = () => (
  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
    <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/>
    <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/>
  </svg>
);

const SettingsIcon = () => (
  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
    <circle cx="12" cy="12" r="3"/>
    <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1-2.83 2.83l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-4 0v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83-2.83l.06-.06A1.65 1.65 0 0 0 4.68 15a1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1 0-4h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 2.83-2.83l.06.06A1.65 1.65 0 0 0 9 4.68a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 4 0v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 2.83l-.06.06A1.65 1.65 0 0 0 19.4 9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 0 4h-.09a1.65 1.65 0 0 0-1.51 1z"/>
  </svg>
);

const TrashIcon = () => (
  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
    <polyline points="3 6 5 6 21 6"/>
    <path d="M19 6l-1 14a2 2 0 0 1-2 2H8a2 2 0 0 1-2-2L5 6"/>
    <path d="M10 11v6M14 11v6"/>
    <path d="M9 6V4a1 1 0 0 1 1-1h4a1 1 0 0 1 1 1v2"/>
  </svg>
);


const ROLE_DISPLAY: Record<string, string> = {
  ADMINISTRADOR: "Administrador",
  "ATENCION AL CLIENTE": "Atención al cliente",
  "USUARIO ORGANIZACIÓN": "Usuario",
  USUARIO: "Usuario",
};

export const UsersDataTable: React.FC<UsersDataTableProps> = ({
  users,
  loading,
  orgId,
  onToggleStatus,
  onDelete,
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

  const sortableColumns: { key: SortKey; label: string }[] = [
    { key: "fullName", label: "Usuario" },
    { key: "createdAt", label: "Registro" },
  ];

  const formatDate = (iso: string | null) =>
    iso ? new Date(iso).toLocaleDateString("es-CO", { day: "2-digit", month: "short", year: "numeric" }) : "—";

  return (
    <div className="overflow-hidden rounded-xl bg-white dark:bg-white/3">

      {/* Toolbar */}
      <div className="flex flex-col gap-2 px-4 py-4 border border-b-0 border-gray-100 dark:border-white/5 rounded-t-xl sm:flex-row sm:items-center sm:justify-between">
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

      {/* Table */}
      <div className="max-w-full overflow-x-auto custom-scrollbar">
        <Table>
          <TableHeader>
            <TableRow>
              <TableCell isHeader className="px-4 py-3 border border-gray-100 dark:border-white/5">
                <div className="flex items-center justify-between cursor-pointer" onClick={() => handleSort("fullName")}>
                  <p className="font-medium text-gray-700 text-theme-xs dark:text-gray-400">Usuario</p>
                  <SortIcon active={sortKey === "fullName"} order={sortOrder} />
                </div>
              </TableCell>
              <TableCell isHeader className="px-4 py-3 border border-gray-100 dark:border-white/5 text-center">
                <p className="font-medium text-gray-700 text-theme-xs dark:text-gray-400">Entidad</p>
              </TableCell>
              <TableCell isHeader className="px-4 py-3 border border-gray-100 dark:border-white/5">
                <div className="flex items-center justify-between cursor-pointer" onClick={() => handleSort("createdAt")}>
                  <p className="font-medium text-gray-700 text-theme-xs dark:text-gray-400">Registro</p>
                  <SortIcon active={sortKey === "createdAt"} order={sortOrder} />
                </div>
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
                <TableCell className="px-4 py-8 text-center text-gray-400 text-theme-sm" colSpan={7}>
                  Cargando...
                </TableCell>
              </TableRow>
            ) : currentData.length === 0 ? (
              <TableRow>
                <TableCell className="px-4 py-8 text-center text-gray-400 text-theme-sm" colSpan={7}>
                  No hay usuarios.
                </TableCell>
              </TableRow>
            ) : (
              currentData.map((user) => {
                const isUserOrg = user.roles.some((r) => r.role === "USUARIO ORGANIZACIÓN");
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
                      />
                      </div>
                    </TableCell>
                    {/* Acciones */}
                    <TableCell className="px-4 py-4 border border-gray-100 dark:border-white/5">
                      <div className="flex items-center justify-center gap-0.5">
                        <IconBtn title="Ver perfil" variant="default" onClick={() => navigate(`/my-users/${user.id}`)}>
                          <EyeIcon />
                        </IconBtn>
                        <IconBtn title="Editar" variant="warning" onClick={() => navigate(`/my-users/${user.id}/edit`)}>
                          <PencilIcon />
                        </IconBtn>
                        {isUserOrg && (
                          <IconBtn title="Configuración" variant="primary" onClick={() => navigate(settingsPath)}>
                            <SettingsIcon />
                          </IconBtn>
                        )}
                        <IconBtn
                          title="Eliminar"
                          variant="error"
                          onClick={() => {
                            if (window.confirm("¿Eliminar este usuario?")) onDelete(user.id);
                          }}
                        >
                          <TrashIcon />
                        </IconBtn>
                      </div>
                    </TableCell>
                  </TableRow>
                );
              })
            )}
          </TableBody>
        </Table>
      </div>

      {/* Footer */}
      <div className="border border-t-0 rounded-b-xl border-gray-100 py-4 pl-4.5 pr-4 dark:border-white/5">
        <div className="flex flex-col xl:flex-row xl:items-center xl:justify-between">
          <p className="pb-3 text-sm font-medium text-center text-gray-500 border-b border-gray-100 dark:border-gray-800 dark:text-gray-400 xl:border-b-0 xl:pb-0 xl:text-left">
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
