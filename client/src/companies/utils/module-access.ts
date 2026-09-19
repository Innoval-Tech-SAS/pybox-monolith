import { getSession } from "@/auth/utils/auth-session-utils";
import type { OrgModule } from "@/types/companies/company-types";

export const filterModules = (
  modules: OrgModule[],
  orgId: string,
  isOrgVerified = false,
): OrgModule[] => {
  const session = getSession();
  if (!session) return [];

  const isGlobal = session.scope === "GLOBAL";
  const orgEntry = session.orgs?.[orgId];
  const isAdmin = isGlobal || orgEntry?.role === "ADMINISTRADOR";
  const permissions = orgEntry?.permissions ?? [];

  return modules.map((mod) => {
    if (mod.requiresVerification && !isOrgVerified) {
      return { ...mod, path: null };
    }
    return mod;
  }).filter((mod) => {
    if (mod.adminOnly) return isAdmin;
    if (mod.requiredPermission) return isAdmin || permissions.includes(mod.requiredPermission);
    return true;
  });
};
