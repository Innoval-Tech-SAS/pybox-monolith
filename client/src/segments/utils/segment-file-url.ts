import { API_URL } from "@/hooks/use-api-client";

export const resolveSegmentFileUrl = (filePath: string): string => {
  const base = API_URL.replace(/\/+$/, "");
  const path = filePath.replace(/^\/+/, "");
  return `${base}/files/${path}`;
};
