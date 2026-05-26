import { useState } from "react";
import { useNavigate, useParams, useSearchParams } from "react-router";
import { ModuleBase } from "@/ui/components/common/module-base";
import { Card, CardTitle } from "@/ui/components/card";
import { usePermissionsCatalog } from "../hooks/use-permissions-catalog";
import { useUserPermissions } from "../hooks/use-user-permissions";

const PermissionToggle: React.FC<{
  name: string;
  label: string | null;
  description: string | null;
  granted: boolean;
  onToggle: (checked: boolean) => Promise<void>;
}> = ({ name, label, description, granted, onToggle }) => {
  const [busy, setBusy] = useState(false);

  const handleChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    setBusy(true);
    await onToggle(e.target.checked);
    setBusy(false);
  };

  return (
    <label className="flex items-start justify-between gap-4 rounded-lg border border-gray-200 p-4 dark:border-gray-700">
      <span>
        <span className="block text-sm font-medium text-gray-800 dark:text-white/90">
          {label ?? name}
        </span>
        <span className="block text-xs text-gray-500 dark:text-gray-400 mt-0.5">
          {name}
        </span>
        {description && (
          <span className="block text-xs text-gray-400 dark:text-gray-500 mt-0.5">
            {description}
          </span>
        )}
      </span>
      <div className="flex items-center gap-2 shrink-0">
        {busy && (
          <span className="h-4 w-4 animate-spin rounded-full border-2 border-brand-500 border-t-transparent" />
        )}
        <input
          type="checkbox"
          checked={granted}
          disabled={busy}
          onChange={handleChange}
          className="h-4 w-4 rounded border-gray-300 text-brand-500 focus:ring-brand-500"
        />
      </div>
    </label>
  );
};

export const UserSettingsPage: React.FC = () => {
  const navigate = useNavigate();
  const { id } = useParams<{ id: string }>();
  const [searchParams] = useSearchParams();
  const orgId = searchParams.get("org") ?? "";
  const userId = Number(id);

  const { catalog, loading: catalogLoading } = usePermissionsCatalog();
  const { permissions, loading: permsLoading, assignPermission, removePermission } = useUserPermissions(orgId, userId);

  const backPath = orgId ? `/my-companies/users?org=${orgId}` : "/my-users";
  const loading = catalogLoading || permsLoading;

  const grantedSet = new Set(
    permissions.filter((p) => p.effect === "GRANT").map((p) => p.name)
  );

  const handleToggle = async (permName: string, checked: boolean) => {
    if (checked) {
      await assignPermission(permName, "GRANT");
    } else {
      await removePermission(permName);
    }
  };

  return (
    <ModuleBase
      pageTitle="Configuración de permisos"
      breadcrumbItems={[{ label: "Usuarios", path: backPath }]}
    >
      <div className="max-w-2xl">
        <Card>
          <CardTitle>Permisos del usuario</CardTitle>
          <p className="mb-5 text-sm text-gray-500 dark:text-gray-400">
            Activa o desactiva el acceso a cada módulo para este usuario.
          </p>

          {loading ? (
            <p className="text-sm text-gray-400">Cargando...</p>
          ) : catalog.length === 0 ? (
            <p className="text-sm text-gray-400">No hay permisos disponibles.</p>
          ) : (
            <div className="flex flex-col gap-3">
              {catalog.map((perm) => (
                <PermissionToggle
                  key={perm.name}
                  name={perm.name}
                  label={perm.label}
                  description={perm.description}
                  granted={grantedSet.has(perm.name)}
                  onToggle={(checked) => handleToggle(perm.name, checked)}
                />
              ))}
            </div>
          )}

          <div className="flex justify-end mt-6 pt-5 border-t border-gray-100 dark:border-gray-800">
            <button
              type="button"
              onClick={() => navigate(backPath)}
              className="rounded-lg bg-brand-500 px-4 py-2.5 text-sm font-medium text-white shadow-theme-xs hover:bg-brand-600"
            >
              Listo
            </button>
          </div>
        </Card>
      </div>
    </ModuleBase>
  );
};
