import { useCallback, useState } from "react";
import { useApiClient } from "@/hooks/use-api-client";
import { useAsyncResource } from "@/hooks/use-async-resource";
import type { OrganizationDetail } from "@/types/companies/company-types";

export interface OrgInfoUpdate {
  name?: string;
  sector?: string;
  description?: string;
  country?: string;
  fiscalDocumentType?: string;
  fiscalDocumentNumber?: string;
  mercantileDocumentType?: string;
}

export const useOrgSettings = (orgId: string) => {
  const { apiClient } = useApiClient();
  const [saving, setSaving] = useState(false);

  const fetchOrg = useCallback(() => {
    if (!orgId) return Promise.resolve(null);
    return apiClient(`/organizations/${orgId}`) as Promise<OrganizationDetail | null>;
  }, [orgId, apiClient]);

  const { data: org, loading, error, refetch, setData: setOrg } = useAsyncResource<OrganizationDetail | null>(
    fetchOrg,
    null,
    [orgId],
  );

  const updateInfo = async (data: OrgInfoUpdate) => {
    setSaving(true);
    try {
      const updated = await apiClient(`/organizations/${orgId}`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data),
      });
      setOrg(updated as OrganizationDetail);
    } finally {
      setSaving(false);
    }
  };

  const uploadDocument = async (docType: "fiscal" | "mercantil" | "representante" | "logo", file: File) => {
    setSaving(true);
    try {
      const form = new FormData();
      form.append("file", file);
      const updated = await apiClient(`/organizations/${orgId}/documents/${docType}`, {
        method: "PATCH",
        body: form,
      });
      setOrg(updated as OrganizationDetail);
    } finally {
      setSaving(false);
    }
  };

  const requestVerification = async () => {
    setSaving(true);
    try {
      const updated = await apiClient(`/organizations/${orgId}/request-verification`, {
        method: "POST",
      });
      setOrg(updated as OrganizationDetail);
    } finally {
      setSaving(false);
    }
  };

  return { org, loading, error, saving, updateInfo, uploadDocument, requestVerification, refetch };
};
