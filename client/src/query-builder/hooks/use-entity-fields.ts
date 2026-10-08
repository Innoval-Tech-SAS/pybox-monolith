import { useApiClient } from "@/hooks/use-api-client";
import { useAsyncResource } from "@/hooks/use-async-resource";
import type { FieldInfo } from "@/query-builder/types/query-builder-types";
import { AUDIT_FIELDS } from "@/query-builder/constants/query-builder-constants";

export const useEntityFields = (tableName: string) => {
  const { apiClient } = useApiClient();
  const { data: fields, loading } = useAsyncResource<FieldInfo[]>(
    () =>
      tableName
        ? apiClient(`/databases/schemas/public/tables/${tableName}/fields`).then((data: FieldInfo[]) =>
            (data ?? []).filter((f) => !AUDIT_FIELDS.includes(f.name)),
          )
        : Promise.resolve([]),
    [],
    [tableName],
  );

  return { fields, loading };
};
