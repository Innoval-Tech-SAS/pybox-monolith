import { useApiClient } from "@/hooks/use-api-client";
import { useAsyncResource } from "@/hooks/use-async-resource";

export const useSchemaTables = (schema: string) => {
  const { apiClient } = useApiClient();
  const { data: tables, loading } = useAsyncResource<string[]>(
    () =>
      schema
        ? apiClient<string[]>(`/databases/schemas/${schema}/tables`).then((data) => data ?? [])
        : Promise.resolve([]),
    [],
    [schema],
  );

  return { tables, loading };
};
