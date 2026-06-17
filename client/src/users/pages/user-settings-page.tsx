import React, { useState } from "react";
import { useNavigate, useParams, useSearchParams } from "react-router";
import { ShieldCheck, FolderOpen } from "lucide-react";
import { ModuleBase } from "@/ui/components/common/module-base";
import { usePermissionsCatalog } from "../hooks/use-permissions-catalog";
import { useUserPermissions } from "../hooks/use-user-permissions";
import { useUserPortfolioAccess } from "../hooks/use-user-portfolio-access";
import type { PermissionCatalogEntry } from "@/types/users/permission-types";

// ─── Checkbox item ────────────────────────────────────────────────────────────

const CheckItem: React.FC<{
  id: string;
  label: string;
  sublabel?: string;
  checked: boolean;
  busy: boolean;
  indent?: boolean;
  onChange: (checked: boolean) => void;
}> = ({ id, label, sublabel, checked, busy, indent, onChange }) => (
  <li className={`border-b border-gray-200 py-3 last:border-b-0 dark:border-gray-800 ${indent ? "pl-10 pr-4" : "px-4"}`}>
    <div className="flex items-center justify-between gap-3">
      <label htmlFor={id} className="flex flex-1 cursor-pointer select-none items-center gap-3">
        <div className="relative size-5 shrink-0">
          <input
            id={id}
            type="checkbox"
            checked={checked}
            disabled={busy}
            onChange={(e) => onChange(e.target.checked)}
            className="size-5 appearance-none cursor-pointer rounded-md border border-gray-300 checked:border-transparent checked:bg-brand-500 disabled:cursor-not-allowed disabled:opacity-50 dark:border-gray-700"
          />
          {checked && (
            <svg
              className="pointer-events-none absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2"
              width="14" height="14" viewBox="0 0 14 14" fill="none"
            >
              <path d="M11.6666 3.5L5.24992 9.91667L2.33325 7" stroke="white" strokeWidth="1.94" strokeLinecap="round" strokeLinejoin="round" />
            </svg>
          )}
        </div>
        <span>
          <span className="block text-sm text-gray-700 dark:text-gray-300">{label}</span>
          {sublabel && (
            <span className="block text-xs text-gray-400 dark:text-gray-500 mt-0.5">{sublabel}</span>
          )}
        </span>
      </label>
      {busy && (
        <span className="size-4 shrink-0 animate-spin rounded-full border-2 border-brand-500 border-t-transparent" />
      )}
    </div>
  </li>
);

// ─── Checklist card ──────────────────────────────────────────────────────────

const ChecklistCard: React.FC<{
  icon: React.ReactNode;
  title: string;
  children: React.ReactNode;
}> = ({ icon, title, children }) => (
  <div className="flex flex-col gap-3">
    <div className="flex items-center gap-2">
      {icon}
      <h3 className="text-sm font-semibold text-gray-700 dark:text-gray-300">{title}</h3>
    </div>
    <div className="rounded-lg border border-gray-200 bg-white dark:border-gray-800 dark:bg-white/3">
      <ul className="flex flex-col">{children}</ul>
    </div>
  </div>
);

// ─── Permissions section (org-level only) ────────────────────────────────────

const PermissionsList: React.FC<{
  orgId: string;
  userId: string;
  catalog: PermissionCatalogEntry[];
  catalogLoading: boolean;
}> = ({ orgId, userId, catalog, catalogLoading }) => {
  const { permissions, loading: permsLoading, assignPermission, removePermission } = useUserPermissions(orgId, userId);
  const [busy, setBusy] = useState<string | null>(null);
  const [localOverride, setLocalOverride] = useState<Set<string> | null>(null);

  const serverGranted = new Set(permissions.filter((p) => p.effect === "GRANT").map((p) => p.name));
  const effective = localOverride ?? serverGranted;

  const toggle = async (name: string, checked: boolean) => {
    setBusy(name);
    const base = localOverride ?? serverGranted;
    const next = new Set(base);
    checked ? next.add(name) : next.delete(name);
    setLocalOverride(next);
    const ok = checked ? await assignPermission(name, "GRANT") : await removePermission(name);
    if (!ok) setLocalOverride(base);
    setBusy(null);
  };

  if (catalogLoading || permsLoading)
    return <li className="px-4 py-3 text-sm text-gray-400">Cargando...</li>;
  if (catalog.length === 0)
    return <li className="px-4 py-3 text-sm text-gray-400">No hay permisos configurados.</li>;

  return (
    <>
      {catalog.map((perm) => (
        <CheckItem
          key={perm.name}
          id={`perm-${perm.name}`}
          label={perm.label ?? perm.name}
          sublabel={perm.description ?? undefined}
          checked={effective.has(perm.name)}
          busy={busy === perm.name}
          onChange={(checked) => toggle(perm.name, checked)}
        />
      ))}
    </>
  );
};

// ─── Portfolios section (with portfolio-level perms as sub-items) ─────────────

const PortfoliosList: React.FC<{
  orgId: string;
  userId: string;
  permsCatalog: PermissionCatalogEntry[];
  catalogLoading: boolean;
}> = ({ orgId, userId, permsCatalog, catalogLoading }) => {
  const { portfolios, loading: portfoliosLoading, grantAccess, revokeAccess } = useUserPortfolioAccess(orgId, userId);
  const { permissions, loading: permsLoading, assignPermission, removePermission } = useUserPermissions(orgId, userId);
  const [busyPortfolio, setBusyPortfolio] = useState<string | null>(null);
  const [busyPerm, setBusyPerm] = useState<string | null>(null);
  const [localOverride, setLocalOverride] = useState<Set<string> | null>(null);

  const serverGranted = new Set(permissions.filter((p) => p.effect === "GRANT").map((p) => p.name));
  const effective = localOverride ?? serverGranted;

  const togglePortfolio = async (portfolioId: string, checked: boolean) => {
    setBusyPortfolio(portfolioId);
    if (checked) await grantAccess(portfolioId);
    else await revokeAccess(portfolioId);
    setBusyPortfolio(null);
  };

  const togglePerm = async (name: string, checked: boolean) => {
    setBusyPerm(name);
    const base = localOverride ?? serverGranted;
    const next = new Set(base);
    checked ? next.add(name) : next.delete(name);
    setLocalOverride(next);
    const ok = checked ? await assignPermission(name, "GRANT") : await removePermission(name);
    if (!ok) setLocalOverride(base);
    setBusyPerm(null);
  };

  if (portfoliosLoading || permsLoading || catalogLoading)
    return <li className="px-4 py-3 text-sm text-gray-400">Cargando...</li>;
  if (portfolios.length === 0)
    return <li className="px-4 py-3 text-sm text-gray-400">No hay portafolios disponibles en esta empresa.</li>;

  return (
    <>
      {portfolios.map((p) => (
        <React.Fragment key={p.portfolio_id}>
          <CheckItem
            id={`portfolio-${p.portfolio_id}`}
            label={p.name}
            checked={p.has_access}
            busy={busyPortfolio === p.portfolio_id}
            onChange={(checked) => togglePortfolio(p.portfolio_id, checked)}
          />
          {p.has_access && permsCatalog.map((perm) => (
            <CheckItem
              key={`${p.portfolio_id}-${perm.name}`}
              id={`perm-${perm.name}-${p.portfolio_id}`}
              label={perm.label ?? perm.name}
              checked={effective.has(perm.name)}
              busy={busyPerm === perm.name}
              indent
              onChange={(checked) => togglePerm(perm.name, checked)}
            />
          ))}
        </React.Fragment>
      ))}
    </>
  );
};

// ─── Page ────────────────────────────────────────────────────────────────────

export const UserSettingsPage: React.FC = () => {
  const navigate = useNavigate();
  const { id } = useParams<{ id: string }>();
  const [searchParams] = useSearchParams();
  const orgId = searchParams.get("org") ?? "";
  const userId = Number(id);

  const backPath = orgId ? `/my-companies/users?org=${orgId}` : "/my-users";

  const { catalog, loading: catalogLoading } = usePermissionsCatalog();
  const orgCatalog = catalog.filter((p) => !p.name.startsWith("portfolio."));
  const portfolioCatalog = catalog.filter((p) => p.name.startsWith("portfolio."));

  return (
    <ModuleBase
      pageTitle="Configuración del usuario"
      breadcrumbItems={[{ label: "Usuarios", path: backPath }]}
    >
      <div className="space-y-6">
        <div>
          <h2 className="text-xl font-bold text-gray-800 dark:text-white/90">Permisos y portafolios</h2>
          <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
            Activa o desactiva el acceso a módulos y portafolios para este usuario.
          </p>
        </div>

        <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
          <ChecklistCard icon={<ShieldCheck size={15} className="text-gray-500" />} title="Módulos">
            {orgId ? (
              <PermissionsList orgId={orgId} userId={userId} catalog={orgCatalog} catalogLoading={catalogLoading} />
            ) : (
              <li className="px-4 py-3 text-sm text-gray-400">Se requiere contexto de empresa.</li>
            )}
          </ChecklistCard>

          <ChecklistCard icon={<FolderOpen size={15} className="text-gray-500" />} title="Portafolios">
            {orgId ? (
              <PortfoliosList orgId={orgId} userId={userId} permsCatalog={portfolioCatalog} catalogLoading={catalogLoading} />
            ) : (
              <li className="px-4 py-3 text-sm text-gray-400">Se requiere contexto de empresa.</li>
            )}
          </ChecklistCard>
        </div>

        <div className="flex justify-end pt-2">
          <button
            type="button"
            onClick={() => navigate(backPath)}
            className="inline-flex items-center justify-center rounded-lg bg-brand-500 px-6 py-3 text-sm font-medium text-white shadow-theme-xs transition hover:bg-brand-600"
          >
            Listo
          </button>
        </div>
      </div>
    </ModuleBase>
  );
};
