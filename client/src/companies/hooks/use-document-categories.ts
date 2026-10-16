import { useEffect, useMemo, useState } from "react";
import { useApiClient } from "@/hooks/use-api-client";
import type { DocumentCategoryOption } from "@/types/companies/portfolio-debtor-types";

/**
 * Categorías de documento desde el backend, que es la fuente de verdad del enum
 * `DocumentCategory`. `labels` es el mapa código → etiqueta para renderizar una
 * categoría suelta (p. ej. en un Badge).
 */
export const useDocumentCategories = () => {
  const { apiClient } = useApiClient();
  const [categories, setCategories] = useState<DocumentCategoryOption[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    apiClient<DocumentCategoryOption[]>("/documents/categories", { method: "GET" })
      .then((data) => setCategories(data ?? []))
      .catch(() => setCategories([]))
      .finally(() => setLoading(false));
  }, [apiClient]);

  const labels = useMemo(
    () => Object.fromEntries(categories.map((c) => [c.value, c.label])) as Record<string, string>,
    [categories],
  );

  return { categories, labels, loading };
};
