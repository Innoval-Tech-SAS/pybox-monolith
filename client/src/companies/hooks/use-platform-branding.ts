import { useState } from "react";
import { useApiClient } from "@/hooks/use-api-client";
import { useAsyncResource } from "@/hooks/use-async-resource";

interface PlatformBranding {
  logoUrl: string | null;
}

/** Espejo de useOrgSettings, sin orgId: el logo global lo sube un admin global vía
 * PATCH /platform/branding/logo y lo lee cualquier sesión autenticada vía
 * GET /platform/branding. */
export const usePlatformBranding = () => {
  const { apiClient } = useApiClient();
  const [saving, setSaving] = useState(false);

  const fetchBranding = () => apiClient("/platform/branding") as Promise<PlatformBranding | null>;

  const { data: branding, loading, error, refetch, setData } = useAsyncResource<PlatformBranding | null>(
    fetchBranding,
    null,
    [],
  );

  const uploadLogo = async (file: File) => {
    setSaving(true);
    try {
      const form = new FormData();
      form.append("file", file);
      const updated = await apiClient("/platform/branding/logo", {
        method: "PATCH",
        body: form,
      });
      setData(updated as PlatformBranding);
    } finally {
      setSaving(false);
    }
  };

  return { branding, loading, saving, error, uploadLogo, refetch };
};
