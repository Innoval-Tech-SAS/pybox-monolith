import { useState } from "react";
import { useApiClient } from "./use-api-client";
import type { OrgOnboardingData } from "@/types/onboarding/onboarding-types";

export const useOrganizationOnboarding = () => {
  const { apiClient } = useApiClient();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const clearError = () => setError(null);

  const saveOrganization = async (data: OrgOnboardingData): Promise<boolean> => {
    setLoading(true);
    try {
      const form = new FormData();
      const payload: Record<string, unknown> = {
        name: data.name,
        country: data.country,
        fiscal_document_number: data.fiscalDocumentNumber,
        representative_mode: data.representativeMode,
      };
      if (data.representativeMode === "create") {
        payload.rep_firstname = data.repFirstname;
        payload.rep_lastname = data.repLastname;
        payload.rep_email = data.repEmail;
        payload.rep_document_type = data.repDocType;
        payload.rep_document_number = data.repDocNumber;
      }
      form.append("data", JSON.stringify(payload));
      form.append("fiscal_document_file", data.fiscalDocumentFile);
      form.append("mercantile_document_file", data.mercantileDocumentFile);
      form.append("representative_document_file", data.representativeDocumentFile);

      await apiClient("/onboarding/organization", {
        method: "POST",
        body: form,
      });
      return true;
    } catch (e) {
      setError(e instanceof Error ? e.message : "Error al guardar organización");
      return false;
    } finally {
      setLoading(false);
    }
  };

  return { saveOrganization, loading, error, clearError };
};
