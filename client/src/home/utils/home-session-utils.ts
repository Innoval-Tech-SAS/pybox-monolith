import type { RoleAssignment, SessionUser } from "@/types/home/home-types";
import { DEFAULT_ROLE_SCOPE } from "@/types/auth/role";

export const DEFAULT_HOME_ROLE = DEFAULT_ROLE_SCOPE.role;
export const DEFAULT_HOME_SCOPE = DEFAULT_ROLE_SCOPE.scope;

export const readSessionUser = (): SessionUser | null => {
  const rawUser = sessionStorage.getItem("user");
  if (!rawUser) return null;

  try {
    return JSON.parse(rawUser) as SessionUser;
  } catch {
    return null;
  }
};

export const getFirstAssignment = (
  user: SessionUser | null,
): RoleAssignment | null => {
  if (!user) return null;
  return user.roles?.[0] ?? user.roleAssignments?.[0] ?? null;
};

export const hasSessionAccess = (
  user: SessionUser | null,
  assignment: RoleAssignment | null,
) =>
  Boolean(
    user?.userRole ||
      user?.userScope ||
      user?.role ||
      user?.scope ||
      assignment,
  );
