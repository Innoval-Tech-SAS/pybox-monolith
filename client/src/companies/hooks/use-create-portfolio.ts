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
  const [showSuccessModal, setShowSuccessModal] = useState(false);

  const formRef = useRef<HTMLFormElement>(null);

  const handleReset = useCallback(() => {
    setPortfolioName("");
    setSelectedFile(null);
    setSelectedCountry("");
    formRef.current?.reset();
  }, []);

  const handleSubmit = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    console.log("[portfolio] submit disparado");

    if (!orgId) {
      console.log("[portfolio] ERROR: orgId vacío — falta ?org= en la URL");
      toastError("Error", "No se pudo identificar la organización.");
      return;
    }
    if (!selectedFile) {
      console.log("[portfolio] ERROR: no hay archivo seleccionado");
      toastError("Validación", "Debes adjuntar el archivo CSV.");
      return;
    }

    console.log("[portfolio] orgId:", orgId, "| archivo:", selectedFile.name, "| nombre:", portfolioName);

    const data = new FormData();
    data.set("file", selectedFile);

    const params = new URLSearchParams({ portfolioName, tenantId: orgId });
    if (selectedCountry) params.set("countryId", selectedCountry);

    console.log("[portfolio] disparando request a /portfolios/upload-csv?" + params.toString());

    // Fire-and-forget: backend acepta y procesa en background, notifica por SSE al terminar
    apiClient(`/portfolios/upload-csv?${params}`, { method: "POST", body: data })
      .then(() => console.log("[portfolio] backend aceptó la petición"))
      .catch((err) => console.error("[portfolio] error en la petición:", err));

    console.log("[portfolio] mostrando modal de confirmación");
    setShowSuccessModal(true);
  };

  const handleSuccessModalClose = useCallback(() => {
    setShowSuccessModal(false);
    navigate(`/my-companies/portfolios?org=${orgId}`);
  }, [navigate, orgId]);

  return {
    showSuccessModal,
    handleSuccessModalClose,
    orgId,
    portfolioName, setPortfolioName,
    selectedFile, setSelectedFile,
    selectedCountry, setSelectedCountry,
    formRef,
    handleReset,
    handleSubmit,
  };
};
