import { useMemo } from "react";
import { useApiClient } from "@/hooks/use-api-client";
import { useAsyncResource } from "@/hooks/use-async-resource";
import { useSession } from "@/auth/hooks/use-session";
import { resolveFileUrl } from "@/companies/utils/resolve-doc-file-url";
import type { OrganizationDetail } from "@/types/companies/company-types";

interface PlatformBrandingResource {
  logoUrl: string | null;
}

type LogoSource = OrganizationDetail | PlatformBrandingResource | null;

/**
 * Logo a mostrar en el sidebar/navbar: el de la primera organización del usuario, o
 * el logo global de la plataforma si no pertenece a ninguna (admin/soporte global).
 * `AsideMenu`/`NavbarMenu` se montan en `admin-layout.tsx` fuera de
 * `OrgModuleContext` (que depende de `?org=` en la URL), así que esto se resuelve
 * directo desde `useSession()`, ya cacheado -- sin fetch extra para saber quién es
 * el usuario.
 */
export const useSidebarLogo = (): { logoUrl: string | null; loading: boolean } => {
  const { apiClient } = useApiClient();
  const { user, loading: sessionLoading } = useSession();

  const orgId = useMemo(() => Object.keys(user?.orgs ?? {})[0] ?? null, [user]);

  const fetchLogo = useMemo<() => Promise<LogoSource>>(() => {
    if (sessionLoading) return () => Promise.resolve(null);
    if (orgId) return () => apiClient(`/organizations/${orgId}`);
    return () => apiClient("/platform/branding");
  }, [sessionLoading, orgId, apiClient]);

  const { data, loading } = useAsyncResource<LogoSource>(fetchLogo, null, [orgId, sessionLoading]);

  return { logoUrl: resolveFileUrl(data?.logoUrl), loading: sessionLoading || loading };
};
