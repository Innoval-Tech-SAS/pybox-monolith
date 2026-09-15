import { useState, useEffect } from "react";
import { useApiClient } from "@/hooks/use-api-client";
import type { EntitySectorOption } from "@/types/companies/company-types";

/**
 * Catálogo de sectores de entidad desde el backend, que es la fuente de verdad del
 * enum `EntitySectors`. El front no declara la lista ni sus etiquetas.
 */
export const useEntitySectors = () => {
  const { apiClient } = useApiClient();
  const [sectors, setSectors] = useState<EntitySectorOption[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    apiClient("/organizations/sectors", { method: "GET" })
      .then((data: EntitySectorOption[]) => setSectors(data))
      .catch(() => setSectors([]))
      .finally(() => setLoading(false));
  }, []);

  return { sectors, loading };
};
