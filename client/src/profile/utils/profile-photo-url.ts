import { API_URL } from "@/hooks/use-api-client";

export const resolveProfilePhotoUrl = (value?: string | null): string | null => {
  console.log("[profile-photo] resolve input", { value, apiUrl: API_URL });
  if (!value) {
    console.log("[profile-photo] resolve output", { resolved: null, reason: "empty" });
    return null;
  }
  if (/^https?:\/\//i.test(value) || value.startsWith("data:") || value.startsWith("blob:")) {
    console.log("[profile-photo] resolve output", { resolved: value, reason: "absolute" });
    return value;
  }
  if (!value.startsWith("/files/")) {
    console.log("[profile-photo] resolve output", { resolved: value, reason: "non-files-path" });
    return value;
  }

  try {
    const base = API_URL.replace(/\/+$/, "");
    const resolved = `${base}${value}`;
    console.log("[profile-photo] resolve output", { resolved, reason: "api-origin" });
    return resolved;
  } catch {
    console.log("[profile-photo] resolve output", { resolved: value, reason: "relative-api-url" });
    return value;
  }
};
