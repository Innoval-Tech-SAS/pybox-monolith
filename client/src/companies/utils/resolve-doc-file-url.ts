import { API_URL } from "@/hooks/use-api-client";

export const resolveFileUrl = (path: string | null | undefined): string | null => {
  if (!path) return null;
  if (/^https?:\/\//i.test(path)) return path;
  if (path.startsWith("/")) {
    try { return `${API_URL.replace(/\/+$/, "")}${path}`; } catch { return path; }
  }
  return path;
};
