import { useCallback, useEffect, useState } from "react";
import { useApiClient } from "@/hooks/use-api-client";
import { ApiError } from "@/types/api-error";
import { getSession } from "@/auth/utils/auth-session-utils";
import type { JudicialInbox } from "@/credits/types/judicial-types";

const EMPTY_INBOX: JudicialInbox = { items: [], unreadCount: 0 };

/** Buzón judicial del titular autenticado, con el contador que pinta el badge. */
export const useJudicialInbox = () => {
  const { apiClient } = useApiClient();
  const [inbox, setInbox] = useState<JudicialInbox>(EMPTY_INBOX);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchInbox = useCallback(async () => {
    setLoading(true);
    setError(null);

    // Igual que useMyCredits/useMyStatements: sin identidad verificada el backend
    // rechaza con 403, así que ni se pide — el buzón queda vacío en silencio (es un
    // widget del dashboard, no tiene su propio estado "pendiente de verificación").
    if (getSession()?.identityVerificationStatus !== "APROBADO") {
      setInbox(EMPTY_INBOX);
      setLoading(false);
      return;
    }

    try {
      const data = await apiClient<JudicialInbox>(
        "/judicial-notifications/mine",
        {},
        { silentStatuses: [403, 404] },
      );
      setInbox(data ?? EMPTY_INBOX);
    } catch (err) {
      // 403/404 = sin identidad verificada o sin deudor asociado: estado vacío normal
      // (no todos los usuarios SELF tienen obligaciones), no un error.
      const isExpected = err instanceof ApiError && (err.status === 403 || err.status === 404);
      if (!isExpected) {
        setError(err instanceof Error ? err.message : "Error al cargar el buzón judicial");
      }
      setInbox(EMPTY_INBOX);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchInbox();
  }, [fetchInbox]);

  const markRead = useCallback(
    async (notificationId: string) => {
      // Optimista: el badge baja de inmediato y se reconcilia con el refetch.
      setInbox((prev) => ({
        items: prev.items.map((n) => (n.id === notificationId ? { ...n, isRead: true } : n)),
        unreadCount: Math.max(0, prev.unreadCount - 1),
      }));
      try {
        await apiClient(`/judicial-notifications/${notificationId}/read`, { method: "POST" });
      } finally {
        await fetchInbox();
      }
    },
    [fetchInbox],
  );

  const markAllRead = useCallback(async () => {
    setInbox((prev) => ({
      items: prev.items.map((n) => ({ ...n, isRead: true })),
      unreadCount: 0,
    }));
    try {
      await apiClient("/judicial-notifications/read-all", { method: "POST" });
    } finally {
      await fetchInbox();
    }
  }, [fetchInbox]);

  return { inbox, loading, error, refetch: fetchInbox, markRead, markAllRead };
};
