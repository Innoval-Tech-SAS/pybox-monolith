import { useEffect, useState } from "react";
import { useApiClient } from "./use-api-client";
import type { SelectOptionGroup } from "@/types/props/select-props";

interface DocumentTypesResponse {
  labels: Record<string, string>;
  groups: SelectOptionGroup[];
}

/**
 * Tipos de documento desde el backend (DB), reemplaza el antiguo dict estático.
 * - `labels`: mapa código → etiqueta legible (p. ej. { CC: "Cédula de Ciudadanía" }).
 * - `groups`: documentos de persona agrupados por país, listos para un <Select groups>.
 */
export const useDocumentTypes = () => {
  const { apiClient } = useApiClient();
  const [labels, setLabels] = useState<Record<string, string>>({});
  const [groups, setGroups] = useState<SelectOptionGroup[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    apiClient<DocumentTypesResponse>("/countries/document-types", { method: "GET" })
      .then((data) => {
        setLabels(data.labels ?? {});
        setGroups(data.groups ?? []);
      })
      .catch(() => {
        setLabels({});
        setGroups([]);
      })
      .finally(() => setLoading(false));
  }, [apiClient]);

  return { labels, groups, loading };
};
