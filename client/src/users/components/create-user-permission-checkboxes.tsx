import { useState } from "react";
import { usePermissionsCatalog } from "../hooks/use-permissions-catalog";
import { Loader } from "@/ui/components/loader/loader";
import EmptyState from "@/ui/components/common/empty-state";
import { ShieldOff } from "lucide-react";
import { useUserPermissions } from "../hooks/use-user-permissions";

export const CreateUserPermissionCheckboxes: React.FC<{ orgId: string; userId: string }> = ({ orgId, userId }) => {
  const { catalog, loading } = usePermissionsCatalog();
  const { permissions, assignPermission, removePermission } = useUserPermissions(orgId, userId);
  const [busy, setBusy] = useState<string | null>(null);
  const [localOverride, setLocalOverride] = useState<Set<string> | null>(null);

  const serverGranted = new Set(permissions.filter((p) => p.effect === "OTORGAR").map((p) => p.name));
  const effective = localOverride ?? serverGranted;

  const toggle = async (name: string, checked: boolean) => {
    setBusy(name);
    const base = localOverride ?? serverGranted;
    const next = new Set(base);
    if (checked) {
      next.add(name);
    } else {
      next.delete(name);
    }
    setLocalOverride(next);
    const ok = checked ? await assignPermission(name, "OTORGAR") : await removePermission(name);
    if (!ok) setLocalOverride(base);
    setBusy(null);
  };

  if (loading) return <Loader size="sm" loaderText="Cargando permisos..." />;
  if (catalog.length === 0) return <EmptyState icon={ShieldOff} title="No hay permisos configurados" className="py-4" />;

  return (
    <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 xl:grid-cols-3">
      {catalog.map((perm) => {
        const checked = effective.has(perm.name);
        const isBusy = busy === perm.name;
        return (
          <label
            key={perm.name}
            className="flex items-start gap-3 rounded-lg border border-gray-200 p-3 cursor-pointer hover:bg-gray-50 dark:border-gray-700 dark:hover:bg-white/5"
          >
            <input
              type="checkbox"
              checked={checked}
              disabled={isBusy}
              onChange={(e) => toggle(perm.name, e.target.checked)}
              className="mt-0.5 h-4 w-4 rounded border-gray-300 text-brand-500 focus:ring-brand-500"
            />
            <span>
              <span className="block text-sm font-medium text-gray-800 dark:text-white/90">
                {perm.label ?? perm.name}
              </span>
              {perm.description && (
                <span className="block text-xs text-gray-400 dark:text-gray-500 mt-0.5">
                  {perm.description}
                </span>
              )}
            </span>
          </label>
        );
      })}
    </div>
  );
};
