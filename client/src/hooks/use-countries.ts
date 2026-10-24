import { useState, useEffect } from "react";
import { useApiClient } from "./use-api-client";
import type { NationalityOption } from "@/types/countries/country-types";

export const useCountries = () => {
  const { apiClient } = useApiClient();
  const [countries, setCountries] = useState<NationalityOption[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    apiClient<NationalityOption[]>("/countries", { method: "GET" })
      .then((data) => setCountries(data))
      .catch(() => setCountries([]))
      .finally(() => setLoading(false));
  }, [apiClient]);

  return { countries, loading };
};
