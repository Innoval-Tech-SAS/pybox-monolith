import { useEffect, useState } from "react";
import { useApiClient } from "@/hooks/use-api-client";
import type { Channel } from "@/types/channels/channel-types";

export const useChannels = () => {
  const { apiClient } = useApiClient();
  const [channels, setChannels] = useState<Channel[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    apiClient("/channels/", { method: "GET" })
      .then((data: Channel[]) => setChannels(data ?? []))
      .catch(() => {})
      .finally(() => setLoading(false));
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return { channels, loading };
};
