import { getSession } from "@/auth/utils/auth-session-utils";

export const useHasAnyPermission = (permission: string): boolean => {
  const session = getSession();
  if (!session) return false;
  if (session.scope === "GLOBAL") return true;
  if (!session.orgs) return false;
  return Object.values(session.orgs).some((org) => org.permissions.includes(permission));
};
