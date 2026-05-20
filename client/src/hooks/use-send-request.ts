export const useSendRequest = () => {
  const sendRequest = async (url: string, options: RequestInit) => {
    const response = await fetch(url, options);
    if (!response.ok) {
      const body = await response.json().catch(() => ({}));
      throw new Error(body?.error ?? `Error ${response.status}`);
    }
    return await response.json();
  };
  return { sendRequest };
};
