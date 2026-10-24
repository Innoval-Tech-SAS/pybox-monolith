import { Badge } from "@/ui/components/badge";
import { getRoleHierarchy } from "@/constants/profile/role-hierarchy";

export const RoleBadge: React.FC<{ role: string; scope: string }> = ({ role, scope }) => {
  const h = getRoleHierarchy(role, scope);
  if (!h) {
    return <Badge color="light" variant="light" size="sm">{scope}</Badge>;
  }
  return (
    <Badge color={h.badgeColor} size="sm" startIcon={h.icon}>
      {h.label}
    </Badge>
  );
};
