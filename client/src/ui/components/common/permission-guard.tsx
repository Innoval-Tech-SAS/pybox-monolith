import type { ReactNode } from "react";
import { useHasPermission } from "@/auth/hooks/use-has-permission";
import type { PermissionGuardProps } from "@/ui/types/permission-guard-props";

export const PermissionGuard: React.FC<PermissionGuardProps> = ({
  permission,
  orgId,
  children,
  fallback = null,
}) => {
  const allowed = useHasPermission(permission, orgId);
  return <>{allowed ? children : fallback}</>;
};
