export const getAuthHeaders = (): Record<string, string> => {
  const token = sessionStorage.getItem("accessToken");
  return token ? { Authorization: `Bearer ${token}` } : {};
};
