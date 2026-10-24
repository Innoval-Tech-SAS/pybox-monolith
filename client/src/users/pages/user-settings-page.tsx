import React, { useState } from "react";
import { useNavigate, useParams, useSearchParams } from "react-router";
import { ShieldCheck, FolderOpen, ShieldOff } from "lucide-react";
import { Loader } from "@/ui/components/loader/loader";
import EmptyState from "@/ui/components/common/empty-state";
import { ModuleBase } from "@/ui/components/common/module-base";
import { Button } from "@/ui/components/button/button";
import { usePermissionsCatalog } from "../hooks/use-permissions-catalog";
import { useUserPermissions } from "../hooks/use-user-permissions";
import { useUserPortfolioAccess } from "../hooks/use-user-portfolio-access";
import { CheckItem } from "../components/check-item";
import { ChecklistCard } from "../components/checklist-card";
import type { PermissionCatalogEntry } from "@/types/users/permission-types";

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

  if (catalogLoading || permsLoading)
    return <li className="px-4 py-4"><Loader size="sm" loaderText="Cargando permisos..." /></li>;
  if (catalog.length === 0)
    return <li className="px-4 py-5"><EmptyState icon={ShieldOff} title="No hay permisos configurados" /></li>;

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

  const serverGranted = new Set(permissions.filter((p) => p.effect === "OTORGAR").map((p) => p.name));
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
    if (checked) {
      next.add(name);
    } else {
      next.delete(name);
    }
    setLocalOverride(next);
    const ok = checked ? await assignPermission(name, "OTORGAR") : await removePermission(name);
    if (!ok) setLocalOverride(base);
    setBusyPerm(null);
  };

  if (portfoliosLoading || permsLoading || catalogLoading)
    return <li className="px-4 py-4"><Loader size="sm" loaderText="Cargando portafolios..." /></li>;
  if (portfolios.length === 0)
    return <li className="px-4 py-5"><EmptyState icon={FolderOpen} title="Sin portafolios en esta empresa" /></li>;

  return (
    <>
      {portfolios.map((p) => (
        <React.Fragment key={p.portfolioId}>
          <CheckItem
            id={`portfolio-${p.portfolioId}`}
            label={p.name}
            checked={p.hasAccess}
            busy={busyPortfolio === p.portfolioId}
            onChange={(checked) => togglePortfolio(p.portfolioId, checked)}
          />
          {p.hasAccess && permsCatalog.map((perm) => (
            <CheckItem
              key={`${p.portfolioId}-${perm.name}`}
              id={`perm-${perm.name}-${p.portfolioId}`}
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
  const userId = id ?? "";

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
          <Button type="button" onClick={() => navigate(backPath)}>
            Listo
          </Button>
        </div>
      </div>
    </ModuleBase>
  );
};
