import { getSession } from "@/auth/utils/auth-session-utils";
import type { OrgModule } from "@/types/companies/company-types";

export const filterModules = (modules: OrgModule[], orgId: string): OrgModule[] => {
  const session = getSession();
  if (!session) return [];

  const isGlobal = session.scope === "GLOBAL";
  const orgEntry = session.orgs?.[orgId];
  const isAdmin = isGlobal || orgEntry?.role === "ADMINISTRADOR";
  const permissions = orgEntry?.permissions ?? [];

  return modules.filter((mod) => {
    if (mod.adminOnly) return isAdmin;
    if (mod.requiredPermission) return isAdmin || permissions.includes(mod.requiredPermission);
    return true;
  });
};
