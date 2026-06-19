import { useEffect, useState } from "react";
import { useApiClient } from "@/hooks/use-api-client";
import type { Template } from "@/types/templates/template-types";

export const useTemplateOptions = (organizationId: string) => {
  const { apiClient } = useApiClient();
  const [templates, setTemplates] = useState<Template[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!organizationId) { setLoading(false); return; }
    setLoading(true);
    apiClient(`/templates/options?organizationId=${organizationId}`, { method: "GET" })
      .then((data: Template[]) => setTemplates(data ?? []))
      .catch(() => setTemplates([]))
      .finally(() => setLoading(false));
  }, [organizationId, apiClient]);

  return { templates, loading };
};
