import { useCallback, useEffect, useState } from "react";

/**
 * Estandariza el patrón {data, loading, error, refetch} para hooks que llaman
 * apiClient, en vez de que cada hook reimplemente su propio try/catch (algunos
 * silenciaban errores con .catch(() => {}) sin exponerlos a la UI).
 */
export function useAsyncResource<T>(
  fetcher: () => Promise<T>,
  initialValue: T,
  deps: React.DependencyList = [],
) {
  const [data, setData] = useState<T>(initialValue);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const refetch = useCallback(() => {
    let cancelled = false;
    setLoading(true);
    setError(null);

    fetcher()
      .then((result) => {
        if (!cancelled) setData(result);
      })
      .catch((err: unknown) => {
        if (!cancelled) {
          setError(err instanceof Error ? err.message : "Ocurrió un error inesperado");
        }
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });

    return () => {
      cancelled = true;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, deps);

  useEffect(() => refetch(), [refetch]);

  return { data, loading, error, refetch, setData };
}
