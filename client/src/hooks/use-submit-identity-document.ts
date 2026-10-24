import { useState } from "react";
import { useApiClient } from "./use-api-client";
import type { IdentityVerificationStatus } from "@/types/onboarding/onboarding-types";

interface IdentityDocumentSubmittedResponse {
  identityVerificationStatus: IdentityVerificationStatus;
}

export const useSubmitIdentityDocument = () => {
  const { apiClient } = useApiClient();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const clearError = () => setError(null);

  const submit = async (file: File): Promise<boolean> => {
    setLoading(true);
    try {
      const form = new FormData();
      form.append("file", file);
      await apiClient<IdentityDocumentSubmittedResponse>("/onboarding/identity-document", {
        method: "PATCH",
        body: form,
      });
      return true;
    } catch (e) {
      setError(e instanceof Error ? e.message : "Error al subir el documento");
      return false;
    } finally {
      setLoading(false);
    }
  };

  return { submit, loading, error, clearError };
};
