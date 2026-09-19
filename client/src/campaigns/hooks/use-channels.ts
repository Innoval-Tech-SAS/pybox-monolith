import { useApiClient } from "@/hooks/use-api-client";
import { useAsyncResource } from "@/hooks/use-async-resource";
import type { Channel } from "@/types/channels/channel-types";

export const useChannels = () => {
  const { apiClient } = useApiClient();
  const { data: channels, loading } = useAsyncResource<Channel[]>(
    () => apiClient("/channels/", { method: "GET" }).then((data: Channel[]) => data ?? []),
    [],
    [],
  );

  return { channels, loading };
};
