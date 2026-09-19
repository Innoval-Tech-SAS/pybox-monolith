import { useEffect, useState } from "react";
import { useApiClient } from "@/hooks/use-api-client";

export interface ContactPolicy {
  id: string;
  name: string;
  country?: string;
  timezone?: string;
}

/**
 * Políticas de contacto disponibles en Helena (horario permitido de marcación).
 *
 * Las administra Helena; aquí solo se listan para elegir cuál aplica al flujo.
 * Si Helena no responde, se devuelve lista vacía: el selector queda con la
 * opción "Sin política" y el flujo sigue siendo guardable.
 */
export const useContactPolicies = () => {
  const { apiClient } = useApiClient();
  const [policies, setPolicies] = useState<ContactPolicy[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let active = true;
    apiClient("/ivr/contact-policies/", { method: "GET" })
      .then((data: ContactPolicy[] | { data?: ContactPolicy[] }) => {
        if (!active) return;
        // Helena puede devolver la lista cruda o envuelta en `data`.
        const list = Array.isArray(data) ? data : (data?.data ?? []);
        setPolicies(list.filter((p) => p && p.id));
      })
      .catch(() => active && setPolicies([]))
      .finally(() => active && setLoading(false));
    return () => {
      active = false;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return { policies, loading };
};
