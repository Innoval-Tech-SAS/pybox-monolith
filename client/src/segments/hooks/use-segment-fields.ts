import { useState, useEffect } from "react";
import { useApiClient } from "@/hooks/use-api-client";
import type { FieldInfo } from "@/segments/types/segment.types";
import { AUDIT_FIELDS } from "@/segments/constants/segment.constants";

export const useSegmentFields = (tableName: string) => {
  const { apiClient } = useApiClient();
  const [fields, setFields] = useState<FieldInfo[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!tableName) { setFields([]); return; }
    setLoading(true);
    apiClient(`/databases/schemas/public/tables/${tableName}/fields`)
      .then((data: FieldInfo[]) =>
        setFields((data ?? []).filter((f) => !AUDIT_FIELDS.includes(f.name)))
      )
      .catch(() => {})
      .finally(() => setLoading(false));
  }, [tableName]);

  return { fields, loading };
};
