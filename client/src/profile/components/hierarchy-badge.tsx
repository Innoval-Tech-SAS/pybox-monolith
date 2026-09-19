import { Badge } from "@/ui/components/badge";
import { getRoleHierarchy } from "@/constants/profile/role-hierarchy";

export const HierarchyBadge: React.FC<{ role?: string; scope?: string }> = ({ role, scope }) => {
  const h = getRoleHierarchy(role, scope);
  if (!h) return null;
  return (
    <span title={`Nivel ${h.tier} de 6`}>
      <Badge color={h.badgeColor} size="sm" startIcon={h.icon}>
        {h.label}
      </Badge>
    </span>
  );
};
