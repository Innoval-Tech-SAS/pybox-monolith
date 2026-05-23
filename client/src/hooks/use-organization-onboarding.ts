import { useState } from "react";
import { API_URL } from "./use-api-client";
import type { OrgOnboardingData } from "@/types/onboarding/onboarding-types";
import { getAuthHeaders } from "@/utils/auth-headers";

export const useOrganizationOnboarding = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const saveOrganization = async (data: OrgOnboardingData) => {
    setLoading(true);
    setError(null);
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

      const response = await fetch(`${API_URL}/onboarding/organization`, {
        method: "POST",
        headers: { ...getAuthHeaders() },
        body: form,
      });

      if (!response.ok) {
        const body = await response.json().catch(() => ({}));
        throw new Error(body?.detail ?? `Error ${response.status}`);
      }
    } catch (err) {
      const message = err instanceof Error ? err.message : "Error al guardar la organización";
      setError(message);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  return { saveOrganization, loading, error, clearError: () => setError(null) };
};
