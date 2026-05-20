export const useSendRequest = () => {
  const sendRequest = async (url: string, options: RequestInit) => {
    try {
      const response = await fetch(url, options);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      return await response.json();
    } catch (error) {
      console.error("Error sending request:", error);
      throw error;
    }
  };
  return { sendRequest };
};
