import { useEffect } from "react";
import { useNavigate } from "react-router";
import { useOrgModule } from "./use-org-module";

/**
 * Páginas de módulo de empresa dependen de `?org=<id>` en la URL (lo agrega
 * `buildOrgPath` en toda navegación interna). Un enlace directo o favorito sin
 * ese query param no debe renderizar el módulo con datos en blanco (los hooks
 * de cada página cortocircuitan el fetch si `orgId` está vacío) — se redirige
 * al listado de empresas para que el usuario elija una.
 */
export const useRequireOrg = () => {
  const { orgId, orgs, loading } = useOrgModule();
  const navigate = useNavigate();

  useEffect(() => {
    if (loading) return;
    const belongsToOrg = orgId && orgs.some((o) => o.id === orgId);
    if (!belongsToOrg) {
      navigate("/my-companies", { replace: true });
    }
  }, [loading, orgId, orgs, navigate]);
};
