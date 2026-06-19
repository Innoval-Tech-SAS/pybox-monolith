import type { RoleAssignment, SessionUser } from "@/types/home/home-types";

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
