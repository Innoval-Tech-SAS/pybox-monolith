import type { ReactNode } from "react";
import { useHasPermission } from "@/auth/hooks/use-has-permission";

interface PermissionGuardProps {
  permission: string;
  orgId?: string;
  children: ReactNode;
  fallback?: ReactNode;
}

export const PermissionGuard: React.FC<PermissionGuardProps> = ({
  permission,
  orgId,
  children,
  fallback = null,
}) => {
  const allowed = useHasPermission(permission, orgId);
  return <>{allowed ? children : fallback}</>;
};
