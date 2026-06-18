import { useEffect, useState } from "react";
import { useApiClient } from "@/hooks/use-api-client";
import type { TemplateVariableOption } from "@/templates/types/template-variable-option";

export const useTemplateVariables = (organizationId: string) => {
  const { apiClient } = useApiClient();
  const [variables, setVariables] = useState<TemplateVariableOption[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!organizationId) {
      setLoading(false);
      return;
    }
    setLoading(true);
    apiClient(`/templates/variables?organizationId=${organizationId}`, { method: "GET" })
      .then((data: TemplateVariableOption[]) => setVariables(data ?? []))
      .catch(() => {})
      .finally(() => setLoading(false));
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [organizationId]);

  return { variables, loading };
};
