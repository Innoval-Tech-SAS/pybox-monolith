import { useMemo } from "react";
import { getSession } from "@/auth/utils/auth-session-utils";
import { Role, Scope } from "@/types/auth/role";
import type { SupportTicketStatus } from "@/types/support/support-types";

const _STAFF_ROLES = new Set<string>([Role.ADMIN, Role.CS]);

export interface TicketPermissions {
  canCreate: boolean;
  canResolve: boolean;
  canEscalate: boolean;
  canAssign: boolean;
  canMoveStatus: boolean;
}

export const useTicketPermissions = (status?: SupportTicketStatus): TicketPermissions => {
  return useMemo(() => {
    const session = getSession();
    if (!session) {
      return { canCreate: false, canResolve: false, canEscalate: false, canAssign: false, canMoveStatus: false };
    }

    const scope = session.scope;
    const role = session.role;
    const orgRoles = Object.values(session.orgs ?? {}).map((o) => o.role);
    const isResolved = status === "resolved";

    if (scope === Scope.GLOBAL) {
      const isStaff = role === Role.ADMIN || role === Role.CS;
      return {
        canCreate: true,
        canResolve: isStaff && !isResolved,
        canEscalate: !isResolved,
        canAssign: role === Role.ADMIN,
        canMoveStatus: isStaff && !isResolved,
      };
    }

    if (scope === Scope.ORG) {
      const hasStaff = orgRoles.some((r) => _STAFF_ROLES.has(r));
      const hasAdmin = orgRoles.includes(Role.ADMIN);
      const hasCS = orgRoles.includes(Role.CS);
      return {
        canCreate: true,
        canResolve: hasCS && !isResolved,
        canEscalate: hasCS && !isResolved,
        canAssign: (hasAdmin || hasCS) && !isResolved,
        canMoveStatus: hasStaff && !isResolved,
      };
    }

    return { canCreate: true, canResolve: false, canEscalate: false, canAssign: false, canMoveStatus: false };
  }, [status]);
};
