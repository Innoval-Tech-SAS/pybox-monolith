import { useEffect, useState } from "react";
import { useApiClient } from "./use-api-client";
import { TOUR_KEYS } from "@/constants/tour-keys";

interface ToursPreferences {
  dismissedTours: string[];
}

type ApiClient = ReturnType<typeof useApiClient>["apiClient"];

// Varios tours pueden montarse en la misma pantalla (p. ej. la lista de
// portafolios). Coalescemos las peticiones simultáneas para no pedir las
// mismas preferencias una vez por hook.
let inFlight: Promise<string[]> | null = null;

const fetchDismissedTours = (apiClient: ApiClient): Promise<string[]> => {
  inFlight ??= apiClient("/users/me/preferences/tours")
    .then((data: ToursPreferences) => data.dismissedTours ?? [])
    .catch(() => [] as string[])
    .finally(() => {
      inFlight = null;
    });
  return inFlight;
};

export const useDismissedTours = () => {
  const { apiClient } = useApiClient();
  const [dismissedTours, setDismissedTours] = useState<string[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let active = true;
    fetchDismissedTours(apiClient)
      .then((tours) => {
        if (active) setDismissedTours(tours);
      })
      .finally(() => {
        if (active) setLoading(false);
      });
    return () => {
      active = false;
    };
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  const isDismissed = (key: string) => dismissedTours.includes(key);

  const dismiss = (key: string) => {
    apiClient(`/users/me/preferences/tours/${key}/dismiss`, { method: "POST" })
      .then((data: ToursPreferences) => setDismissedTours(data.dismissedTours ?? []))
      .catch(() => {});
  };

  // useTour también silencia el tour por sesión vía sessionStorage: hay que
  // limpiar esa marca o el tour restaurado no reaparecería hasta la próxima sesión.
  const restore = (key: string) => {
    apiClient(`/users/me/preferences/tours/${key}/restore`, { method: "POST" })
      .then((data: ToursPreferences) => {
        sessionStorage.removeItem(key);
        setDismissedTours(data.dismissedTours ?? []);
      })
      .catch(() => {});
  };

  const restoreAll = () => {
    apiClient("/users/me/preferences/tours/restore", { method: "POST" })
      .then((data: ToursPreferences) => {
        TOUR_KEYS.forEach((key) => sessionStorage.removeItem(key));
        setDismissedTours(data.dismissedTours ?? []);
      })
      .catch(() => {});
  };

  return { isDismissed, dismiss, restore, restoreAll, loading };
};
