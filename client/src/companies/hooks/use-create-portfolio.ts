import { useCallback, useRef, useState } from "react";
import { useSearchParams, useNavigate } from "react-router";
import { useToast } from "@/context/toast-context";
import { useApiClient } from "@/hooks/use-api-client";
import type { CreatePortfolioResult } from "@/types/companies/company-types";

export const useCreatePortfolio = () => {
  const { error: toastError } = useToast();
  const navigate = useNavigate();
  const { apiClient } = useApiClient();
  const [searchParams] = useSearchParams();
  const orgId = searchParams.get("org") ?? "";

  const [portfolioName, setPortfolioName] = useState("");
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [selectedCountry, setSelectedCountry] = useState("");

  const formRef = useRef<HTMLFormElement>(null);

  const handleReset = useCallback(() => {
    setPortfolioName("");
    setSelectedFile(null);
    setSelectedCountry("");
    formRef.current?.reset();
  }, []);

  const handleSubmit = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    if (!orgId) { toastError("Error", "No se pudo identificar la organización."); return; }
    if (!selectedFile) { toastError("Validación", "Debes adjuntar el archivo CSV."); return; }

    const data = new FormData();
    data.set("file", selectedFile);

    const params = new URLSearchParams({ portfolioName, tenantId: orgId });
    if (selectedCountry) params.set("countryId", selectedCountry);

    // Navigate immediately — user can keep working
    navigate(`/my-companies/portfolios?org=${orgId}`);

    // Fire-and-forget: backend creates a bell notification when done via SSE
    apiClient(`/portfolios/upload-csv?${params}`, { method: "POST", body: data })
      .catch(() => {
        // apiClient already shows an error toast on failure
      });
  };

  return {
    isSubmitting: false,
    orgId,
    portfolioName, setPortfolioName,
    selectedFile, setSelectedFile,
    selectedCountry, setSelectedCountry,
    formRef,
    handleReset,
    handleSubmit,
  };
};
