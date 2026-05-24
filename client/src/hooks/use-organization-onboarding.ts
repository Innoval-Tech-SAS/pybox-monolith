import { useState } from "react";
import { useApiClient } from "./use-api-client";
import type { OrgOnboardingData } from "@/types/onboarding/onboarding-types";

export const useOrganizationOnboarding = () => {
  const { apiClient } = useApiClient();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const clearError = () => setError(null);

  const saveOrganization = async (data: OrgOnboardingData) => {
    setLoading(true);
    try {
      const form = new FormData();
      form.append(
        "data",
        JSON.stringify({
          name: data.name,
          country: data.country,
          fiscalDocumentNumber: data.fiscalDocumentNumber,
        }),
      );
      form.append("fiscal_document_file", data.fiscalDocumentFile);
      form.append("mercantile_document_file", data.mercantileDocumentFile);

      await apiClient("/onboarding/organization", {
        method: "POST",
        body: form,
      });
    } catch (e) {
      setError(e instanceof Error ? e.message : "Error al guardar organización");
    } finally {
      setLoading(false);
    }
  };

  return { saveOrganization, loading, error, clearError };
};
