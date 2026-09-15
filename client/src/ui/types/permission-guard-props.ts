import type { ReactNode } from "react";

export interface PermissionGuardProps {
  permission: string;
  orgId?: string;
  children: ReactNode;
  fallback?: ReactNode;
}
