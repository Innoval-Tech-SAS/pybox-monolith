import { useCallback } from "react";

export const useSendRequest = () => {
  const sendRequest = useCallback(
    (url: string, options: RequestInit): Promise<Response> => fetch(url, options),
    [],
  );

  return { sendRequest };
};
