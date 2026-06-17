import { API_URL } from "@/hooks/use-api-client";

export const resolveReportFileUrl = (filePath: string): string => {
  const base = API_URL.replace(/\/+$/, "");
  const path = filePath.replace(/^\/+/, "");
  return `${base}/files/${path}`;
};
