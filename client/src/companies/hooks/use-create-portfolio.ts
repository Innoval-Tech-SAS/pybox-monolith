import { useCallback, useRef, useState } from "react";
import { useSearchParams, useNavigate } from "react-router";
import { useToast } from "@/context/toast-context";
import { useApiClient } from "@/hooks/use-api-client";
import type { CreatePortfolioResult } from "@/types/companies/company-types";

export const useCreatePortfolio = () => {
  const { success, error: toastError } = useToast();
  const navigate = useNavigate();
  const { apiClient } = useApiClient();
  const [searchParams] = useSearchParams();
  const orgId = searchParams.get("org") ?? "";

  const [isSubmitting, setIsSubmitting] = useState(false);
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

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    if (!orgId) { toastError("Error", "No se pudo identificar la organización."); return; }
    if (!selectedFile) { toastError("Validación", "Debes adjuntar el archivo CSV."); return; }

    setIsSubmitting(true);
    try {
      const data = new FormData();
      data.set("file", selectedFile);

      const params = new URLSearchParams({ portfolioName, tenantId: orgId });
      if (selectedCountry) params.set("countryId", selectedCountry);

      const result: CreatePortfolioResult = await apiClient(`/portfolios/upload-csv?${params}`, {
        method: "POST",
        body: data,
      });
      if (result) {
        success(
          "Portafolio creado",
          `${result.processed_rows} registros procesados${result.failed_rows > 0 ? `, ${result.failed_rows} fallidos` : ""}.`,
        );
        navigate(`/my-companies?org=${orgId}`);
      }
    } catch {
      // handled by apiClient
    } finally {
      setIsSubmitting(false);
    }
  };

  return {
    isSubmitting,
    orgId,
    portfolioName, setPortfolioName,
    selectedFile, setSelectedFile,
    selectedCountry, setSelectedCountry,
    formRef,
    handleReset,
    handleSubmit,
  };
};
