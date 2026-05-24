import { useEffect, useState } from "react";
import { useApiClient } from "./use-api-client";

interface ToursPreferences {
  dismissedTours: string[];
}

export const useDismissedTours = () => {
  const { apiClient } = useApiClient();
  const [dismissedTours, setDismissedTours] = useState<string[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    apiClient("/users/me/preferences/tours")
      .then((data: ToursPreferences) => setDismissedTours(data.dismissedTours ?? []))
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  const isDismissed = (key: string) => dismissedTours.includes(key);

  const dismiss = (key: string) => {
    apiClient(`/users/me/preferences/tours/${key}/dismiss`, { method: "POST" })
      .then((data: ToursPreferences) => setDismissedTours(data.dismissedTours ?? []))
      .catch(() => {});
  };

  return { isDismissed, dismiss, loading };
};
