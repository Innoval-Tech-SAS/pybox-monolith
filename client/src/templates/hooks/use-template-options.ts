import { useEffect, useState } from "react";
import { useApiClient } from "@/hooks/use-api-client";
import type { Template } from "@/types/templates/template-types";

export const useTemplateOptions = (portfolioId: string) => {
  const { apiClient } = useApiClient();
  const [templates, setTemplates] = useState<Template[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!portfolioId) { setLoading(false); return; }
    setLoading(true);
    apiClient(`/templates/options?portfolioId=${portfolioId}`, { method: "GET" })
      .then((data: Template[]) => setTemplates(data ?? []))
      .catch(() => setTemplates([]))
      .finally(() => setLoading(false));
  }, [portfolioId, apiClient]);

  return { templates, loading };
};
