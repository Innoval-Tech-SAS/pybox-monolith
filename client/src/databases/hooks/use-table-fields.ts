import { useApiClient } from "@/hooks/use-api-client";
import { useAsyncResource } from "@/hooks/use-async-resource";
import type { FieldInfo } from "@/databases/types/database-types";

export const useTableFields = (schema: string, table: string) => {
  const { apiClient } = useApiClient();
  const { data: fields, loading } = useAsyncResource<FieldInfo[]>(
    () =>
      schema && table
        ? apiClient<FieldInfo[]>(`/databases/schemas/${schema}/tables/${table}/fields`).then((data) => data ?? [])
        : Promise.resolve([]),
    [],
    [schema, table],
  );

  return { fields, loading };
};
