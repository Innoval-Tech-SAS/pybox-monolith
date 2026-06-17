import { useState, useEffect } from "react";
import { useApiClient } from "@/hooks/use-api-client";
import type { FieldInfo } from "@/reports/types/report.types";
import { AUDIT_FIELDS } from "@/reports/constants/report.constants";

export const useReportFields = (tableName: string) => {
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
