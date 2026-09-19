import { useApiClient } from "@/hooks/use-api-client";
import { useAsyncResource } from "@/hooks/use-async-resource";
import type { TemplateVariableOption } from "@/templates/types/template-variable-option";

export const useTemplateVariables = (organizationId: string) => {
  const { apiClient } = useApiClient();
  const { data: variables, loading } = useAsyncResource<TemplateVariableOption[]>(
    () =>
      organizationId
        ? apiClient(`/templates/variables?organizationId=${organizationId}`, { method: "GET" }).then(
            (data: TemplateVariableOption[]) => data ?? [],
          )
        : Promise.resolve([]),
    [],
    [organizationId],
  );

  return { variables, loading };
};
