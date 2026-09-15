import { API_URL } from "@/hooks/use-api-client";

export const resolveProfilePhotoUrl = (value?: string | null): string | null => {
  if (!value) {
    return null;
  }
  if (/^https?:\/\//i.test(value) || value.startsWith("data:") || value.startsWith("blob:")) {
    return value;
  }
  if (!value.startsWith("/")) {
    return value;
  }

  try {
    const base = API_URL.replace(/\/+$/, "");
    return `${base}${value}`;
  } catch {
    return value;
  }
};
