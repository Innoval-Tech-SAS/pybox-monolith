import { useState, useEffect } from "react";
import { useApiClient } from "./use-api-client";

export interface NationalityOption {
  code: string;
  name: string;
  flagUrl: string;
  phonePrefix: string;
  documentTypes: string[];
}

export const useNationalities = () => {
  const { apiClient } = useApiClient();
  const [nationalities, setNationalities] = useState<NationalityOption[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    apiClient("/countries", { method: "GET" })
      .then((data: NationalityOption[]) => setNationalities(data))
      .catch(() => setNationalities([]))
      .finally(() => setLoading(false));
  }, []);

  return { nationalities, loading };
};
