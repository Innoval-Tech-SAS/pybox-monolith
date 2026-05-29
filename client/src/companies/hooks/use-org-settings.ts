import { useCallback, useEffect, useState } from "react";
import { useApiClient } from "@/hooks/use-api-client";
import type { OrganizationDetail } from "@/types/companies/company-types";

export interface OrgInfoUpdate {
  name?: string;
  description?: string;
  country?: string;
  fiscalDocumentType?: string;
  fiscalDocumentNumber?: string;
  mercantileDocumentType?: string;
}

export const useOrgSettings = (orgId: string) => {
  const { apiClient } = useApiClient();
  const [org, setOrg] = useState<OrganizationDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);

  const load = useCallback(() => {
    if (!orgId) return;
    setLoading(true);
    apiClient(`/organizations/${orgId}`)
      .then((data) => setOrg(data as OrganizationDetail))
      .catch(() => {})
      .finally(() => setLoading(false));
  }, [orgId]);

  useEffect(() => { load(); }, [load]);

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

  const uploadDocument = async (docType: "fiscal" | "mercantil" | "representante", file: File) => {
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

  return { org, loading, saving, updateInfo, uploadDocument, requestVerification };
};
