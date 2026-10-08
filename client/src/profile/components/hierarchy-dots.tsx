import { getRoleHierarchy } from "@/constants/profile/role-hierarchy";

export const HierarchyDots: React.FC<{ role?: string; scope?: string }> = ({ role, scope }) => {
  const h = getRoleHierarchy(role, scope);
  if (!h) return null;
  return (
    <div className="flex items-center gap-1.5">
      {Array.from({ length: 6 }, (_, i) => (
        <span
          key={i}
          className={`h-1.5 w-4 rounded-full transition-colors ${
            i < 7 - h.tier ? h.dotClass : "bg-gray-200 dark:bg-gray-700"
          }`}
        />
      ))}
    </div>
  );
};
