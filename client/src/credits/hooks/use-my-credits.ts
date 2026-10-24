import { useCallback, useEffect, useState } from "react";
import { useApiClient } from "@/hooks/use-api-client";
import { ApiError } from "@/types/api-error";
import { getSession } from "@/auth/utils/auth-session-utils";
import type { CreditWithPayments } from "@/credits/types/credit-types";

export const useMyCredits = () => {
  const { apiClient } = useApiClient();
  const [credits, setCredits] = useState<CreditWithPayments[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  // Conocer tipo+número de documento de alguien no es secreto: además de ser deudor
  // conocido, el backend exige identidad verificada (ver MyCreditsService). Se revisa
  // en la sesión primero para no pedir el endpoint cuando ya se sabe que va a rechazar.
  const [identityPending, setIdentityPending] = useState(false);

  const loadCredits = useCallback(async () => {
    setLoading(true);
    setError(null);
    setIdentityPending(false);

    if (getSession()?.identityVerificationStatus !== "APROBADO") {
      setIdentityPending(true);
      setLoading(false);
      return;
    }

    try {
      const data = await apiClient<CreditWithPayments[]>(
        "/credits/my-credits",
        {},
        { silentStatuses: [403, 404] },
      );
      setCredits(data);
    } catch (err) {
      if (err instanceof ApiError && err.status === 403) {
        setIdentityPending(true);
      } else if (err instanceof ApiError && err.status === 404) {
        // 404 = todavía no hay un deudor asociado a este documento: estado vacío
        // normal (no todos los usuarios SELF tienen obligaciones), no un error.
        setCredits([]);
      } else {
        setError(err instanceof Error ? err.message : "Error al cargar los créditos");
      }
    } finally {
      setLoading(false);
    }
  }, [apiClient]);

  useEffect(() => { loadCredits(); }, [loadCredits]);

  return { credits, loading, error, identityPending, refetch: loadCredits };
};
