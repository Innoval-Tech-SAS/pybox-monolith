import { useSendRequest } from "./use-send-request";

export const API_URL = import.meta.env.VITE_API_URL;

export const useApiClient = () => {
  
    const { sendRequest } = useSendRequest();

  const apiClient = (endpoint: string, options: RequestInit) => {
    
    if(!endpoint.startsWith("/")) throw new Error("endpoint must be start with '/'")

    return await sendRequest(
        `${API_URL}${endpoint}`
        options
    )
  };
};
