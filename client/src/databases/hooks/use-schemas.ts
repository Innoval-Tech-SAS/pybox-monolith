import { useApiClient } from "@/hooks/use-api-client";
import { useAsyncResource } from "@/hooks/use-async-resource";

export const useSchemas = () => {
  const { apiClient } = useApiClient();
  const { data: schemas, loading } = useAsyncResource<string[]>(
    () => apiClient<string[]>("/databases/schemas").then((data) => data ?? []),
    [],
    [],
  );

  return { schemas, loading };
};
