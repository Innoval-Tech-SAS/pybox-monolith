import { getSession } from "@/auth/utils/auth-session-utils";

export const useHasPermission = (permission: string, orgId?: string): boolean => {
  const session = getSession();
  if (!session) return false;
  if (session.scope === "GLOBAL") return true;
  if (!orgId || !session.orgs) return false;
  const org = session.orgs[orgId];
  if (!org) return false;
  return org.permissions.includes(permission);
};
