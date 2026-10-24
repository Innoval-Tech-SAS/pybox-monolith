import { useState, useEffect } from "react";
import { useApiClient } from "./use-api-client";
import type { NationalityOption } from "@/types/countries/country-types";

export const useNationalities = () => {
  const { apiClient } = useApiClient();
  const [nationalities, setNationalities] = useState<NationalityOption[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    apiClient<NationalityOption[]>("/countries", { method: "GET" })
      .then((data) => setNationalities(data))
      .catch(() => setNationalities([]))
      .finally(() => setLoading(false));
  }, [apiClient]);

  return { nationalities, loading };
};
