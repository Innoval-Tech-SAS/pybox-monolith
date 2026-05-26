import { useState } from "react";
import { useSearchParams, useNavigate } from "react-router";
import { ModuleBase } from "@/ui/components/common/module-base";
import { UsersDataTable } from "../components/users-data-table";
import { Dropdown, DropdownItem } from "@/ui/components/dropdown";
import { useUsers } from "../hooks/use-users";
import { useUpdateUser } from "../hooks/use-update-user";
import { useDeleteUser } from "../hooks/use-delete-user";
import { getSession } from "@/auth/utils/auth-session-utils";

type RoleOption = { label: string; role: string };

const GLOBAL_ADMIN_OPTIONS: RoleOption[] = [
  { label: "Administrador", role: "ADMINISTRADOR" },
  { label: "Atención al cliente", role: "ATENCION AL CLIENTE" },
];

const ORG_ADMIN_OPTIONS: RoleOption[] = [
  { label: "Atención al cliente", role: "ATENCION AL CLIENTE" },
  { label: "Usuario", role: "USUARIO ORGANIZACIÓN" },
];

const AddUserButton: React.FC<{ orgId: string | undefined }> = ({ orgId }) => {
  const [open, setOpen] = useState(false);
  const navigate = useNavigate();

  const session = getSession();
  const sessionRole = session?.role ?? null;
  const sessionScope = session?.scope ?? null;
  const orgs = (session?.orgs ?? {}) as Record<string, { role: string }>;

  // Global admin: top-level role is set
  const isGlobalAdmin =
    sessionRole === "ADMINISTRADOR" && sessionScope === "GLOBAL";

  // Org admin: role is null at top level but inside orgs[id].role
  const adminOrgId = orgId
    ? orgs[orgId]?.role === "ADMINISTRADOR"
      ? orgId
      : null
    : (Object.entries(orgs).find(
        ([, entry]) => entry.role === "ADMINISTRADOR",
      )?.[0] ?? null);
  const isOrgAdmin = sessionScope === "ORGANIZATION" && !!adminOrgId;

  if (!isGlobalAdmin && (!isOrgAdmin || !orgId)) return null;

  const options = isGlobalAdmin ? GLOBAL_ADMIN_OPTIONS : ORG_ADMIN_OPTIONS;
  const targetOrgId = isOrgAdmin ? adminOrgId : null;

  const handleSelect = (roleValue: string) => {
    setOpen(false);
    const search = targetOrgId ? `?org=${targetOrgId}` : "";
    navigate(`/my-users/add${search}`, { state: { role: roleValue } });
  };

  return (
    <div className="relative">
      <button
        onClick={() => setOpen((v) => !v)}
        className="dropdown-toggle inline-flex items-center gap-2 rounded-lg bg-brand-500 px-4 py-2.5 text-sm font-medium text-white shadow-theme-xs hover:bg-brand-600"
      >
        <svg
          width="16"
          height="16"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          strokeWidth="2"
        >
          <line x1="12" y1="5" x2="12" y2="19" />
          <line x1="5" y1="12" x2="19" y2="12" />
        </svg>
        Nuevo usuario
        <svg
          width="12"
          height="12"
          viewBox="0 0 16 16"
          fill="none"
          stroke="currentColor"
          strokeWidth="2"
        >
          <path
            d="M3.8 5.9L8 10.1l4.2-4.2"
            strokeLinecap="round"
            strokeLinejoin="round"
          />
        </svg>
      </button>
      <Dropdown isOpen={open} onClose={() => setOpen(false)}>
        <ul className="flex flex-col gap-0.5 p-2">
          {options.map((opt) => (
            <li key={opt.role}>
              <DropdownItem onClick={() => handleSelect(opt.role)}>
                {opt.label}
              </DropdownItem>
            </li>
          ))}
        </ul>
      </Dropdown>
    </div>
  );
};

export const UsersPage: React.FC = () => {
  const [searchParams] = useSearchParams();
  const orgId = searchParams.get("org") ?? undefined;
  const { users, setUsers, loading, refetch } = useUsers(orgId);
  const { updateUser } = useUpdateUser();
  const { deleteUser } = useDeleteUser();

  const handleToggleStatus = async (userId: number, isActive: boolean) => {
    setUsers((prev) =>
      prev.map((u) => (u.id === userId ? { ...u, isActive } : u)),
    );
    const result = await updateUser(userId, { isActive });
    if (!result) {
      setUsers((prev) =>
        prev.map((u) => (u.id === userId ? { ...u, isActive: !isActive } : u)),
      );
    }
  };

  const handleDelete = async (userId: number) => {
    const ok = await deleteUser(userId);
    if (ok) refetch();
  };

  return (
    <ModuleBase
      pageTitle={"Usuarios"}
      breadcrumbItems={[{ label: "Inicio", path: "/home" }]}
    >
      <div className="flex justify-end mb-4">
        <AddUserButton orgId={orgId} />
      </div>
      <UsersDataTable
        users={users}
        loading={loading}
        orgId={orgId}
        onToggleStatus={handleToggleStatus}
        onDelete={handleDelete}
      />
    </ModuleBase>
  );
};
