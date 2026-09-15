import { useRef, useState } from "react";
import { useNavigate } from "react-router";
import { Plus, ChevronDown } from "lucide-react";
import { Dropdown } from "@/ui/components/dropdown/dropdown";
import { DropdownItem } from "@/ui/components/dropdown/dropdown-item";
import { getSession } from "@/auth/utils/auth-session-utils";
import { GLOBAL_ADMIN_ROLE_OPTIONS, ORG_ADMIN_ROLE_OPTIONS } from "../constants/add-user-role-options";
import type { AddUserButtonProps } from "../types/props/add-user-button-props";

export const AddUserButton: React.FC<AddUserButtonProps> = ({ orgId }) => {
  const [open, setOpen] = useState(false);
  const navigate = useNavigate();
  const triggerRef = useRef<HTMLButtonElement>(null);

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
  const isOrgAdmin = sessionScope === "ORGANIZACION" && !!adminOrgId;

  if (!isGlobalAdmin && (!isOrgAdmin || !orgId)) return null;

  const options = isGlobalAdmin ? GLOBAL_ADMIN_ROLE_OPTIONS : ORG_ADMIN_ROLE_OPTIONS;
  const targetOrgId = isOrgAdmin ? adminOrgId : null;

  const handleSelect = (roleValue: string) => {
    setOpen(false);
    const search = targetOrgId ? `?org=${targetOrgId}` : "";
    navigate(`/my-users/add${search}`, { state: { role: roleValue } });
  };

  return (
    <div className="relative">
      <button
        ref={triggerRef}
        type="button"
        onClick={() => setOpen((v) => !v)}
        aria-haspopup="true"
        aria-expanded={open}
        className="dropdown-toggle inline-flex items-center gap-2 rounded-lg bg-brand-500 px-4 py-2.5 text-sm font-medium text-white shadow-theme-xs hover:bg-brand-600"
      >
        <Plus size={16} />
        Nuevo usuario
        <ChevronDown size={12} />
      </button>
      <Dropdown isOpen={open} onClose={() => setOpen(false)} triggerRef={triggerRef}>
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
